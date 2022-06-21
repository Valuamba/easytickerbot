import logging

import requests
from django.core.exceptions import ValidationError
from rest_framework.exceptions import ValidationError as DrfValidationError
from rest_framework.fields import empty, get_error_detail

from apps.management.serializers import OrganizerBoundSerializer

from .models import Bot

logger = logging.getLogger(__name__)


class BotSerializer(OrganizerBoundSerializer):
    def __init__(self, instance=None, data=empty, **kwargs):
        super(BotSerializer, self).__init__(instance, data, **kwargs)

        if "request" not in self._context:
            return

        if hasattr(self, "initial_data"):
            try:
                # Check token
                token = self.initial_data.get("token")
                if not token:
                    return
                instance = Bot(token=token)
                check_data = instance.client.check_token()
                if not check_data:
                    raise DrfValidationError(
                        get_error_detail(
                            ValidationError({"token": "Токен недействителен."})
                        )
                    )

                # Set username
                self.initial_data["username"] = check_data["result"]["username"]
            except requests.RequestException as e:
                logger.exception(e)
                raise DrfValidationError(
                    get_error_detail(
                        ValidationError(
                            {
                                "token": (
                                    "Невозможно проверить корректность токена из-за "
                                    "проблем с подключением к API Telegram. Попробуйте "
                                    "позже."
                                )
                            }
                        )
                    )
                )

    def save(self, **kwargs):
        instance: Bot = super(BotSerializer, self).save(**kwargs)

        try:
            instance.register_webhook()
        except requests.RequestException as e:
            logger.exception(e)
            raise DrfValidationError(
                get_error_detail(
                    ValidationError(
                        {
                            "non_field_errors": (
                                "Невозможно зарегистрировать вебхук. Попробуйте позже."
                            )
                        }
                    )
                )
            )

        return instance

    class Meta:
        model = Bot
        fields = [
            "id",
            "username",
            "token",
            "organizer",
            "organizer_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]
