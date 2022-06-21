from ..generic.viewsets import CustomModelViewSet
from ..management.models import AdminAccount
from .models import Participant
from .serializers import ParticipantSerializer


class ParticipantViewSet(CustomModelViewSet):
    queryset = Participant.objects.all()
    serializer_class = ParticipantSerializer
    search_fields = [
        "id",
        "first_name",
        "last_name",
        "username",
        "telegram_id",
        "is_blocked",
    ]

    def get_queryset(self):
        current_user = self.request.user

        if current_user.role == AdminAccount.SUPER_ADMIN:
            return self.queryset.all()
        elif current_user.role == AdminAccount.ORGANIZER:
            return self.queryset.raw(
                """
            SELECT DISTINCT p.*
            FROM
                participants_participant p,
                tickets_ticket t,
                tickets_ticketcategory tc,
                events_event e,
                staff_staffmember sm
            WHERE (
                t.participant_id = p.id
                AND t.category_id = tc.id
                AND tc.event_id = e.id
                AND e.organizer_id = %(organizer_id)s
            )
            OR (
                p.id = sm.participant_id
                AND sm.organizer_id =  %(organizer_id)s
            )
            """,
                {"organizer_id": current_user.id},
            )

        return self.queryset.none()
