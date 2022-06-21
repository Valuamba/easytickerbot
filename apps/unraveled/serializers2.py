from rest_framework.serializers import ModelSerializer

from apps.bots.models import Bot


class SimpleBotSerializer(ModelSerializer):
    class Meta:
        model = Bot
        fields = [
            "id",
            "username",
        ]
