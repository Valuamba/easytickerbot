import logging
from typing import Optional

from django.core.files import File
from django.db import transaction

from apps.bots.consts import (
    CONFIRM_PURCHASE_CHAT_CONTEXT_KEY,
    UPLOAD_SELFIE_CHAT_CONTEXT_KEY,
)
from apps.bots.models import Bot
from apps.bots.scenarios.qr_handling.guest_invite import handle_guest_invite_qr
from apps.bots.scenarios.qr_handling.not_found import handle_not_found_qr
from apps.bots.scenarios.qr_handling.staff import handle_staff_qr
from apps.bots.scenarios.qr_handling.staff_invite import handle_staff_invite_qr
from apps.bots.scenarios.qr_handling.ticket import handle_ticket_qr
from apps.bots.scenarios.qr_handling.unified_pass import handle_unified_pass_qr
from apps.bots.scenarios.qr_handling.unknown import handle_unknown_qr
from apps.bots.scenarios.staff.invitation import staff_invite_choose_category_handler
from apps.bots.scenarios.tickets.buying import (
    _check_event_availability,
    _check_participant_is_blocked,
    _check_participant_ticket_limit,
    _check_ticket_category_availability,
    _display_event,
    _display_ticket_category,
)
from apps.events.models import Event
from apps.participants.models import Participant
from apps.qrcodes.models import QrCode
from apps.tickets.models import (
    GuestInvite,
    PurchaseConfirmation,
    SelfieMessage,
    SelfieUpload,
    Ticket,
    TicketCategory,
    TicketSelfie,
)
from lib.icons import ACCEPT_ICON, DECLINE_ICON, ENVELOPE_ICON, REFUND_ICON
from lib.telegram import IncomingData
from lib.telegram.datatypes import IncomingDataType

logger = logging.getLogger(__name__)

QR_HANDLER_MAP = {
    QrCode.TICKET: handle_ticket_qr,
    QrCode.STAFF: handle_staff_qr,
    QrCode.STAFF_INVITE: handle_staff_invite_qr,
    QrCode.GUEST_INVITE: handle_guest_invite_qr,
    QrCode.UNIFIED_PASS: handle_unified_pass_qr,
}


def process_start_qr_code(
    bot: Bot, incoming_data: IncomingData, chat_context, token: str
):
    try:
        qr_code = QrCode.objects.get(token=token)
        handle_qr = QR_HANDLER_MAP.get(qr_code.type, handle_unknown_qr)
        handle_qr(bot, incoming_data, chat_context, qr_code)
    except QrCode.DoesNotExist:
        handle_not_found_qr(bot, incoming_data, chat_context)


def fallback_handler(bot: Bot, incoming_data: IncomingData, chat_context):
    if incoming_data.message_text == "Мои билеты":
        return display_my_tickets_handler(bot, incoming_data, chat_context)

    display_nearest_events_handler(bot, incoming_data, chat_context)


def display_my_tickets_handler(bot: Bot, incoming_data: IncomingData, chat_context):
    from_data = incoming_data.original_data.get("from")

    participant = Participant.get_or_create(
        telegram_id=incoming_data.from_id,
        first_name=(from_data or {}).get("first_name", ""),
        last_name=(from_data or {}).get("last_name", ""),
        username=(from_data or {}).get("username", ""),
    )

    tickets = participant.get_active_tickets()

    if not tickets.exists():
        return bot.client.send_message(
            incoming_data.from_id, "У вас нет активных билетов."
        )

    bot.client.send_message(incoming_data.from_id, "Ваши активные билеты:")

    for ticket in tickets:
        ticket.send_to_participant(set_payed=False)


def display_nearest_events_handler(bot: Bot, incoming_data: IncomingData, chat_context):
    nearest_events = bot.get_nearest_events()

    banner_reply_markup = {
        "keyboard": [[{"text": "Мероприятия"}, {"text": "Мои билеты"}]],
        "resize_keyboard": True,
    }

    if not nearest_events:
        return bot.client.send_message(
            incoming_data.from_id,
            "На данный момент нет ни одного доступного мероприятия.",
            reply_markup=banner_reply_markup,
        )

    bot.client.send_message(
        incoming_data.from_id,
        "Ближайшие мероприятия:",
        reply_markup=banner_reply_markup,
    )

    for event in nearest_events:
        _display_event(bot, incoming_data, event)


