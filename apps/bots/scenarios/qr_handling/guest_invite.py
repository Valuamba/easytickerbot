from apps.bots.models import Bot
from apps.bots.scenarios.tickets.buying import (
    _check_event_availability,
    _display_event,
    _display_ticket_category,
)
from apps.qrcodes.models import QrCode
from lib.telegram import IncomingData


def handle_guest_invite_qr(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, qr_code: QrCode
):
    guest_invite = qr_code.guestinvite

    event = guest_invite.ticket_category.event

    if not _check_event_availability(bot, incoming_data, event):
        return

    bot.client.send_message(incoming_data.from_id, "Вас пригласили на мероприятие:")

    _display_event(bot, incoming_data, event, False)

    bot.client.send_message(
        incoming_data.from_id, "Вам доступны следующие категории билетов:"
    )

    _display_ticket_category(
        bot, incoming_data, guest_invite.ticket_category,
    )

    bot.set_chat_context(
        incoming_data.from_id, {**chat_context, "guest_invite_id": guest_invite.id},
    )
