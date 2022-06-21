import logging
import secrets
import typing
from functools import cached_property

from django.conf import settings
from django.db import models
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone
from rest_framework.utils import json

from apps.generic.models import TimeStamped
from apps.management.models import OrganizerBound
from lib.redis import redis_client
from lib.telegram.client import TelegramClient

if typing.TYPE_CHECKING:
    from apps.events.models import Event

logger = logging.getLogger(__name__)


class Bot(TimeStamped, OrganizerBound):
    CHAT_CONTEXT_KEY_PREFIX = "chat_context"

    username = models.CharField(max_length=500)
    token = models.CharField(max_length=250)
    registered_webhook = models.CharField(max_length=2000, blank=True, default="")
    secret = models.CharField(max_length=1000, blank=True, default="", unique=True)

    @cached_property
    def client(self) -> TelegramClient:
        return TelegramClient(token=self.token, api_origin=settings.TELEGRAM_API_ORIGIN)

    def save(self, *args, **kwargs):
        if not self.secret:
            self.secret = secrets.token_urlsafe()
        super(Bot, self).save(*args, **kwargs)

    def register_webhook(self, save=True):
        webhook_url = self.get_webhook_url()

        if self.registered_webhook == webhook_url:
            logger.info("Webhook already registered: %s", {"bot_name": self.username})
            return

        self.client.set_webhook(webhook_url)
        self.registered_webhook = webhook_url
        if save:
            self.save(update_fields=["registered_webhook"])

        logger.info("Webhook successfully registered for bot: %s", self.username)

    def get_webhook_url(self):
        webhook_path = reverse("bots:webhook", kwargs={"bot_secret": self.secret})
        return f"{settings.PUBLIC_ORIGIN}{webhook_path}"

    def get_chat_context(self, chat_id) -> dict:
        context_str = redis_client.get(f"{self.CHAT_CONTEXT_KEY_PREFIX}:{chat_id}")
        if context_str:
            return json.loads(context_str)
        return {}

    def set_chat_context(self, chat_id, context_data):
        context_str = json.dumps(context_data)
        redis_client.set(f"{self.CHAT_CONTEXT_KEY_PREFIX}:{chat_id}", context_str)

    def reset_chat_context(self, chat_id):
        self.set_chat_context(chat_id, {})

    def remove_chat_context_items(self, chat_id, keys, chat_context=None):
        if not chat_context:
            chat_context = self.get_chat_context(chat_id)

        new_chat_context = {k: v for k, v in chat_context.items() if k not in keys}

        self.set_chat_context(chat_id, new_chat_context)

    def get_nearest_events(self) -> QuerySet["Event"]:
        return self.events.filter(time_end__gt=timezone.now()).order_by("time_start")

    def get_url(self):
        return f"https://t.me/{self.username}"