def buy_tickets_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, handler_value: str
):
    try:
        event = Event.objects.get(pk=handler_value)
    except Event.DoesNotExist:
        return logger.warning(
            "No event with such ID for ticket buying: %s", handler_value
        )

    if not _check_event_availability(bot, incoming_data, event):
        return

    active_ticket_categories = event.get_active_ticket_categories()

    if not active_ticket_categories:
        return bot.client.send_message(
            incoming_data.from_id, f"Нет билетов в продаже для {event.name}.",
        )

    bot.client.send_message(incoming_data.from_id, "Доступные категории билетов:")

    for ticket_category in active_ticket_categories:
        _display_ticket_category(bot, incoming_data, ticket_category)


def _create_ticket(
    bot: Bot,
    incoming_data: IncomingData,
    chat_context: dict,
    participant: Participant,
    ticket_category: TicketCategory,
    purchase_price: float = None,
    if_doesnt_exists_only: bool = False,
):
    if if_doesnt_exists_only:
        ticket = Ticket.objects.filter(
            category=ticket_category, participant=participant, status=Ticket.CREATED,
        ).first()
        if ticket:
            return ticket

    # Create QR-code
    qr_code = QrCode(type=QrCode.TICKET)
    qr_code.save()

    # Check for guest invite
    guest_invite_id = chat_context.get("guest_invite_id")
    guest_invite = None
    if guest_invite_id:
        try:
            guest_invite = GuestInvite.objects.get(id=guest_invite_id)
        except GuestInvite.DoesNotExist:
            pass

        if guest_invite and not (guest_invite.ticket_category == ticket_category):
            guest_invite = None
        else:
            bot.remove_chat_context_items(
                incoming_data.from_id, ["guest_invite_id"], chat_context
            )

    # Create ticket
    return Ticket.objects.create(
        qr_code=qr_code,
        category=ticket_category,
        purchase_price=(purchase_price or ticket_category.base_price),
        participant=participant,
        guest_invite=guest_invite,
    )


def buy_tickets_for_category_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, handler_value: str
):
    try:
        ticket_category = TicketCategory.objects.get(pk=handler_value)
    except TicketCategory.DoesNotExist:
        return logger.warning(
            "No ticket category with such ID for ticket buying: %s", handler_value
        )

    if not _check_event_availability(bot, incoming_data, ticket_category.event):
        return

    from_data = incoming_data.original_data["callback_query"]["from"]

    participant = Participant.get_or_create(
        telegram_id=incoming_data.from_id,
        first_name=from_data.get("first_name", ""),
        last_name=from_data.get("last_name", ""),
        username=from_data.get("username", ""),
    )

    if not _check_ticket_category_availability(bot, incoming_data, ticket_category):
        return

    if not _check_participant_ticket_limit(
        bot, incoming_data, participant, ticket_category
    ):
        return

    if _check_participant_is_blocked(bot, incoming_data, participant):
        return

    if ticket_category.is_free():
        ticket = _create_ticket(
            bot, incoming_data, chat_context, participant, ticket_category
        )
        if ticket_category.selfie_required:
            _upload_selfie_handler(bot, incoming_data, chat_context, ticket)
        else:
            ticket.send_to_participant()
    elif ticket_category.with_manual_confirmation:
        ticket = _create_ticket(
            bot, incoming_data, chat_context, participant, ticket_category
        )
        if ticket_category.selfie_required:
            _upload_selfie_handler(bot, incoming_data, chat_context, ticket)
        else:
            ticket.request_payment_confirmation()
    elif ticket_category.selfie_required:
        ticket = _create_ticket(
            bot, incoming_data, chat_context, participant, ticket_category
        )
        _upload_selfie_handler(bot, incoming_data, chat_context, ticket)
    elif ticket_category.with_auto_confirmation():
        ticket = _create_ticket(
            bot, incoming_data, chat_context, participant, ticket_category
        )
        ticket.send_checkout_details()


def just_request_payment_confirmation_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, handler_value: str
):
    try:
        ticket = Ticket.objects.get(pk=handler_value)
    except TicketCategory.DoesNotExist:
        return logger.warning(
            "No ticket with such ID for ticket buying: %s", handler_value
        )

    ticket.request_payment_confirmation()


