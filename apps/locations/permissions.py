from apps.management.models import AdminAccount


class LocationPermissions:
    def has_permission(self, request, view):
        if request.user.role == AdminAccount.ORGANIZER:
            if request.method == "POST":
                return False
        return True

    def has_object_permission(self, request, view, obj):
        current_user = request.user

        #  Enable full access to all locations for super_admin
        if current_user.role == AdminAccount.SUPER_ADMIN:
            return True

        #  Enable full access to owned locations for location owner
        if current_user.role == AdminAccount.LOCATION_OWNER:
            return current_user.id == obj.location_owner_id

        #  Enable reading of locations for assigned organizer
        if current_user.role == AdminAccount.ORGANIZER:
            if request.method == "GET":
                return obj.organizers.filter(id=current_user.id).exists()


class SublocationPermissions:
    def has_permission(self, request, view):
        if request.user.role == AdminAccount.ORGANIZER:
            if request.method == "POST":
                return False
        return True

    def has_object_permission(self, request, view, obj):
        current_user = request.user

        if current_user.role == AdminAccount.SUPER_ADMIN:
            return True

        if current_user.role == AdminAccount.LOCATION_OWNER:
            return current_user.id == obj.location.location_owner_id

        if current_user.role == AdminAccount.ORGANIZER:
            if request.method == "GET":
                return obj.location.organizers.filter(id=current_user.id).exists()
