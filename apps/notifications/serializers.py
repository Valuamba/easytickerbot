from django.core.exceptions import ValidationError

from ..events.serializers import EventSerializer
from ..locations.serializers import LocationSerializer
from ..management.serializers import OrganizerBoundSerializer
from ..tickets.serializers import TicketCategorySerializer
from ..unraveled.serializers import StaffCategorySerializer
from .models import Notification


class NotificationSerializer(OrganizerBoundSerializer):
    event_data = EventSerializer(read_only=True)
    location_data = LocationSerializer(read_only=True)
    ticket_category_data = TicketCategorySerializer(read_only=True)
    staff_category_data = StaffCategorySerializer(read_only=True)

    def validate(self, attrs):
        super(NotificationSerializer, self).validate(attrs)

        location = attrs.get("location")
        event = attrs.get("event")

        if not location and not event:
            raise ValidationError("Требуется выбрать мероприятие или локацию.")

        if event and location:
            if location not in event.locations.all():
                raise ValidationError(
                    {"location": "Локация не соответствует выбранному мероприятию."}
                )

        return attrs

    class Meta:
        model = Notification
        fields = [
            "id",
            "location",
            "location_data",
            "event",
            "event_data",
            "type",
            "type_label",
            "ticket_category",
            "ticket_category_data",
            "staff_category",
            "staff_category_data",
            "schedule_time",
            "text",
            "poster",
            "telegram_poster_id",
            "was_sent",
            "organizer",
            "organizer_data",
            "created_at",
        ]
        read_only_fields = ["created_at", "was_sent"]
