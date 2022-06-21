from ..generic.viewsets import CustomModelViewSet
from .models import AdminAccount
from .serializers import AdminAccountSerializer


class AdminAccountViewSet(CustomModelViewSet):
    queryset = AdminAccount.objects.all()
    serializer_class = AdminAccountSerializer
    search_fields = [
        "id",
        "email",
        "role",
        "is_active",
    ]

    def get_queryset(self):
        role_str = self.request.query_params.get("role")
        if role_str:
            return self.queryset.filter(role=role_str)
        return self.queryset.all()


class OrganizerOrientedViewSet(CustomModelViewSet):
    def get_queryset(self):
        current_user = self.request.user

        if current_user.role == AdminAccount.SUPER_ADMIN:
            return self.queryset.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            return self.queryset.filter(organizer=current_user)

        return self.queryset.none()
