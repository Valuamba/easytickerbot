from django.core.exceptions import ValidationError
from rest_framework.fields import JSONField

from apps.bots.serializers import BotSerializer
from apps.events.serializers import EventSerializer
from apps.locations.serializers import LocationSerializer, SublocationSerializer
from apps.management.serializers import OrganizerBoundSerializer
from apps.participants.serializers import ParticipantSerializer
from apps.staff.models import StaffInvite, StaffMember
from apps.unraveled.serializers import StaffCategorySerializer


class StaffInviteSerializer(OrganizerBoundSerializer):
    bot_data = BotSerializer(read_only=True)
    qr_code_computed_data = JSONField(read_only=True)
    staff_categories_data = StaffCategorySerializer(read_only=True, many=True)

    class Meta:
        model = StaffInvite
        fields = [
            "id",
            "bot",
            "bot_data",
            "qr_code_computed_data",
            "staff_categories",
            "staff_categories_data",
            "organizer",
            "organizer_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class StaffMemberSerializer(OrganizerBoundSerializer):
    staff_category_data = StaffCategorySerializer(read_only=True)
    participant_data = ParticipantSerializer(read_only=True)
    current_access_control_event_data = EventSerializer(read_only=True)
    current_access_control_location_data = LocationSerializer(read_only=True)
    current_access_control_sublocation_data = SublocationSerializer(read_only=True)

    def validate(self, attrs):
        current_access_control_location = attrs.get("current_access_control_location")
        current_access_control_sublocation = attrs.get(
            "current_access_control_sublocation"
        )

        if current_access_control_sublocation:
            if (
                current_access_control_sublocation
                not in current_access_control_location.sublocations.all()
            ):
                raise ValidationError(
                    {
                        "current_access_control_sublocation": (
                            "Указанная саблокация не относится к выбранной локации"
                        ),
                    }
                )

        return attrs

    class Meta:
        model = StaffMember
        fields = [
            "id",
            "participant",
            "participant_data",
            "staff_category",
            "staff_category_data",
            "current_access_control_event",
            "current_access_control_event_data",
            "current_access_control_location",
            "current_access_control_location_data",
            "current_access_control_sublocation",
            "current_access_control_sublocation_data",
            "organizer",
            "organizer_data",
            "is_approved",
            "created_at",
        ]
        read_only_fields = ["created_at"]
