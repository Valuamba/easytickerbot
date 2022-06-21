from apps.bots.models import Bot
from apps.bots.scenarios._generic import (
    check_access_control_event,
    check_access_control_location,
    check_access_control_sublocation,
    send_access_denied,
)
from apps.events.models import StaffPass
from apps.qrcodes.models import QrCode
from apps.staff.models import StaffMember
from lib.icons import ACCEPT_ICON
from lib.telegram import IncomingData


def handle_staff_qr(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, qr_code: QrCode
):
    try:
        access_control_member = StaffMember.get_access_control_member(
            incoming_data.from_id
        )
    except StaffMember.DoesNotExist:
        return bot.client.send_message(
            incoming_data.from_id, "Вы не можете осуществлять пропускной контроль."
        )

    try:
        staff_pass = qr_code.staffpass
    except StaffPass.DoesNotExist:
        return send_access_denied(bot, incoming_data, "пропуск недействителен")

    if not check_access_control_event(
        bot,
        incoming_data,
        access_control_member,
        staff_pass.event,
        "пропуск персонала не соответствует мероприятию",
    ):
        return

    if not check_access_control_location(
        bot,
        incoming_data,
        access_control_member,
        staff_pass.get_allowed_locations(),
        "у персонала нет доступа к локации",
    ):
        return

    if not check_access_control_sublocation(
        bot,
        incoming_data,
        access_control_member,
        staff_pass.get_allowed_sublocations(),
        "у персонала нет доступа к саблокации",
    ):
        return

    bot.client.send_message(
        incoming_data.from_id, f"{ACCEPT_ICON} Доступ для персонала разрешён."
    )