def document_upload_handler(bot: Bot, incoming_data: IncomingData, chat_context: dict):
    if try_handle_additional_data(bot, incoming_data, chat_context, mode="document"):
        return

    if chat_context.get("image_processing") in ("confirm_purchase", "upload_selfie"):
        bot.client.send_message(
            incoming_data.from_id, "Используйте загрузку изображения, а не документа.",
        )
    else:
        bot.client.send_message(
            incoming_data.from_id, "Невозможно обработать загруженный документ.",
        )


def _selfie_image_upload_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, ticket_id
):
    file_ = bot.client.download_file(incoming_data.message_photo.file_id)
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return logger.error("Ticket not found: %s", ticket_id)

    if ticket.selfies.count() > 0:
        return bot.client.send_message(
            incoming_data.from_id, "Для данного билета уже загружено селфи."
        )

    with transaction.atomic():
        ticket_selfie = TicketSelfie(ticket=ticket)
        ticket_selfie.image.save(
            f"{incoming_data.message_photo.file_unique_id}.jpg", File(file_), save=True,
        )
        ticket_selfie.save()

        bot.remove_chat_context_items(
            incoming_data.from_id,
            [UPLOAD_SELFIE_CHAT_CONTEXT_KEY, "upload_selfie"],
            chat_context,
        )

        if ticket.category.additional_data_short_request:
            return _request_additional_data_short(
                bot, incoming_data, chat_context, ticket_selfie
            )
        elif ticket.category.additional_data_request:
            return _request_additional_data(
                bot, incoming_data, chat_context, ticket_selfie
            )

        bot.client.send_message(
            incoming_data.from_id, "Селфи загружено. Ожидайте проверки."
        )


def _request_additional_data(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, ticket_selfie
):
    additional_data_request = ticket_selfie.ticket.category.additional_data_request

    bot.set_chat_context(
        incoming_data.from_id,
        {**chat_context, "additional_data_for_selfie": ticket_selfie.id},
    )

    message_text = (
        "Организатор запросил дополнительные данные для идентификации:\n"
        f'"{additional_data_request}"\n'
        "Вам нужно отправить их в этот чат.\n"
        'После отправки всех данных нажмите кнопку "Готово".'
    )

    bot.client.send_message(
        incoming_data.from_id,
        message_text,
        inline_keyboard=[[{"text": "Готово", "callback_data": "additional_data_done"}]],
    )


def _request_additional_data_short(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, ticket_selfie
):
    bot.set_chat_context(
        incoming_data.from_id,
        {
            **chat_context,
            "additional_data_for_selfie": ticket_selfie.id,
            "additional_data_for_selfie_short": True,
        },
    )

    bot.client.send_message(
        incoming_data.from_id,
        (
            ticket_selfie.ticket.category.additional_data_request
            or "Теперь отправьте дополнительные данные в текстовом сообщении."
        ),
    )


def clear_message_markup(bot: Bot, incoming_data: IncomingData):
    bot.client.call_api(
        "editMessageReplyMarkup",
        {
            "chat_id": incoming_data.from_id,
            "message_id": incoming_data.original_data["callback_query"]["message"][
                "message_id"
            ],
        },
    )


def _additional_data_done(bot: Bot, incoming_data: IncomingData, chat_context: dict):
    bot.remove_chat_context_items(
        incoming_data.from_id,
        ["additional_data_for_selfie", "additional_data_for_selfie_short"],
        chat_context,
    )
    bot.client.send_message(incoming_data.from_id, "Готово. Ожидайте проверки.")


def additional_data_done_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, *args
):
    _additional_data_done(bot, incoming_data, chat_context)
    clear_message_markup(bot, incoming_data)


