import rest_framework.urls
from django.urls import include, path
from django.views.generic import TemplateView
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import DefaultRouter
from rest_framework.schemas import get_schema_view

from apps.bots.viewsets import BotViewSet
from apps.events.viewsets import EventReportViewSet, EventViewSet
from apps.locations.viewsets import LocationViewSet, SublocationViewSet
from apps.staff.viewsets import (
    StaffCategoryViewSet,
    StaffInviteViewSet,
    StaffMemberViewSet,
)

from ..fileuploads.viewsets import ImageUploadViewSet
from ..notifications.viewsets import NotificationViewSet
from ..participants.viewsets import ParticipantViewSet
from ..tickets.viewsets import (
    GuestInviteViewSet,
    PurchaseConfirmationViewSet,
    TicketCategoryViewSet,
    TicketSelfieViewSet,
    TicketViewSet,
    UnifiedPassViewSet,
)
from .views import AccountView
from .viewsets import AdminAccountViewSet

router = DefaultRouter()
router.register(r"admin-accounts", AdminAccountViewSet)
router.register(r"locations", LocationViewSet)
router.register(r"sublocations", SublocationViewSet)
router.register(r"events", EventViewSet)
router.register(r"event-reports", EventReportViewSet)
router.register(r"bots", BotViewSet)
router.register(r"participants", ParticipantViewSet)
router.register(r"staff-categories", StaffCategoryViewSet)
router.register(r"staff-members", StaffMemberViewSet)
router.register(r"staff-invites", StaffInviteViewSet)
router.register(r"ticket-categories", TicketCategoryViewSet)
router.register(r"tickets", TicketViewSet)
router.register(r"guest-invites", GuestInviteViewSet)
router.register(r"unified-passes", UnifiedPassViewSet)
router.register(r"purchase-confirmations", PurchaseConfirmationViewSet)
router.register(r"ticket-selfies", TicketSelfieViewSet)
router.register(r"image-uploads", ImageUploadViewSet)
router.register(r"notifications", NotificationViewSet)

urlpatterns = [
    path(
        "management-api/redoc/",
        TemplateView.as_view(
            template_name="redoc.html", extra_context={"schema_url": "openapi-schema"}
        ),
        name="redoc",
    ),
    path("management-api/openapi-schema", get_schema_view(), name="openapi-schema"),
    path("management-api/api-auth/", include(rest_framework.urls)),
    path("management-api/auth", obtain_auth_token),
    path("management-api/account", AccountView.as_view()),
    path("management-api/", include(router.urls)),
]
