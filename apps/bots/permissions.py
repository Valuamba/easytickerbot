from apps.management.models import AdminAccount


class BotPermissions:
    def has_permission(self, request, view):
        return request.user.role in {AdminAccount.SUPER_ADMIN, AdminAccount.ORGANIZER}

    def has_object_permission(self, request, view, obj):
        current_user = request.user

        #  Enable full access to all bots for super_admin
        if current_user.role == AdminAccount.SUPER_ADMIN:
            return True

        #  Enable full access to owned bots for organizer
        if current_user.role == AdminAccount.ORGANIZER:
            return current_user.id == obj.organizer_id
