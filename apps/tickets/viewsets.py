from django.db.models import Q

from ..generic.viewsets import CustomModelViewSet
from ..management.models import AdminAccount
from ..management.viewsets import OrganizerOrientedViewSet
from .models import (
    GuestInvite,
    PurchaseConfirmation,
    Ticket,
    TicketCategory,
    TicketSelfie,
    UnifiedPass,
)
from .serializers import (
    GuestInviteSerializer,
    PurchaseConfirmationSerializer,
    TicketCategorySerializer,
    TicketSelfieSerializer,
    TicketSerializer,
    UnifiedPassSerializer,
)


class TicketCategoryViewSet(CustomModelViewSet):
    queryset = TicketCategory.objects.all()
    serializer_class = TicketCategorySerializer
    search_fields = [
        "id",
        "name",
        "event__name",
        "base_price",
        "max_ticket_count",
        "per_participant_limit",
        "with_manual_confirmation",
        "selfie_required",
        "is_active",
        "is_hidden",
        "created_at",
    ]

    def get_queryset(self):
        current_user = self.request.user

        if current_user.role == AdminAccount.SUPER_ADMIN:
            return self.queryset.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            return self.queryset.filter(event__organizer=current_user)

        return self.queryset.none()


class TicketViewSet(CustomModelViewSet):
    queryset = Ticket.objects.filter(~Q(status=Ticket.CREATED))
    serializer_class = TicketSerializer
    search_fields = [
        "id",
        "category__name",
        "category__event__name",
        "purchase_price",
        "payment_id",
        "participant__first_name",
        "participant__last_name",
        "participant__username",
        "status",
        "access_control_comment",
        "created_at",
    ]

    def get_queryset(self):
        current_user = self.request.user

        if current_user.role == AdminAccount.SUPER_ADMIN:
            return self.queryset.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            return self.queryset.filter(category__event__organizer=current_user)

        return self.queryset.none()


class PurchaseConfirmationViewSet(CustomModelViewSet):
    queryset = PurchaseConfirmation.objects.all()
    serializer_class = PurchaseConfirmationSerializer
    extra_ordering_fields = [
        "ticket__participant",
        "ticket__category",
        "ticket__category__event",
    ]
    search_fields = [
        "id",
        "status",
        "ticket__participant__first_name",
        "ticket__participant__last_name",
        "ticket__participant__username",
        "ticket__category__name",
        "ticket__category__event__name",
        "created_at",
    ]

    def get_queryset(self):
        current_user = self.request.user

        if current_user.role == AdminAccount.SUPER_ADMIN:
            return self.queryset.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            return self.queryset.filter(ticket__category__event__organizer=current_user)

        return self.queryset.none()


class TicketSelfieViewSet(CustomModelViewSet):
    queryset = TicketSelfie.objects.all()
    serializer_class = TicketSelfieSerializer
    extra_ordering_fields = [
        "ticket__participant",
        "ticket__category",
        "ticket__category__event",
    ]
    search_fields = [
        "id",
        "ticket__participant__username",
        "ticket__category__name",
        "ticket__category__event__name",
        "status",
        "created_at",
    ]

    def get_queryset(self):
        current_user = self.request.user

        if current_user.role == AdminAccount.SUPER_ADMIN:
            return self.queryset.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            return self.queryset.filter(ticket__category__event__organizer=current_user)

        return self.queryset.none()


class GuestInviteViewSet(OrganizerOrientedViewSet):
    queryset = GuestInvite.objects.all()
    serializer_class = GuestInviteSerializer
    search_fields = [
        "id",
        "ticket_category__name",
        "ticket_category__event__name",
        "organizer__email",
        "created_at",
    ]


class UnifiedPassViewSet(OrganizerOrientedViewSet):
    queryset = UnifiedPass.objects.all()
    serializer_class = UnifiedPassSerializer
    search_fields = [
        "id",
        "location__name",
        "bot__username",
        "organizer__email",
        "created_at",
    ]