def handle_additional_data(
    bot: Bot,
    incoming_data: IncomingData,
    chat_context: dict,
    ticket_selfie_id: int,
    mode: str,
):
    try:
        ticket_selfie = TicketSelfie.objects.get(id=ticket_selfie_id)
    except TicketSelfie.DoesNotExist:
        return logger.error("No selfie with such id: %s", ticket_selfie_id)

    if chat_context.get("additional_data_for_selfie_short"):
        SelfieMessage.objects.create(
            selfie=ticket_selfie, text=incoming_data.message_text
        )
        return _additional_data_done(bot, incoming_data, chat_context)

    if mode == "text":
        SelfieMessage.objects.create(
            selfie=ticket_selfie, text=incoming_data.message_text
        )
        bot.client.send_message(
            incoming_data.from_id,
            (
                "Вы добавили тестовое сообщение. "
                f"Всего сообщений добавлено: {ticket_selfie.messages.count()}."
            ),
        )

    elif mode in ("document", "image"):
        if mode == "image":
            file_ = bot.client.download_file(incoming_data.message_photo.file_id)
            file_name = f"{incoming_data.message_photo.file_unique_id}.jpg"
        else:
            file_ = bot.client.download_file(incoming_data.message_document.file_id)
            file_name = incoming_data.message_document.file_name
        selfie_upload = SelfieUpload(selfie=ticket_selfie)
        selfie_upload.file.save(
            file_name, File(file_), save=True,
        )
        selfie_upload.save()
        bot.client.send_message(
            incoming_data.from_id,
            (
                "Вы добавили вложение. "
                f"Всего вложений добавлено: {ticket_selfie.attachments.count()}."
            ),
        )


# FIXME: ticket already defined
def _purchase_confirmation_image_upload_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, ticket_category_id
):
    # Fetch image
    file_ = bot.client.download_file(incoming_data.message_photo.file_id)

    participant = Participant.get_by_telegram_id(incoming_data.from_id)
    ticket = Ticket.objects.get(id=ticket_category_id)
    ticket_category = ticket.category

    if not _check_ticket_category_availability(bot, incoming_data, ticket_category):
        return

    if not _check_participant_ticket_limit(
        bot, incoming_data, participant, ticket_category
    ):
        return

    if _check_participant_is_blocked(bot, incoming_data, participant):
        return

    with transaction.atomic():
        purchase_confirmation = PurchaseConfirmation(ticket=ticket)
        purchase_confirmation.image.save(
            f"{incoming_data.message_photo.file_unique_id}.jpg", File(file_), save=True,
        )
        purchase_confirmation.save()

        bot.remove_chat_context_items(
            incoming_data.from_id,
            [CONFIRM_PURCHASE_CHAT_CONTEXT_KEY, "image_processing"],
            chat_context,
        )

        bot.client.send_message(
            incoming_data.from_id, "Изображение загружено. Ожидайте проверки оплаты.",
        )


def image_upload_handler(bot: Bot, incoming_data: IncomingData, chat_context: dict):
    if try_handle_additional_data(bot, incoming_data, chat_context, mode="image"):
        return

    image_processing = chat_context.get("image_processing")
    if image_processing == "confirm_purchase":
        ticket_id = chat_context.get(CONFIRM_PURCHASE_CHAT_CONTEXT_KEY)
        _purchase_confirmation_image_upload_handler(
            bot, incoming_data, chat_context, ticket_id
        )
    elif image_processing == "upload_selfie":
        ticket_id = chat_context.get(UPLOAD_SELFIE_CHAT_CONTEXT_KEY)
        _selfie_image_upload_handler(bot, incoming_data, chat_context, ticket_id)
    else:
        bot.client.send_message(
            incoming_data.from_id, "Невозможно обработать загруженное изображение.",
        )


def pre_checkout_query_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict
):
    invoice_payload = incoming_data.pre_checkout_query["invoice_payload"]
    ticket_category = TicketCategory.get_from_invoice_payload(invoice_payload)
    if not ticket_category:
        logger.warning(
            "No ticket category for such invoice payload: %s", invoice_payload
        )
        return bot.client.call_api(
            "answerPreCheckoutQuery",
            {
                "pre_checkout_query_id": incoming_data.pre_checkout_query_id,
                "ok": False,
                "error_message": "Не найдена указанная категория билетов.",
            },
        )

    purchase_price = TicketCategory.get_purchase_price(
        incoming_data.pre_checkout_query["total_amount"]
    )
    participant = Participant.get_or_create(
        telegram_id=incoming_data.from_id,
        first_name=incoming_data.pre_checkout_query["from"].get("first_name", ""),
        last_name=incoming_data.pre_checkout_query["from"].get("last_name"),
        username=incoming_data.pre_checkout_query["from"].get("username"),
    )
    _create_ticket(
        bot,
        incoming_data,
        chat_context,
        participant,
        ticket_category,
        purchase_price,
        if_doesnt_exists_only=True,
    )

    bot.client.call_api(
        "answerPreCheckoutQuery",
        {"pre_checkout_query_id": incoming_data.pre_checkout_query_id, "ok": True},
    )


