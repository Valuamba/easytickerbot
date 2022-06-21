from typing import List, Union

from django.db.models import QuerySet

from apps.bots.models import Bot
from apps.locations.models import Location
from apps.staff.models import StaffMember
from lib.icons import DECLINE_ICON
from lib.telegram import IncomingData


def send_access_denied(bot: Bot, incoming_data: IncomingData, reason=None):
    bot.client.send_message(
        incoming_data.from_id,
        (f"{DECLINE_ICON} Доступ запрещён" + (f": {reason}." if reason else ".")),
    )


def check_access_control_event(
    bot: Bot,
    incoming_data: IncomingData,
    access_control_member: StaffMember,
    target_event,
    fail_reason,
) -> bool:
    controlled_event = access_control_member.current_access_control_event

    if not controlled_event:
        bot.client.send_message(
            incoming_data.from_id,
            (
                "Вы не можете производить контроль доступа. "
                "Для вас не назначено мероприятие."
            ),
        )
        return False

    if controlled_event != target_event:
        send_access_denied(bot, incoming_data, fail_reason)
        return False

    return True


def check_access_control_location(
    bot: Bot,
    incoming_data: IncomingData,
    access_control_member: StaffMember,
    allowed_locations: Union[QuerySet[Location], List[Location]],
    fail_reason,
) -> bool:
    controlled_location = access_control_member.current_access_control_location

    if not controlled_location:
        bot.client.send_message(
            incoming_data.from_id,
            "Вы не можете производить контроль доступа. Для вас не назначена локация.",
        )
        return False

    if controlled_location not in allowed_locations:
        send_access_denied(bot, incoming_data, fail_reason)
        return False

    return True


def check_access_control_sublocation(
    bot: Bot,
    incoming_data: IncomingData,
    access_control_member: StaffMember,
    allowed_sublocations,
    fail_reason,
) -> bool:
    controlled_sublocation = access_control_member.current_access_control_sublocation

    if controlled_sublocation and (controlled_sublocation not in allowed_sublocations):
        send_access_denied(bot, incoming_data, fail_reason)
        return False

    return True
