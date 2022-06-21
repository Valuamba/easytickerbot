from rest_framework.settings import api_settings

from apps.generic.viewsets import CustomModelViewSet
from apps.locations.models import Location, Sublocation
from apps.locations.permissions import LocationPermissions, SublocationPermissions
from apps.locations.serializers import LocationSerializer, SublocationSerializer
from apps.management.models import AdminAccount


class LocationViewSet(CustomModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [
        LocationPermissions,
    ]
    search_fields = [
        "id",
        "name",
        "location_owner__email",
        "created_at",
    ]

    def get_queryset(self):
        current_user = self.request.user

        if current_user.role == AdminAccount.LOCATION_OWNER:
            return self.queryset.filter(location_owner=current_user)
        elif current_user.role == AdminAccount.SUPER_ADMIN:
            return self.queryset.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            return current_user.organizer_locations.all()

        return self.queryset.none()


class SublocationViewSet(CustomModelViewSet):
    queryset = Sublocation.objects.all()
    serializer_class = SublocationSerializer
    permission_classes = api_settings.DEFAULT_PERMISSION_CLASSES + [
        SublocationPermissions,
    ]
    search_fields = [
        "id",
        "name",
        "location__name",
        "location__location_owner__email",
        "created_at",
    ]

    def get_queryset(self):
        current_user = self.request.user

        if current_user.role == AdminAccount.LOCATION_OWNER:
            return self.queryset.filter(location__location_owner=current_user)
        elif current_user.role == AdminAccount.SUPER_ADMIN:
            return self.queryset.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            return self.queryset.filter(location__organizers__in=[current_user])

        return self.queryset.none()
