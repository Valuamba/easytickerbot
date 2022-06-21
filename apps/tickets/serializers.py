from django.db.models import QuerySet
from rest_framework.fields import JSONField
from rest_framework.serializers import ModelSerializer

from apps.bots.serializers import BotSerializer
from apps.events.serializers import EventSerializer, MinimalEventSerializer
from apps.locations.serializers import (
    LocationBoundSerializer,
    MinimalLocationSerializer,
)
from apps.management.serializers import OrganizerBoundSerializer
from apps.participants.serializers import ParticipantSerializer
from apps.tickets.models import (
    GuestInvite,
    PurchaseConfirmation,
    SelfieMessage,
    SelfieUpload,
    Ticket,
    TicketCategory,
    TicketSelfie,
    UnifiedPass,
)


class TicketCategorySerializer(LocationBoundSerializer):
    event_data = EventSerializer(read_only=True)

    class Meta:
        model = TicketCategory
        fields = [
            "id",
            "event",
            "event_data",
            "name",
            "description",
            "with_manual_confirmation",
            "selfie_required",
            "base_price",
            "max_ticket_count",
            "per_participant_limit",
            "available_locations",
            "available_locations_data",
            "available_sublocations",
            "available_sublocations_data",
            "available_ticket_count",
            "additional_data_request",
            "additional_data_short_request",
            "selfie_confirmed_text",
            "avoid_selfie_reconfirmation",
            "lifetime_end",
            # "available_features",
            # "available_features_data",
            "is_active",
            "is_hidden",
            "created_at",
        ]
        read_only_fields = ["available_ticket_count", "created_at"]


class MinimalTicketCategorySerializer(ModelSerializer):
    class Meta:
        model = TicketCategory
        fields = ["id", "name"]


class MinimalTicketCategorySerializer2(ModelSerializer):
    event_data = MinimalEventSerializer(read_only=True)

    class Meta:
        model = TicketCategory
        fields = ["id", "name", "event", "event_data"]


class PurchaseConfirmationSerializer(ModelSerializer):
    event_data = MinimalEventSerializer(read_only=True)
    ticket_category_data = MinimalTicketCategorySerializer(read_only=True)

    class Meta:
        model = PurchaseConfirmation
        fields = [
            "id",
            "status",
            "event_data",
            "status_label",
            "participant_label",
            "image",
            "ticket_category_data",
            "created_at",
        ]
        read_only_fields = ["id", "image", "status_label", "created_at"]


class SelfieUploadSerializer(ModelSerializer):
    class Meta:
        model = SelfieUpload
        fields = ["id", "selfie", "file"]


class SelfieMessageSerializer(ModelSerializer):
    class Meta:
        model = SelfieMessage
        fields = ["id", "selfie", "text"]


class TicketSelfieSerializer(ModelSerializer):
    EXCLUDE_FROM_LIST = [
        "attachments",
        "messages",
    ]

    event_data = MinimalEventSerializer(read_only=True)
    ticket_category_data = MinimalTicketCategorySerializer(read_only=True)
    attachments = SelfieUploadSerializer(many=True, read_only=True)
    messages = SelfieMessageSerializer(many=True, read_only=True)

    def get_field_names(self, declared_fields, info):
        field_names = super(TicketSelfieSerializer, self).get_field_names(
            declared_fields, info
        )
        if isinstance(self.instance, QuerySet):
            return [f for f in field_names if f not in self.EXCLUDE_FROM_LIST]
        return field_names

    class Meta:
        model = TicketSelfie
        fields = [
            "id",
            "status",
            "event_data",
            "status_label",
            "participant_label",
            "image",
            "ticket_category_data",
            "admin_comment",
            "attachments",
            "messages",
            "created_at",
        ]
        read_only_fields = ["id", "image", "status_label", "created_at"]


class GuestInviteSerializer(OrganizerBoundSerializer):
    EXCLUDE_FROM_LIST = (
        "purchased_ticket_count",
        "purchased_ticket_sum",
        "qr_code_computed_data",
    )

    ticket_category_data = MinimalTicketCategorySerializer2(read_only=True)
    qr_code_computed_data = JSONField(read_only=True)

    def get_field_names(self, declared_fields, info):
        field_names = super(GuestInviteSerializer, self).get_field_names(
            declared_fields, info
        )
        if isinstance(self.instance, QuerySet):
            return [f for f in field_names if f not in self.EXCLUDE_FROM_LIST]
        return field_names

    class Meta:
        model = GuestInvite
        fields = [
            "id",
            "ticket_category",
            "ticket_category_data",
            "qr_code_computed_data",
            "purchased_ticket_count",
            "purchased_ticket_sum",
            "organizer",
            "organizer_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class UnifiedPassSerializer(OrganizerBoundSerializer):
    EXCLUDE_FROM_LIST = ("qr_code_computed_data",)

    location_data = MinimalLocationSerializer(read_only=True)
    bot_data = BotSerializer(read_only=True)
    qr_code_computed_data = JSONField(read_only=True)

    def get_field_names(self, declared_fields, info):
        field_names = super(UnifiedPassSerializer, self).get_field_names(
            declared_fields, info
        )
        if isinstance(self.instance, QuerySet):
            return [f for f in field_names if f not in self.EXCLUDE_FROM_LIST]
        return field_names

    class Meta:
        model = UnifiedPass
        fields = [
            "id",
            "location",
            "location_data",
            "bot",
            "bot_data",
            "qr_code_computed_data",
            "organizer",
            "organizer_data",
            "created_at",
        ]
        read_only_fields = ["created_at"]


class TicketSerializer(ModelSerializer):
    category_data = MinimalTicketCategorySerializer2(read_only=True)
    participant_data = ParticipantSerializer(read_only=True)
    guest_invite_data = GuestInviteSerializer(read_only=True)

    class Meta:
        model = Ticket
        fields = [
            "id",
            "category",
            "category_data",
            "purchase_price",
            "payment_id",
            "participant",
            "participant_data",
            "status",
            "status_label",
            "guest_invite",
            "guest_invite_data",
            "access_control_comment",
            "created_at",
            "updated_at",
        ]
