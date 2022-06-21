import logging
from typing import Optional

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone
from sorl.thumbnail import get_thumbnail

import lib.kassa as yoomoney_lib
from apps.bots.consts import CONFIRM_PURCHASE_CHAT_CONTEXT_KEY
from apps.bots.models import Bot
from apps.events.models import Event, EventBound
from apps.features.models import Feature
from apps.generic.models import TimeStamped
from apps.locations.models import Location, LocationBound
from apps.management.models import OrganizerBound
from apps.participants.models import Participant
from apps.qrcodes.models import QrCode, QrCodeBound
from apps.tickets.renderers import render_ticket_info
from lib.fondy import get_fondy_checkout_url, make_fondy_refund
from lib.kassa import check_yoomoney_payment, get_yoomoney_checkout_data
from lib.payment import get_integer_big_payment_amount
from lib.telegram.datatypes import ParseMode
from lib.telegram.textutils import escape_markdown

logger = logging.getLogger(__name__)


class TicketPlace(models.Model):
    number = models.IntegerField()


class TicketCategory(TimeStamped, EventBound, LocationBound):
    name = models.CharField(max_length=500)
    base_price = models.PositiveIntegerField()
    max_ticket_count = models.PositiveIntegerField()
    available_features = models.ManyToManyField(
        Feature, through="FeatureLimit", blank=True
    )
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, default="")
    with_manual_confirmation = models.BooleanField(default=False)
    selfie_required = models.BooleanField(default=False)
    avoid_selfie_reconfirmation = models.BooleanField(default=False)
    per_participant_limit = models.PositiveIntegerField(default=1)
    is_hidden = models.BooleanField(default=False)
    selfie_confirmed_text = models.TextField(blank=True, default="")
    additional_data_request = models.TextField(blank=True, default="")
    additional_data_short_request = models.BooleanField(default=False)
    lifetime_end = models.DateTimeField(blank=True, null=True)

    def is_expired(self) -> bool:
        return bool(self.lifetime_end and self.lifetime_end <= timezone.now())

    @property
    def available_features_data(self):
        return self.available_features

    def is_free(self):
        return self.base_price == 0

    def with_auto_confirmation(self):
        return (not self.is_free()) and (not self.with_manual_confirmation)

    def get_base_price_label(self):
        if self.is_free():
            return "бесплатно"
        else:
            return f"{self.base_price} руб."

    @property
    def available_ticket_count(self):
        return self.max_ticket_count - self.get_purchased_ticket_count()

    def get_purchased_ticket_count(self):
        return self.tickets.filter(status__in=(Ticket.PAYED, Ticket.USED)).count()

    def get_invoice_payload(self):
        return f"ticket_category:{self.id}"

    def get_invoice_price(self):
        return get_integer_big_payment_amount(self.base_price)

    def get_invoice_currency(self):
        return "RUB"

    @classmethod
    def get_from_invoice_payload(
        cls, invoice_payload: str
    ) -> Optional["TicketCategory"]:
        prefix, _, instance_id = invoice_payload.partition(":")

        try:
            return cls.objects.get(pk=instance_id)
        except cls.DoesNotExist:
            pass

    def render_description(self, minimal=False, markdown=True):
        lines = []

        _escape = escape_markdown if markdown else (lambda v: v)

        # lines.append((f"Доступно билетов: " f"{_escape(self.available_ticket_count)}"))  # noqa

        if not minimal and self.description:
            lines.append(_escape(self.description))

        return "\n".join(lines)

    def send_telegram_yoomoney_invoice(self, from_id, minimal: bool = False):
        telegram_yandex_checkout_token = (
            self.event.organizer.organizer_telegram_checkout_token
        )

        if not telegram_yandex_checkout_token:
            return self.event.bot.client.send_message(
                from_id, "Не настроено подключение к системе оплаты."
            )

        self.event.bot.client.call_api(
            "sendInvoice",
            {
                "chat_id": from_id,
                "title": self.name,
                "description": self.render_description(minimal=minimal, markdown=False)
                or "Покупка билета",
                "payload": self.get_invoice_payload(),
                "provider_token": telegram_yandex_checkout_token,
                "start_parameter": "custom_start_parameter",
                "currency": self.get_invoice_currency(),
                "prices": [{"label": "Стоимость", "amount": self.get_invoice_price()}],
            },
        )

    @classmethod
    def get_purchase_price(cls, total_amount):
        return total_amount / 100

    def after_selfie_confirmation(self, ticket):
        inline_keyboard = None
        if self.with_manual_confirmation:
            inline_keyboard = [
                [
                    {
                        "text": "Отправить скрин подтверждения",
                        "callback_data": (f"just_request_confirmation|{ticket.id}"),
                    }
                ],
            ]
        self.event.bot.client.send_message(
            ticket.participant.telegram_id,
            (self.selfie_confirmed_text or "Селфи подтверждено."),
            inline_keyboard=inline_keyboard,
        )
        if self.with_auto_confirmation():
            ticket.send_checkout_details()
        elif self.is_free():
            ticket.send_to_participant()


