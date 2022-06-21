from ..management.viewsets import OrganizerOrientedViewSet
from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(OrganizerOrientedViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    search_fields = [
        "id",
        "location__name",
        "event__name",
        "type",
        "ticket_category__name",
        "staff_category__name",
        "schedule_time",
        "was_sent",
        "organizer__email",
        "created_at",
    ]