def successful_payment_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict
):
    invoice_payload = incoming_data.successful_payment["invoice_payload"]
    ticket_category = TicketCategory.get_from_invoice_payload(invoice_payload)
    participant = Participant.get_by_telegram_id(incoming_data.from_id)
    ticket = ticket_category.tickets.filter(
        status=Ticket.CREATED, participant=participant
    ).first()
    if ticket:
        payment_id = incoming_data.successful_payment.get("provider_payment_charge_id")
        ticket.send_to_participant(payment_id=payment_id)


def _preprocess_ticket_action(
    bot: Bot, incoming_data: IncomingData, handler_value: str
) -> Optional[Ticket]:
    try:
        ticket = Ticket.objects.get(id=int(handler_value))
    except Ticket.DoesNotExist as e:
        return logger.exception(e)

    clear_message_markup(bot, incoming_data)

    return ticket


def accept_visitor_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, handler_value: str
):
    ticket = _preprocess_ticket_action(bot, incoming_data, handler_value)
    if not ticket:
        return

    ticket.set_used()

    bot.client.send_message(
        incoming_data.from_id, f"{ACCEPT_ICON} Проход на мероприятие разрешён."
    )

    bot.client.send_message(
        ticket.participant.telegram_id,
        f'{ACCEPT_ICON} Вы допущены на мероприятие "{ticket.category.event.name}".',
    )


def add_ticket_comment_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, handler_value: str
):
    try:
        ticket = Ticket.objects.get(id=int(handler_value))
    except Ticket.DoesNotExist as e:
        return logger.exception(e)

    bot.set_chat_context(
        incoming_data.from_id,
        {**chat_context, "waiting_for_ticket_comment": ticket.id},
    )

    bot.client.send_message(incoming_data.from_id, "Напишите в чат текст комментария.")


def _make_refund(bot: Bot, incoming_data: IncomingData, ticket: Ticket):
    success = ticket.set_returned()

    if not success:
        return bot.client.send_message(
            incoming_data.from_id,
            (
                f"{REFUND_ICON} Не удалось выполнить возврат и аннулировать билет. "
                "Попробуйте ещё раз."
            ),
        )

    if ticket.category.is_free():
        extra_text = ""
        extra_text2 = ""
        icon = ""
    else:
        extra_text = "\nВозврат средств будет выполнен в ближайшее время."
        extra_text2 = "\nВозврат средств будет выполнен в ближайшее время."
        icon = f"{REFUND_ICON} "

    bot.client.send_message(
        incoming_data.from_id,
        (f"{icon}Билет аннулирван.{extra_text}"),
        inline_keyboard=[
            [
                {
                    "text": "Добавить комментарий",
                    "callback_data": f"add_ticket_comment|{ticket.id}",
                }
            ]
        ],
    )

    bot.client.send_message(
        ticket.participant.telegram_id, (f"{icon}Ваш билет аннулирван.{extra_text2}"),
    )


def decline_visitor_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, handler_value: str
):
    ticket = _preprocess_ticket_action(bot, incoming_data, handler_value)
    if not ticket:
        return

    bot.client.send_message(
        incoming_data.from_id, f"{DECLINE_ICON} В проходе на мероприятие отказано."
    )

    bot.client.send_message(
        ticket.participant.telegram_id,
        f"{DECLINE_ICON} Вам отказано в проходе на мероприятие.",
    )

    _make_refund(bot, incoming_data, ticket)


def refund_visitor_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, handler_value: str
):
    ticket = _preprocess_ticket_action(bot, incoming_data, handler_value)
    if not ticket:
        return

    _make_refund(bot, incoming_data, ticket)


