from apps.bots.models import Bot
from apps.bots.scenarios._generic import check_access_control_location
from apps.qrcodes.models import QrCode
from apps.staff.models import StaffMember
from apps.tickets.models import UnifiedPass
from lib.icons import ACCEPT_ICON
from lib.telegram import IncomingData


def handle_unified_pass_qr(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, qr_code: QrCode
):
    unified_pass = UnifiedPass.get_by_qr_code(qr_code)
    if not unified_pass:
        return bot.client.send_message(incoming_data.from_id, "Пропуск не найден.")

    access_control_member = StaffMember.get_access_control_member(incoming_data.from_id)
    is_access_control = bool(access_control_member)

    if not is_access_control:
        return bot.client.send_message(
            incoming_data.from_id, "Вы не можете осуществлять пропускной контроль."
        )

    if not check_access_control_location(
        bot,
        incoming_data,
        access_control_member,
        [unified_pass.location],
        "у универсального пропуска нет доступа к локации",
    ):
        return

    bot.client.send_message(
        incoming_data.from_id,
        f"{ACCEPT_ICON} Доступ по универсальному пропуску разрешён.",
    )
