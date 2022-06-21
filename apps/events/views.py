from rest_framework.exceptions import NotFound
from rest_framework.response import Response
from rest_framework.views import APIView

from ..management.models import AdminAccount
from .models import Event


class SendEventPassesView(APIView):
    def post(self, request, id=None):
        current_user = request.user

        if current_user.role == AdminAccount.SUPER_ADMIN:
            event_queryset = Event.objects.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            event_queryset = Event.objects.filter(organizer=current_user)
        else:
            event_queryset = Event.objects.none()

        try:
            event = event_queryset.get(id=id)
        except Event.DoesNotExist:
            raise NotFound

        force_resending = request.data.get("force_resending", False)

        sent_count = event.send_staff_passes(force_resending)

        return Response({"sent_count": sent_count})


class MakeRefundForUnusedTicketsView(APIView):
    def post(self, request, id=None):
        current_user = request.user

        if current_user.role == AdminAccount.SUPER_ADMIN:
            event_queryset = Event.objects.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            event_queryset = Event.objects.filter(organizer=current_user)
        else:
            event_queryset = Event.objects.none()

        try:
            event = event_queryset.get(id=id)
        except Event.DoesNotExist:
            raise NotFound

        event.make_refund_for_unused_tickets()

        return Response({"success": True})
