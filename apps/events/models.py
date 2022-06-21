import logging
import typing

from django.db import models, transaction
from django.db.models import Q, QuerySet
from django.utils import timezone

from apps.bots.models import Bot
from apps.fileuploads.models import HasPoster
from apps.generic.models import TimeStamped
from apps.locations.models import Location, Sublocation
from apps.management.models import OrganizerBound
from apps.qrcodes.models import QrCode, QrCodeBound
from apps.staff.models import StaffCategory, StaffMember
from lib.telegram.datatypes import ParseMode
from lib.telegram.textutils import escape_markdown
from lib.utils import as_timezone, format_datetime

if typing.TYPE_CHECKING:
    from apps.tickets.models import TicketCategory


logger = logging.getLogger(__name__)


class Event(TimeStamped, OrganizerBound, HasPoster):
    YOOMONEY = "yoomoney"
    YOOMONEY_TELEGRAM = "yoomoney_telegram"
    FONDY = "fondy"
    PAYMENT_TYPE_CHOICES = (
        (YOOMONEY, "YooMoney"),
        (YOOMONEY_TELEGRAM, "YooMoney (Telegram)"),
        (FONDY, "Fondy"),
    )

    name = models.CharField(max_length=1000)
    time_start = models.DateTimeField()
    time_end = models.DateTimeField()
    bot = models.ForeignKey(
        Bot, on_delete=models.SET_NULL, blank=True, null=True, related_name="events",
    )
    locations = models.ManyToManyField(Location, related_name="events", blank=True)
    staff_categories = models.ManyToManyField(
        StaffCategory, related_name="events", blank=True
    )
    selfie_rejected_text = models.TextField(
        default="Извините. Будем ждать Вас в другой день."
    )
    payment_type = models.CharField(
        max_length=100, choices=PAYMENT_TYPE_CHOICES, blank=True, default=""
    )

    def is_available(self):
        return self in Event.objects.filter(time_end__gt=timezone.now())

    @classmethod
    def get_active(cls):
        pass

    @property
    def bot_data(self):
        return self.bot

    @property
    def locations_data(self):
        return self.locations

    @property
    def staff_categories_data(self):
        return self.staff_categories

    @property
    def report_data(self):
        staff_count = self.staffpass_set.count()

        from apps.tickets.models import Ticket

        all_tickets = Ticket.objects.filter(
            category__in=self.ticketcategory_set.all(),
            status__in=(Ticket.PAYED, Ticket.USED),
        )
        returned_tickets = Ticket.objects.filter(
            category__in=self.ticketcategory_set.all(), status=Ticket.RETURNED,
        )
        prices = set()
        for ticket in all_tickets:
            prices.add(ticket.purchase_price)
        visitor_count_total = all_tickets.count()
        visitor_count_free = all_tickets.filter(purchase_price=0).count()
        visitor_count_payed = visitor_count_total - visitor_count_free
        visitor_count_passed = all_tickets.filter(status=Ticket.USED).count()
        not_passed_paid_tickets = all_tickets.filter(status=Ticket.PAYED).filter(
            ~Q(purchase_price=0)
        )
        visitor_count_not_passed_payed = not_passed_paid_tickets.count()
        visitor_count_not_passed_free = all_tickets.filter(
            status=Ticket.PAYED, purchase_price=0
        ).count()
        visitor_count_returned = returned_tickets.count()
        promoted_tickets = all_tickets.exclude(guest_invite__isnull=True)
        visitor_count_promoted = promoted_tickets.count()

        revenue_total = sum([t.purchase_price for t in all_tickets])
        revenue_promoters = sum([t.purchase_price for t in promoted_tickets])
        revenue_organizer = revenue_total - revenue_promoters
        revenue_returned = sum([t.purchase_price for t in returned_tickets])
        revenue_to_return_unused = sum(
            [t.purchase_price for t in not_passed_paid_tickets]
        )

        return {
            "visitor_count": {
                "total": visitor_count_total,
                "free": visitor_count_free,
                "payed": visitor_count_payed,
                "promoted": visitor_count_promoted,
                "passed": visitor_count_passed,
                "not_passed_payed": visitor_count_not_passed_payed,
                "not_passed_free": visitor_count_not_passed_free,
                "returned": visitor_count_returned,
            },
            "staff_count": staff_count,
            "revenue": {
                "total": revenue_total,
                "promoters": revenue_promoters,
                "organizer": revenue_organizer,
                "to_return_unused": revenue_to_return_unused,
                "returned": revenue_returned,
            },
        }

    def get_brief_info(self):
        start_str = escape_markdown(format_datetime(as_timezone(self.time_start)))
        end_str = escape_markdown(format_datetime(as_timezone(self.time_end)))
        return (
            f"*{escape_markdown(self.name)}*\n"
            f"Начало: {start_str}\n"
            f"Окончание: {end_str}"
        )

    def get_active_ticket_categories(
        self, include_hidden=False
    ) -> QuerySet["TicketCategory"]:
        if include_hidden:
            return self.ticketcategory_set.filter(is_active=True)
        else:
            return self.ticketcategory_set.filter(is_active=True, is_hidden=False)

    def send_staff_passes(self, force_resending=False):
        new_staff_passes = []

        for staff_category in self.staff_categories.all():
            for staff_member in staff_category.staff_members.all():
                staff_pass = StaffPass.get_or_create(
                    event=self, staff_member=staff_member
                )
                try:
                    new_staff_passes.append(staff_pass)
                    staff_pass.send_grant(force_resending)
                except Exception as e:
                    logger.exception(e)

        old_staff_passes = self.staffpass_set.all()
        for old_staff_pass in old_staff_passes:
            if old_staff_pass not in new_staff_passes:
                try:
                    old_staff_pass.send_revoke()
                    old_staff_pass.delete()
                except Exception as e:
                    logger.exception(e)

    def make_refund_for_unused_tickets(self):
        from apps.tickets.models import Ticket

        unused_tickets = Ticket.objects.filter(
            category__in=self.ticketcategory_set.all(), status=Ticket.PAYED
        )
        for unused_ticket in unused_tickets:
            try:
                unused_ticket.set_returned()
            except Exception:
                logger.exception("Unable to make automatic refund.", exc_info=True)


