from apps.bots.models import Bot
from apps.qrcodes.models import QrCode
from lib.telegram import IncomingData


def handle_staff_invite_qr(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, qr_code: QrCode
):
    staff_invite = qr_code.staffinvite

    inline_keyboard = [
        [
            {
                "text": staff_category.name,
                "callback_data": (
                    f"staff_invite:choose_category|{staff_category.id}:{qr_code.id}"
                ),
            },
        ]
        for staff_category in staff_invite.staff_categories.all()
    ]

    message_text = "Выберите категорию персонала к которой вы желаете присоединиться:"
    bot.client.send_message(
        incoming_data.from_id, message_text, inline_keyboard=inline_keyboard
    )