def _upload_selfie_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, ticket: Ticket
):
    if ticket.category.avoid_selfie_reconfirmation:
        if ticket.participant.have_confirmed_selfie():
            return ticket.category.after_selfie_confirmation(ticket)

    bot.set_chat_context(
        incoming_data.from_id,
        {
            **chat_context,
            UPLOAD_SELFIE_CHAT_CONTEXT_KEY: ticket.id,
            "image_processing": "upload_selfie",
        },
    )

    bot.client.send_message(
        incoming_data.from_id, "Загрузите в чат селфи для контроля на входе.",
    )


def handle_ticket_comment_adding(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, ticket_id: int
):
    bot.remove_chat_context_items(
        incoming_data.from_id, ["waiting_for_ticket_comment"], chat_context
    )

    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist as e:
        return logger.exception(e)

    ticket.set_access_control_comment(incoming_data.message_text)

    bot.client.send_message(
        incoming_data.from_id,
        f"{ENVELOPE_ICON} Ваш комментарий отправлен организатору.",
    )


CALLBACK_QUERY_HANDLER_MAP = {
    "buy_tickets": buy_tickets_handler,
    "buy_tickets:for_category": buy_tickets_for_category_handler,
    "just_request_confirmation": just_request_payment_confirmation_handler,
    "accept_visitor": accept_visitor_handler,
    "decline_visitor": decline_visitor_handler,
    "refund_visitor": refund_visitor_handler,
    "add_ticket_comment": add_ticket_comment_handler,
    "staff_invite:choose_category": staff_invite_choose_category_handler,
    "additional_data_done": additional_data_done_handler,
}


def handle_callback_query(bot: Bot, incoming_data: IncomingData, chat_context: dict):
    handler_slug, _, handler_value = incoming_data.callback_data.partition("|")
    handler = CALLBACK_QUERY_HANDLER_MAP.get(handler_slug)
    if not handler:
        return logger.warning(
            "No callback query handler for such slug: %s", handler_slug
        )
    handler(bot, incoming_data, chat_context, handler_value)
    bot.client.call_api(
        "answerCallbackQuery", {"callback_query_id": incoming_data.callback_query_id}
    )


def try_handle_additional_data(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, mode: str
):
    if (selfie_id := chat_context.get("additional_data_for_selfie")) :
        handle_additional_data(bot, incoming_data, chat_context, int(selfie_id), mode)
        return True
    return False


class DefaultScenario:
    @classmethod
    def run(self, bot: Bot, incoming_data: IncomingData, chat_context: dict):
        if incoming_data.type == IncomingDataType.MESSAGE:
            if incoming_data.message_entities:
                if incoming_data.message_entities[0]["type"] == "bot_command":
                    (
                        command_name,
                        _,
                        command_payload,
                    ) = incoming_data.message_text.partition(" ")
                    if command_name == "/start":
                        if command_payload:
                            return process_start_qr_code(
                                bot, incoming_data, chat_context, command_payload
                            )
                        else:
                            bot.reset_chat_context(incoming_data.from_id)
                            return fallback_handler(bot, incoming_data, chat_context)
            elif incoming_data.successful_payment:
                return successful_payment_handler(bot, incoming_data, chat_context)
            elif incoming_data.message_document:
                return document_upload_handler(bot, incoming_data, chat_context)
            elif incoming_data.message_photo:
                return image_upload_handler(bot, incoming_data, chat_context)
        elif incoming_data.type == IncomingDataType.CALLBACK_QUERY:
            return handle_callback_query(bot, incoming_data, chat_context)
        elif incoming_data.type == IncomingDataType.PRE_CHECKOUT_QUERY:
            return pre_checkout_query_handler(bot, incoming_data, chat_context)
        elif incoming_data.type == IncomingDataType.CHAT_MEMBER_UPDATED:
            return
        elif not incoming_data.type == IncomingDataType.MESSAGE:
            return bot.client.send_message(
                incoming_data.from_id, "Недопустимый тип сообщения. Используйте текст."
            )

        if (ticket_id := chat_context.get("waiting_for_ticket_comment")) :
            return handle_ticket_comment_adding(
                bot, incoming_data, chat_context, int(ticket_id)
            )

        if try_handle_additional_data(bot, incoming_data, chat_context, mode="text"):
            return

        fallback_handler(bot, incoming_data, chat_context)
