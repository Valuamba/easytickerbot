from ..management.viewsets import OrganizerOrientedViewSet
from .models import Event
from .serializers import EventReportSerializer, EventSerializer


class EventViewSet(OrganizerOrientedViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    search_fields = [
        "name",
        "time_start",
        "time_end",
        "organizer__email",
        "bot__username",
        "created_at",
    ]


class EventReportViewSet(OrganizerOrientedViewSet):
    queryset = Event.objects.all()
    serializer_class = EventReportSerializer
