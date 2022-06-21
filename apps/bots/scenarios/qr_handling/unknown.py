from apps.bots.models import Bot
from apps.qrcodes.models import QrCode
from lib.telegram import IncomingData


def handle_unknown_qr(
    bot: Bot, incoming_data: IncomingData, chat_context: dict, qr_code: QrCode
):
    message_text = "Предоставлен корректный QR-код неизвестного типа."
    bot.client.send_message(incoming_data.from_id, message_text)
