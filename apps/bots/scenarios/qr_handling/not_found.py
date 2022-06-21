from apps.bots.models import Bot
from lib.telegram import IncomingData


def handle_not_found_qr(bot: Bot, incoming_data: IncomingData, chat_context: dict):
    message_text = "Предоставлен некорректный QR-код."
    bot.client.send_message(incoming_data.from_id, message_text)
