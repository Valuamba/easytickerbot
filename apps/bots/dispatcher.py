import apps.bots.scenarios.guest.informational
from apps.bots.models import Bot
from apps.bots.scenarios.default import DefaultScenario
from lib.telegram.datatypes import IncomingData

SCENARIOS = [
    apps.bots.scenarios.guest.informational.InformationalGuestScenario,
]

SCENARIO_MAP = {scenario.slug: scenario for scenario in SCENARIOS}


def dispatch(bot: Bot, incoming_data: IncomingData):
    chat_context = bot.get_chat_context(incoming_data.from_id)

    scenario = SCENARIO_MAP.get(chat_context.get("scenario_slug"))

    if scenario:
        scenario.run(bot, incoming_data, chat_context)
    else:
        DefaultScenario.run(bot, incoming_data, chat_context)
