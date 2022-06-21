import json
import logging

from apps.bots.models import Bot
from apps.bots.scenarios._generic import (
    check_access_control_event,
    check_access_control_location,
    check_access_control_sublocation,
)
from apps.qrcodes.models import QrCode
from apps.staff.models import StaffMember
from apps.tickets.models import Ticket
from apps.tickets.renderers import render_ticket_info
from lib.icons import ACCEPT_ICON, DECLINE_ICON, REFUND_ICON
from lib.telegram import IncomingData
from lib.telegram.datatypes import ParseMode

logger = logging.getLogger(__name__)


def _display_selfie(
    bot: Bot,
    incoming_data: IncomingData,
    ticket: Ticket,
    caption,
    inline_keyboard=None,
):
    ticket_selfie = ticket.get_confirmed_selfie()

    if not ticket_selfie:
        if ticket.category.selfie_required:
            return bot.client.send_message(
                incoming_data.from_id, "Селфи не подтверждено.",
            )

        return bot.client.send_message(
            incoming_data.from_id,
            caption,
            parse_mode=ParseMode.MARKDOWN_V2,
            inline_keyboard=inline_keyboard,
        )

    if ticket_selfie.telegram_image_id:
        selfie_image = ticket_selfie.telegram_image_id
    else:
        selfie_image = ticket_selfie.get_selfie_image()

    if selfie_image:
        if inline_keyboard:
            reply_markup = json.dumps({"inline_keyboard": inline_keyboard})
        else:
            reply_markup = None
        response = bot.client.send_image(
            incoming_data.from_id,
            selfie_image,
            caption=caption,
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN_V2,
        )

        try:
            response.raise_for_status()
        except Exception as e:
            logger.exception(e)
            return bot.client.send_message(
                incoming_data.from_id, "Ошибка при показе селфи через Telegram API."
            )

        json_data = response.json()

        new_telegram_image_id = json_data["result"]["photo"][-1]["file_id"]
        if new_telegram_image_id != ticket_selfie.telegram_image_id:
            ticket_selfie.telegram_image_id = new_telegram_image_id
            ticket_selfie.save(update_fields=["telegram_image_id"])


def _display_ticket_info(
    bot: Bot, incoming_data: IncomingData, ticket: Ticket, access_control_mode=False
):
    inline_buttons = []

    if access_control_mode:
        if ticket.is_used():
            inline_buttons = [
                {
                    "text": f"{REFUND_ICON} Выполнить возврат",
                    "callback_data": f"refund_visitor|{ticket.id}",
                },
            ]
        elif ticket.is_payed():
            inline_buttons = [
                {
                    "text": f"{ACCEPT_ICON} Пропустить",
                    "callback_data": f"accept_visitor|{ticket.id}",
                },
                {
                    "text": f"{DECLINE_ICON} Отказать",
                    "callback_data": f"decline_visitor|{ticket.id}",
                },
            ]

        _display_selfie(
            bot,
            incoming_data,
            ticket,
            render_ticket_info(ticket, access_control=True),
            ([inline_buttons] if inline_buttons else None),
        )
    else:
        bot.client.send_message(
            incoming_data.from_id,
            render_ticket_info(ticket),
            parse_mode=ParseMode.MARKDOWN_V2,
            # FIXME: are inline_buttons really need here?
            inline_keyboard=([inline_buttons] if inline_buttons else None),
        )


def handle_ticket_qr(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, qr_code: QrCode
):
    ticket = Ticket.get_by_qr_code(qr_code)
    if not ticket:
        return bot.client.send_message(incoming_data.from_id, "Билет не найден.")

    if not (ticket.status == Ticket.PAYED):
        return bot.client.send_message(incoming_data.from_id, "Билет недействителен.")

    access_control_member = StaffMember.get_access_control_member(incoming_data.from_id)
    is_access_control = bool(access_control_member)

    if is_access_control:
        if not check_access_control_event(
            bot,
            incoming_data,
            access_control_member,
            ticket.category.event,
            "билет не соответствует мероприятию",
        ):
            return

        if not check_access_control_location(
            bot,
            incoming_data,
            access_control_member,
            ticket.category.available_locations.all(),
            "у билета нет доступа к локации",
        ):
            return

        if not check_access_control_sublocation(
            bot,
            incoming_data,
            access_control_member,
            ticket.category.available_sublocations.all(),
            "у билета нет доступа к саблокации",
        ):
            return

        if ticket.category.is_expired():
            return bot.client.send_message(
                incoming_data.from_id, "Время действия билета истекло."
            )

    _display_ticket_info(bot, incoming_data, ticket, is_access_control)
