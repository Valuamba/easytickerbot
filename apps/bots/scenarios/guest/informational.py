from apps.bots.models import Bot
from lib.telegram import IncomingData


class InformationalGuestScenario:
    slug = "guest:informational"

    @classmethod
    def run(self, bot: Bot, incoming_data: IncomingData, chat_context: dict):
        message_text = "..."
        bot.client.send_message(incoming_data.from_id, message_text)
