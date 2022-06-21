import logging

from django.db import models

from apps.events.models import Event
from apps.fileuploads.models import HasPoster
from apps.generic.models import TimeStamped
from apps.locations.models import Location
from apps.management.models import OrganizerBound
from apps.staff.models import StaffCategory, StaffMember
from apps.tickets.models import Ticket, TicketCategory

logger = logging.getLogger(__name__)


class Notification(TimeStamped, OrganizerBound, HasPoster):
    TO_ALL = "to_all"
    TO_STAFF = "to_staff"
    TO_GUESTS = "to_guests"
    TYPE_CHOICES = (
        (TO_ALL, "Всем"),
        (TO_STAFF, "Персоналу"),
        (TO_GUESTS, "Гостям"),
    )

    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, blank=True, null=True
    )
    event = models.ForeignKey(Event, on_delete=models.CASCADE, blank=True, null=True)
    type = models.CharField(max_length=100, choices=TYPE_CHOICES)
    staff_category = models.ForeignKey(
        StaffCategory, on_delete=models.CASCADE, blank=True, null=True
    )
    ticket_category = models.ForeignKey(
        TicketCategory, on_delete=models.CASCADE, blank=True, null=True
    )
    text = models.TextField()
    schedule_time = models.DateTimeField(blank=True, null=True)
    was_sent = models.BooleanField(default=False)

    @property
    def event_data(self):
        return self.event

    @property
    def location_data(self):
        return self.location

    def save(
        self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        super(Notification, self).save(
            force_insert=force_insert,
            force_update=force_update,
            using=using,
            update_fields=update_fields,
        )

        if not self.schedule_time and not self.was_sent:
            self.send()

    @property
    def type_label(self):
        return self.get_type_display()

    @property
    def ticket_category_data(self):
        return self.ticket_category

    @property
    def staff_category_data(self):
        return self.staff_category

    def _get_target_participants(self, event):
        if not event.bot:
            return set()

        target_participants = set()

        if self.type in (self.TO_ALL, self.TO_STAFF):
            if self.staff_category:
                staff_members = StaffMember.objects.filter(
                    staff_category=self.staff_category
                )
            else:
                staff_members = StaffMember.objects.filter(
                    staff_category__in=event.staff_categories.all()
                )

            for staff_member in staff_members:
                target_participants.add(staff_member.participant)

        if self.type in (self.TO_ALL, self.TO_GUESTS):
            ticket_filter_kwargs = {"status__in": [Ticket.USED]}
            if self.ticket_category:
                ticket_filter_kwargs["category"] = self.ticket_category
            else:
                ticket_filter_kwargs["category__event"] = event

            for ticket in Ticket.objects.filter(**ticket_filter_kwargs):
                target_participants.add(ticket.participant)

        return target_participants

    def send(self):
        # Get participants and its bots

        if self.location:
            location_events = self.location.get_past_events()
            target_participants = set()
            participant_bots = {}

            for event in location_events:
                target_participants_ = self._get_target_participants(event)
                for participant in target_participants:
                    participant_bots[participant] = event.bot
                target_participants.update(target_participants_)
        else:
            target_participants = self._get_target_participants(self.event)
            participant_bots = {
                participant: self.event.bot for participant in target_participants
            }

        # Send notifications

        for participant in target_participants:
            participant_bot = participant_bots.get(participant)
            try:
                poster_file = self.get_poster_file_or_file_id()
                if poster_file:
                    if not self.poster_is_video():
                        response = participant_bot.client.send_image(
                            participant.telegram_id, poster_file, caption=self.text,
                        )

                        json_data = response.json()
                        new_telegram_poster_id = json_data["result"]["photo"][-1][
                            "file_id"
                        ]
                    else:
                        response = participant_bot.client.send_video(
                            participant.telegram_id, poster_file, caption=self.text,
                        )

                        json_data = response.json()
                        new_telegram_poster_id = json_data["result"]["video"]["file_id"]

                    self.telegram_poster_id = new_telegram_poster_id
                else:
                    participant_bot.client.send_message(
                        participant.telegram_id, self.text
                    )
            except Exception as e:
                logger.exception(e)

        # Set notification as sent

        self.was_sent = True
        self.save(update_fields=["was_sent", "telegram_poster_id"])

    @classmethod
    def filter_for_date(cls, date):
        return cls.objects.filter(
            schedule_time__year=date.year,
            schedule_time__month=date.month,
            schedule_time__day=date.day,
            schedule_time__hour=date.hour,
            schedule_time__minute=date.minute,
        )

    class Meta:
        ordering = ("-id",)