class FeatureLimit(models.Model):
    """
    Fields:

    - max_value:
        -1 - unlimited
        0 - unavailable (equal to absence of record)
        1 - one item
        2 - two items
        ...
    """

    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    max_value = models.IntegerField()


class GuestInvite(TimeStamped, OrganizerBound, QrCodeBound):
    ticket_category = models.ForeignKey(TicketCategory, on_delete=models.CASCADE)

    @property
    def ticket_category_data(self):
        return self.ticket_category

    @property
    def qr_code_computed_data(self):
        return {
            "start_url": self.qr_code.get_start_url(
                self.ticket_category.event.bot.username
            ),
            "base64_image": self.qr_code.get_base64_image(
                self.ticket_category.event.bot.username
            ),
        }

    @property
    def purchased_tickets(self):
        return self.ticket_set.filter(status__in=(Ticket.PAYED, Ticket.USED))

    @property
    def purchased_ticket_count(self):
        return self.purchased_tickets.count()

    @property
    def purchased_ticket_sum(self):
        return sum([t.purchase_price for t in self.purchased_tickets])

    def save(self, *args, **kwargs):
        if not self.qr_code_id:
            qr_code = QrCode(type=QrCode.GUEST_INVITE)
            qr_code.save()
            self.qr_code = qr_code
        super(GuestInvite, self).save(*args, **kwargs)


class TicketPromoCode(models.Model):
    category = models.ForeignKey(TicketCategory, on_delete=models.SET_NULL, null=True)
    code = models.CharField(max_length=500)
    is_disposable = models.BooleanField(default=False)
    new_price = models.IntegerField()


