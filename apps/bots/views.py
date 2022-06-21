import json
import logging

from django.http import Http404, HttpRequest, HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.bots import dispatcher
from apps.bots.models import Bot
from lib.telegram import IncomingData

logger = logging.getLogger(__name__)


@csrf_exempt
def webhook_view(request: HttpRequest, bot_secret=None):
    try:
        bot = Bot.objects.get(secret=bot_secret)
    except Bot.DoesNotExist:
        raise Http404

    try:
        json_data = json.loads(request.body)
    except json.JSONDecodeError:
        logger.error("Invalid JSON body: %s", request.body)
        return HttpResponse(status=400)

    incoming_data = IncomingData.parse(json_data)

    dispatcher.dispatch(bot, incoming_data)

    return HttpResponse()
