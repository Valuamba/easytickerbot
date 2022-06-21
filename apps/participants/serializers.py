from rest_framework.serializers import ModelSerializer

from .models import Participant


class ParticipantSerializer(ModelSerializer):
    class Meta:
        model = Participant
        fields = [
            "id",
            "telegram_id",
            "first_name",
            "last_name",
            "username",
            "label",
            "is_blocked",
            "created_at",
        ]
        read_only_fields = ["created_at"]