class Ticket(TimeStamped, QrCodeBound):
    CREATED = "created"
    PENDING = "pending"
    PAYED = "payed"
    USED = "used"
    RETURNED = "returned"
    STATUS_CHOICES = (
        (CREATED, "Создан"),
        (PENDING, "Ожидает оплаты"),
        (PAYED, "Действителен"),
        (USED, "Проход осуществлён"),
        (RETURNED, "Выполнен возврат"),
    )

    category = models.ForeignKey(
        TicketCategory, on_delete=models.SET_NULL, null=True, related_name="tickets"
    )
    purchase_price = models.FloatField()
    payment_id = models.CharField(max_length=1000, blank=True, default="")
    participant = models.ForeignKey(Participant, on_delete=models.SET_NULL, null=True)
    # TODO: remove
    consumed_features = models.ManyToManyField(Feature, through="FeatureConsumption")
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=CREATED)
    guest_invite = models.ForeignKey(
        GuestInvite, on_delete=models.SET_NULL, blank=True, null=True
    )
    access_control_comment = models.TextField(blank=True, default="")

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def category_data(self):
        return self.category

    @property
    def participant_data(self):
        return self.participant

    @property
    def guest_invite_data(self):
        return self.guest_invite

    def get_confirmed_selfie(self):
        selfie = (
            self.selfies.filter(status=TicketSelfie.CONFIRMED).order_by("-id").first()
        )
        if not selfie and self.category.avoid_selfie_reconfirmation:
            return self.participant.get_confirmed_selfie()
        return selfie

    def set_payed(self, payment_id=None):
        self.status = self.PAYED
        if payment_id:
            self.payment_id = payment_id
        self.save(update_fields=["status"] + (["payment_id"] if payment_id else []))

    def set_pending(self, payment_id):
        self.status = self.PENDING
        self.payment_id = payment_id
        self.save(update_fields=["status", "payment_id"])

    def set_used(self):
        self.status = self.USED
        self.save(update_fields=["status"])

    def set_returned(self):
        if self.category.with_manual_confirmation:
            purchase_confirmation = self.purchase_confirmations.last()
            purchase_confirmation.status = PurchaseConfirmation.REFUND_REQUESTED
            purchase_confirmation.save(update_fields=["status"])
            # TODO: notify on request
            success = True
        else:
            success = self.make_automatic_refund()

        if success:
            self.status = self.RETURNED
            self.save(update_fields=["status"])
            return True

    def get_organizer(self):
        try:
            return self.category.event.organizer
        except AttributeError:
            logger.error(
                f"No organizer found for this event: id={self.id}", exc_info=True
            )

    def make_automatic_refund(self):
        if not self.payment_id:
            return

        if self.category.is_free():
            return

        if not (organizer := self.get_organizer()):
            return

        try:
            payment_type = self.category.event.payment_type
        except AttributeError:
            logger.error("Unable to extract ticket payment type", exc_info=True)
            return

        if payment_type == Event.FONDY:
            return make_fondy_refund(
                self.payment_id,
                self.purchase_price,
                organizer.organizer_fondy_merchant_id,
                organizer.organizer_fondy_merchant_password,
            )
        elif payment_type == Event.YOOMONEY:
            try:
                return yoomoney_lib.make_api_refund(
                    self.payment_id,
                    self.purchase_price,
                    username=organizer.organizer_shop_id,
                    password=organizer.organizer_shop_secret,
                    idempotence_key=str(self.id),
                )
            except Exception as e:
                logger.exception(e)

    def is_payed(self):
        return self.status == self.PAYED

    def is_used(self):
        return self.status == self.USED

    def get_purchase_price_label(self):
        return f"{self.purchase_price} руб."

    def send_to_participant(self, payment_id=None, set_payed=True):
        if set_payed:
            self.set_payed(payment_id=payment_id)

        self.category.event.bot.client.send_message(
            self.participant.telegram_id,
            render_ticket_info(self),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        image = self.qr_code.get_image(self.category.event.bot.username)
        self.category.event.bot.client.send_image(self.participant.telegram_id, image)

    def request_payment_confirmation(self):
        chat_context = self.category.event.bot.get_chat_context(
            self.participant.telegram_id
        )
        self.category.event.bot.set_chat_context(
            self.participant.telegram_id,
            {
                **chat_context,
                CONFIRM_PURCHASE_CHAT_CONTEXT_KEY: self.id,
                "image_processing": "confirm_purchase",
            },
        )
        self.category.event.bot.client.send_message(
            self.participant.telegram_id,
            ("Загрузите в чат скриншот экрана с проведённой оплатой."),
        )

    def set_access_control_comment(self, comment_text: str):
        # Set comment

        self.access_control_comment = comment_text
        self.save(update_fields=("access_control_comment",))

        # Notify organizer

        try:
            event = self.category.event
        except AttributeError:
            return

        event.organizer.send_notification(
            (
                f'Охрана отозвала билет на мероприятие "{event.name}" '
                "и оставила комментарий:\n\n"
                f"{comment_text}"
            )
        )

    def get_fondy_payment_url(self):
        if not (organizer := self.get_organizer()):
            return

        return get_fondy_checkout_url(
            server_callback_url=(
                f"{settings.PUBLIC_ORIGIN}{reverse('payments:fondy_webhook')}"
            ),
            order_id=f"ticket:{self.id}",
            order_desc=(f"Билет на мероприятие {self.category.event.name}.")[:1024],
            amount=self.category.get_invoice_price(),
            merchant_id=organizer.organizer_fondy_merchant_id,
            merchant_password=organizer.organizer_fondy_merchant_password,
        )

    def get_yoomoney_payment_data(self):
        if not (organizer := self.get_organizer()):
            return

        return get_yoomoney_checkout_data(
            return_url=self.category.event.bot.get_url(),
            order_id=f"ticket:{self.id}",
            order_desc=(f"Билет на мероприятие {self.category.event.name}.")[:128],
            amount=self.category.base_price,
            username=organizer.organizer_shop_id,
            password=organizer.organizer_shop_secret,
        )

    def send_checkout_details(self):
        try:
            payment_type = self.category.event.payment_type
        except AttributeError:
            logger.error("Unable to get payment type.", exc_info=True)
            payment_type = None

        if payment_type == Event.YOOMONEY_TELEGRAM:
            self.category.send_telegram_yoomoney_invoice(
                self.participant.telegram_id, minimal=True,
            )
        elif payment_type == Event.FONDY:
            self.send_fondy_invoice()
        elif payment_type == Event.YOOMONEY:
            self.send_yoomoney_invoice()
        else:
            self.category.event.bot.client.send_message(
                self.participant.telegram_id, "Неизвестный тип оплаты."
            )

    def send_fondy_invoice(self):
        if not (payment_url := self.get_fondy_payment_url()):
            return self.category.event.bot.client.send_message(
                self.participant.telegram_id,
                "Не удалось сформировать счёт для оплаты.",
            )

        self.category.event.bot.client.send_message(
            self.participant.telegram_id, f"Оплата билета: {payment_url}",
        )

    def send_yoomoney_invoice(self):
        if not (payment_data := self.get_yoomoney_payment_data()):
            return self.category.event.bot.client.send_message(
                self.participant.telegram_id,
                "Не удалось сформировать счёт для оплаты.",
            )

        self.set_pending(payment_id=payment_data["payment_id"])

        self.category.event.bot.client.send_message(
            self.participant.telegram_id,
            f"Оплата билета: {payment_data['checkout_url']}",
        )

    def check_yoomoney_payment(self):
        if not (organizer := self.get_organizer()):
            return

        if not self.payment_id:
            return logger.error("No payment ID for checking.")

        is_confirmed = check_yoomoney_payment(
            self.payment_id,
            username=organizer.organizer_shop_id,
            password=organizer.organizer_shop_secret,
        )

        if is_confirmed is None:
            return

        if is_confirmed is True:
            return self.send_to_participant()

        if is_confirmed is False:
            self.delete()

    class Meta:
        ordering = ("-id",)


class UnifiedPass(TimeStamped, QrCodeBound, OrganizerBound):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    is_active = models.BooleanField(default=True)

    @property
    def location_data(self):
        return self.location

    @property
    def bot_data(self):
        return self.bot

    @property
    def qr_code_computed_data(self):
        return {
            "start_url": self.qr_code.get_start_url(self.bot.username),
            "base64_image": self.qr_code.get_base64_image(self.bot.username),
        }

    def save(self, *args, **kwargs):
        if not self.qr_code_id:
            qr_code = QrCode(type=QrCode.UNIFIED_PASS)
            qr_code.save()
            self.qr_code = qr_code
        super(UnifiedPass, self).save(*args, **kwargs)


class FeatureConsumption(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    feature = models.ForeignKey(Feature, on_delete=models.CASCADE)
    value = models.IntegerField()


class PurchaseConfirmation(TimeStamped):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    REFUND_REQUESTED = "refund_requested"
    REFUND_PERFORMED = "refund_performed"
    STATUS_CHOICES = (
        (PENDING, "Не обработано"),
        (CONFIRMED, "Оплата подтверждена"),
        (REJECTED, "Отклонено"),
        (REFUND_REQUESTED, "Запрошен возврат"),
        (REFUND_PERFORMED, "Выполнен возврат"),
    )

    image = models.FileField(upload_to="purchase-confirmations/%Y/%m/%d")
    ticket = models.ForeignKey(
        Ticket, related_name="purchase_confirmations", on_delete=models.CASCADE
    )
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)

    def __init__(self, *args, **kwargs):
        super(PurchaseConfirmation, self).__init__(*args, **kwargs)
        self._original_status = self.status

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.status != self._original_status:
            self.handle_status_change(self._original_status, self.status)

        is_creating = not self.id

        super(PurchaseConfirmation, self).save(
            force_insert, force_update, *args, **kwargs
        )
        self._original_status = self.status

        if is_creating:
            self.handle_create()

    def handle_status_change(self, old_status, new_status):
        if new_status == self.CONFIRMED:
            # TODO: prevent when there is enriched limit of tickets per ticket category
            self.ticket.category.event.bot.client.send_message(
                self.ticket.participant.telegram_id, "Оплата подтверждена.",
            )
            self.ticket.send_to_participant()
        elif new_status == self.REJECTED:
            chat_context = self.ticket.category.event.bot.get_chat_context(
                self.ticket.participant.telegram_id
            )
            self.ticket.category.event.bot.set_chat_context(
                self.ticket.participant.telegram_id,
                {
                    **chat_context,
                    CONFIRM_PURCHASE_CHAT_CONTEXT_KEY: self.ticket.id,
                    "image_processing": "confirm_purchase",
                },
            )
            self.ticket.category.event.bot.client.send_message(
                self.ticket.participant.telegram_id,
                "Оплата не принята, попробуйте ещё раз.",
            )

    def handle_create(self):
        try:
            event = self.ticket.category.event
        except AttributeError:
            return

        event.organizer.send_notification(
            (
                f"Добавлено новое подтверждение оплаты для мероприятия "
                f'"{event.name}":\n'
                f"{self.get_public_edit_url()}"
            )
        )

    @property
    def participant_label(self):
        return self.ticket.participant.label

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def event_data(self):
        return self.ticket.category.event

    @property
    def ticket_category_data(self):
        return self.ticket.category

    def get_public_edit_url(self):
        return (
            f"{settings.PUBLIC_ORIGIN}/management/purchase-confirmations/{self.id}/edit"
        )

    class Meta:
        ordering = ("-created_at",)


class TicketSelfie(TimeStamped):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    STATUS_CHOICES = (
        (PENDING, "Не обработано"),
        (CONFIRMED, "Одобрено"),
        (REJECTED, "Отклонено"),
    )

    image = models.FileField(upload_to="ticket-selfies/%Y/%m/%d")
    telegram_image_id = models.CharField(max_length=1000, blank=True, default="")
    ticket = models.ForeignKey(Ticket, related_name="selfies", on_delete=models.CASCADE)
    status = models.CharField(max_length=100, choices=STATUS_CHOICES, default=PENDING)
    admin_comment = models.TextField(blank=True, default="")

    def __init__(self, *args, **kwargs):
        super(TicketSelfie, self).__init__(*args, **kwargs)
        self._original_status = self.status

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.status != self._original_status:
            self.handle_status_change(self._original_status, self.status)

        is_creating = not self.id

        super(TicketSelfie, self).save(force_insert, force_update, *args, **kwargs)
        self._original_status = self.status

        if is_creating:
            self.handle_create()

    def handle_create(self):
        try:
            event = self.ticket.category.event
        except AttributeError:
            return

        event.organizer.send_notification(
            (
                f'Добавлено новое селфи для мероприятия "{event.name}":\n'
                f"{self.get_public_edit_url()}"
            )
        )

    def handle_status_change(self, old_status, new_status):
        if new_status == self.CONFIRMED:
            self.ticket.category.after_selfie_confirmation(self.ticket)
        elif new_status == self.REJECTED:
            self.ticket.category.event.bot.client.send_message(
                self.ticket.participant.telegram_id,
                self.ticket.category.event.selfie_rejected_text,
            )

    @property
    def ticket_category_data(self):
        return self.ticket.category

    @property
    def event_data(self):
        return self.ticket.category.event

    @property
    def participant_label(self):
        return self.ticket.participant.label

    @property
    def status_label(self):
        return self.get_status_display()

    @property
    def attachments(self):
        return self.selfieupload_set.all()

    @property
    def messages(self):
        return self.selfiemessage_set.all()

    def get_selfie_image(self):
        if self.image:
            return get_thumbnail(self.image.file, "800", scale=False)

    def get_public_edit_url(self):
        return f"{settings.PUBLIC_ORIGIN}/management/ticket-selfies/{self.id}/edit"

    class Meta:
        ordering = ("-created_at",)


class SelfieMessage(TimeStamped):
    selfie = models.ForeignKey(TicketSelfie, on_delete=models.CASCADE)
    text = models.TextField()


class SelfieUpload(TimeStamped):
    selfie = models.ForeignKey(TicketSelfie, on_delete=models.CASCADE)
    file = models.FileField(upload_to="selfie-uploads/%Y/%m/%d")
