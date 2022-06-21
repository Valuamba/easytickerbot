import logging

from apps.bots.models import Bot
from apps.participants.models import Participant
from apps.qrcodes.models import QrCode
from apps.staff.models import StaffCategory, StaffInvite, StaffMember
from lib.telegram import IncomingData

logger = logging.getLogger(__name__)


def staff_invite_choose_category_handler(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, handler_value: str
):
    staff_category_id, _, qr_code_id = handler_value.partition(":")

    try:
        qr_code = QrCode.objects.get(id=qr_code_id)
    except QrCode.DoesNotExist as e:
        bot.client.send_message(
            incoming_data.from_id, "Предоставлены недействительные данные."
        )
        return logger.exception(e)

    staff_invite: StaffInvite = qr_code.staffinvite

    try:
        staff_category = staff_invite.staff_categories.get(id=int(staff_category_id))
    except StaffCategory.DoesNotExist as e:
        bot.client.send_message(
            incoming_data.from_id, "Выбрана недопустимая категория персонала."
        )
        return logger.exception(e)

    participant = Participant.get_or_create(
        telegram_id=incoming_data.from_id,
        first_name=incoming_data.original_data["callback_query"]["from"].get(
            "first_name", ""
        ),
        last_name=incoming_data.original_data["callback_query"]["from"].get(
            "last_name", ""
        ),
        username=incoming_data.original_data["callback_query"]["from"].get(
            "username", ""
        ),
    )

    try:
        StaffMember.objects.get(participant=participant)
        return bot.client.send_message(
            incoming_data.from_id, "Вы уже зарегистрированы в качестве персонала."
        )
    except StaffMember.DoesNotExist:
        StaffMember.objects.create(
            organizer=staff_invite.organizer,
            participant=participant,
            staff_category=staff_category,
            staff_invite=staff_invite,
        )

    bot.client.send_message(
        incoming_data.from_id, "Ваша заявка отправлена. Ожидайте подтверждения."
    )
