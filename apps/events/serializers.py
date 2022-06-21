from rest_framework.serializers import ModelSerializer

from apps.bots.serializers import BotSerializer
from apps.events.models import Event
from apps.locations.serializers import LocationSerializer
from apps.management.serializers import OrganizerBoundSerializer
from apps.unraveled.serializers import StaffCategorySerializer


class MinimalEventSerializer(ModelSerializer):
    class Meta:
        model = Event
        fields = ["id", "name"]


class EventSerializer(OrganizerBoundSerializer):
    bot_data = BotSerializer(read_only=True)
    locations_data = LocationSerializer(read_only=True, many=True)
    staff_categories_data = StaffCategorySerializer(read_only=True, many=True)

    class Meta:
        model = Event
        fields = [
            "id",
            "name",
            "time_start",
            "time_end",
            "poster",
            "telegram_poster_id",
            "bot",
            "bot_data",
            "organizer",
            "organizer_data",
            "locations",
            "locations_data",
            "staff_categories",
            "staff_categories_data",
            "payment_type",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class EventReportSerializer(OrganizerBoundSerializer):
    class Meta:
        model = Event
        fields = ["id", "report_data"]
