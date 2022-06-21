from rest_framework.settings import api_settings

from ..management.viewsets import OrganizerOrientedViewSet
from .models import Bot
from .permissions import BotPermissions
from .serializers import BotSerializer


class BotViewSet(OrganizerOrientedViewSet):
    queryset = Bot.objects.all()
    serializer_class = BotSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [
        BotPermissions,
    ]
    search_fields = [
        "id",
        "username",
        "organizer__email",
        "created_at",
    ]
