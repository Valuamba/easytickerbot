from apps.management.viewsets import OrganizerOrientedViewSet
from apps.staff.models import StaffCategory, StaffInvite, StaffMember
from apps.staff.serializers import StaffInviteSerializer, StaffMemberSerializer
from apps.unraveled.serializers import StaffCategorySerializer


class StaffCategoryViewSet(OrganizerOrientedViewSet):
    queryset = StaffCategory.objects.all()
    serializer_class = StaffCategorySerializer
    search_fields = [
        "id",
        "name",
        "parent__name",
        "stereotype",
        "organizer__email",
        "created_at",
    ]


class StaffMemberViewSet(OrganizerOrientedViewSet):
    queryset = StaffMember.objects.all()
    serializer_class = StaffMemberSerializer
    extra_ordering_fields = ["participant__telegram_id"]
    search_fields = [
        "id",
        "participant__username",
        "participant__first_name",
        "participant__last_name",
        "participant__telegram_id",
        "organizer__email",
        "staff_category__name",
        "is_approved",
    ]


class StaffInviteViewSet(OrganizerOrientedViewSet):
    queryset = StaffInvite.objects.all()
    serializer_class = StaffInviteSerializer
    search_fields = [
        "id",
        "bot__username",
        "organizer__email",
        "created_at",
    ]
