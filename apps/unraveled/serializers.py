from django.core.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer

from apps.locations.serializers import LocationBoundSerializer
from apps.management.serializers import OrganizerBoundSerializer
from apps.staff.models import StaffCategory


class ParentStaffCategorySerializer(ModelSerializer):
    class Meta:
        model = StaffCategory
        fields = ["id", "name"]


class StaffCategorySerializer(OrganizerBoundSerializer, LocationBoundSerializer):
    parent_data = ParentStaffCategorySerializer(read_only=True)

    def validate(self, attrs):
        super(StaffCategorySerializer, self).validate(attrs)

        parent = attrs["parent"]

        if self.instance:
            if parent in self.instance.get_children_recursive():
                raise ValidationError(
                    {"parent": "Выбранное значение создаёт циклическую иерархию."}
                )

        return attrs

    class Meta:
        model = StaffCategory
        fields = [
            "id",
            "name",
            "parent",
            "parent_data",
            "stereotype",
            "stereotype_label",
            "available_locations",
            "available_locations_data",
            "available_sublocations",
            "available_sublocations_data",
            "organizer",
            "organizer_data",
            "created_at",
        ]
        read_only_fields = ["stereotype_label", "created_at"]
