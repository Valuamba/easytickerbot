from django.core.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from apps.management.serializers import (
    AdminAccountSerializer,
    LocationOwnerBoundSerializer,
)

from .models import Location, Sublocation


class LocationSerializer(LocationOwnerBoundSerializer):
    organizers_data = AdminAccountSerializer(read_only=True, many=True)

    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "location_owner",
            "location_owner_data",
            "organizers",
            "organizers_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class MinimalLocationSerializer(LocationOwnerBoundSerializer):
    class Meta:
        model = Location
        fields = [
            "id",
            "name",
            "location_owner",
            "location_owner_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class SublocationSerializer(ModelSerializer):
    location_data = LocationSerializer(read_only=True)
    location_owner_data = AdminAccountSerializer(read_only=True)
    organizers_data = AdminAccountSerializer(read_only=True, many=True)

    class Meta:
        model = Sublocation
        fields = [
            "id",
            "name",
            "location",
            "location_data",
            "location_owner_data",
            "organizers_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class LocationBoundSerializer(ModelSerializer):
    available_locations_data = LocationSerializer(read_only=True, many=True)
    available_sublocations_data = SublocationSerializer(read_only=True, many=True)

    def validate(self, attrs):
        available_locations = attrs.get("available_locations")
        available_sublocations = attrs.get("available_sublocations")

        if available_sublocations:
            possible_sublocations = []
            for available_location in available_locations:
                possible_sublocations.extend(
                    list(available_location.sublocations.all())
                )

            for available_sublocation in available_sublocations:
                if available_sublocation not in possible_sublocations:
                    raise ValidationError(
                        {
                            "available_sublocations": (
                                "Указанные саблокации не соотносятся с "
                                "указанными локациями."
                            ),
                        }
                    )

        return attrs