class EventBound(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)

    @property
    def event_data(self):
        return self.event

    class Meta:
        abstract = True


class StaffPass(TimeStamped, QrCodeBound, EventBound):
    staff_member = models.ForeignKey(StaffMember, on_delete=models.CASCADE)
    was_sent = models.BooleanField(default=False)

    def get_grant_text(self):
        return (
            f"Вам выдан пропуск на мероприятие *{escape_markdown(self.event.name)}*\n"
            "Категория персонала: "
            f"*{escape_markdown(self.staff_member.staff_category.name)}*"
        )

    def get_revoke_text(self):
        return (
            f"Ваш пропуск на мероприятие *{escape_markdown(self.event.name)}* "
            "с категорией персонала "
            f"*{escape_markdown(self.staff_member.staff_category.name)}* отозван\\."
        )

    def send_grant(self, force_resending=False):
        if not force_resending:
            if self.was_sent:
                return

        qr_image = self.qr_code.get_image(self.event.bot.username)
        self.event.bot.client.send_image(
            self.staff_member.participant.telegram_id,
            qr_image,
            caption=self.get_grant_text(),
            parse_mode=ParseMode.MARKDOWN_V2,
        )
        self.was_sent = True
        self.save(update_fields=["was_sent"])

    def send_revoke(self):
        self.event.bot.client.send_message(
            self.staff_member.participant.telegram_id,
            self.get_revoke_text(),
            parse_mode=ParseMode.MARKDOWN_V2,
        )

    def get_allowed_locations(self) -> QuerySet[Location]:
        return self.staff_member.staff_category.available_locations.all()

    def get_allowed_sublocations(self) -> QuerySet[Sublocation]:
        return self.staff_member.staff_category.available_sublocations.all()

    @classmethod
    def get_or_create(cls, event, staff_member) -> "StaffPass":
        try:
            return StaffPass.objects.get(event=event, staff_member=staff_member)
        except StaffPass.DoesNotExist:
            pass

        with transaction.atomic():
            qr_code = QrCode(type=QrCode.STAFF)
            qr_code.save()

            return cls.objects.create(
                qr_code=qr_code, event=event, staff_member=staff_member
            )
