from rest_framework import serializers
from rest_framework.fields import empty
from rest_framework.serializers import ModelSerializer

from apps.management.models import AdminAccount
from apps.unraveled.serializers2 import SimpleBotSerializer


class AdminAccountSerializer(ModelSerializer):
    new_password = serializers.CharField(
        min_length=6, allow_blank=True, allow_null=True
    )
    new_password_confirmation = serializers.CharField(
        min_length=6, allow_blank=True, allow_null=True
    )
    notification_bot_data = SimpleBotSerializer(read_only=True)

    def validate(self, attrs):
        new_password = attrs.get("new_password")
        new_password_confirmation = attrs.get("new_password_confirmation")

        if new_password or new_password_confirmation:
            if new_password != new_password_confirmation:
                raise serializers.ValidationError("Пароли должны совпадать.")

        return super(AdminAccountSerializer, self).validate(attrs)

    class Meta:
        model = AdminAccount
        fields = [
            "id",
            "email",
            "role",
            "role_label",
            "first_name",
            "last_name",
            "is_active",
            "date_joined",
            "new_password",
            "new_password_confirmation",
            "notification_bot",
            "notification_bot_data",
            "organizer_telegram_checkout_token",
            "organizer_shop_id",
            "organizer_shop_secret",
            "organizer_fondy_merchant_id",
            "organizer_fondy_merchant_password",
            "telegram_id",
        ]
        extra_kwargs = {
            "new_password": {"write_only": True},
            "new_password_confirmation": {"write_only": True},
        }


class OrganizerBoundSerializer(ModelSerializer):
    organizer_data = AdminAccountSerializer(read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super(OrganizerBoundSerializer, self).__init__(instance, data, **kwargs)

        if "request" not in self._context:
            return

        current_user = self._context["request"].user

        if current_user.role == AdminAccount.ORGANIZER:
            if hasattr(self, "initial_data"):
                self.initial_data["organizer"] = (
                    instance.organizer_id if instance else current_user.id
                )


class LocationOwnerBoundSerializer(ModelSerializer):
    location_owner_data = AdminAccountSerializer(read_only=True)

    def __init__(self, instance=None, data=empty, **kwargs):
        super(LocationOwnerBoundSerializer, self).__init__(instance, data, **kwargs)

        if "request" not in self._context:
            return

        current_user = self._context["request"].user

        if current_user.role == AdminAccount.LOCATION_OWNER:
            if hasattr(self, "initial_data"):
                self.initial_data["location_owner"] = (
                    instance.location_owner_id if instance else current_user.id
                )
