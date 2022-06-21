from typing import Optional

from django.conf import settings
from django.db import models

from apps.bots.models import Bot
from apps.generic.models import TimeStamped
from apps.locations.models import Location, LocationBound, Sublocation
from apps.management.models import OrganizerBound
from apps.participants.models import Participant
from apps.qrcodes.models import QrCode, QrCodeBound


class StaffCategory(TimeStamped, OrganizerBound, LocationBound):
    ACCESS_CONTROL = "access_control"
    BAR = "bar"
    STEREOTYPE_CHOICES = (
        (ACCESS_CONTROL, "Пропускной контроль"),
        (BAR, "Бар"),
    )

    parent = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="children",
    )
    name = models.CharField(max_length=200)
    stereotype = models.CharField(
        max_length=500, choices=STEREOTYPE_CHOICES, blank=True, null=True
    )

    @property
    def stereotype_label(self):
        return self.get_stereotype_display()

    @property
    def parent_data(self):
        return self.parent

    def get_children_recursive(self):
        children = set()
        for child in self.children.all():
            children.add(child)
            for c in child.get_children_recursive():
                children.add(c)
        return children


class StaffInvite(TimeStamped, OrganizerBound, QrCodeBound):
    bot = models.ForeignKey(Bot, on_delete=models.CASCADE)
    staff_categories = models.ManyToManyField(StaffCategory, related_name="+")

    @property
    def staff_categories_data(self):
        return self.staff_categories

    @property
    def qr_code_computed_data(self):
        return {
            "start_url": self.qr_code.get_start_url(self.bot.username),
            "base64_image": self.qr_code.get_base64_image(self.bot.username),
        }

    def save(self, *args, **kwargs):
        if not self.qr_code_id:
            qr_code = QrCode(type=QrCode.STAFF_INVITE)
            qr_code.save()
            self.qr_code = qr_code
        super(StaffInvite, self).save(*args, **kwargs)

    @property
    def bot_data(self):
        return self.bot


class StaffMember(TimeStamped, OrganizerBound):
    participant = models.OneToOneField(Participant, on_delete=models.CASCADE)
    staff_category = models.ForeignKey(
        StaffCategory,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name="staff_members",
    )
    is_approved = models.BooleanField(default=False)
    staff_invite = models.ForeignKey(
        StaffInvite, on_delete=models.SET_NULL, blank=True, null=True
    )
    current_access_control_event = models.ForeignKey(
        "events.Event", on_delete=models.SET_NULL, blank=True, null=True
    )
    current_access_control_location = models.ForeignKey(
        Location, on_delete=models.SET_NULL, blank=True, null=True
    )
    current_access_control_sublocation = models.ForeignKey(
        Sublocation, on_delete=models.SET_NULL, blank=True, null=True
    )

    @property
    def current_access_control_event_data(self):
        return self.current_access_control_event

    @property
    def current_access_control_location_data(self):
        return self.current_access_control_location

    @property
    def current_access_control_sublocation_data(self):
        return self.current_access_control_sublocation

    @property
    def participant_data(self):
        return self.participant

    @property
    def staff_category_data(self):
        return self.staff_category

    def __init__(self, *args, **kwargs):
        super(StaffMember, self).__init__(*args, **kwargs)
        self._original_is_approved = self.is_approved

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.is_approved != self._original_is_approved:
            self.handle_is_approved_change(self._original_is_approved, self.is_approved)

        is_creating = not self.id

        super(StaffMember, self).save(force_insert, force_update, *args, **kwargs)
        self._original_is_approved = self.is_approved

        if is_creating:
            self.handle_create()

    def handle_is_approved_change(self, old_value, new_value):
        if new_value:
            if self.staff_invite:
                self.staff_invite.bot.client.send_message(
                    self.participant.telegram_id,
                    (
                        "Для вашего аккаунта подтверждена категория персонала "
                        f'"{self.staff_category.name}".'
                    ),
                )
        else:
            if self.staff_invite:
                self.staff_invite.bot.client.send_message(
                    self.participant.telegram_id,
                    (
                        "Для вашего аккаунта аннулирована категория персонала "
                        f'"{self.staff_category.name}".'
                    ),
                )

    def handle_create(self):
        if self.is_approved:
            return

        self.organizer.send_notification(
            (
                (
                    f'Новый член персонала в категории "{self.staff_category.name}" '
                    "ждёт одобрения:\n"
                )
                if self.staff_category
                else "Новый член персонала ждёт одобрения:\n"
            )
            + f"{self.get_public_edit_url()}"
        )

    def is_event_organizer(self, event):
        return self.organizer == event.organizer

    def is_access_control(self) -> bool:
        if self.staff_category:
            return self.staff_category.stereotype == StaffCategory.ACCESS_CONTROL
        return False

    @classmethod
    def get_approved(cls, telegram_id: int) -> Optional["StaffMember"]:
        try:
            return cls.objects.get(
                is_approved=True, participant__telegram_id=telegram_id
            )
        except cls.DoesNotExist:
            pass

    @classmethod
    def get_access_control_member(cls, telegram_id: int) -> Optional["StaffMember"]:
        approved_member = cls.get_approved(telegram_id)
        if approved_member and approved_member.is_access_control():
            return approved_member

    def get_public_edit_url(self):
        return f"{settings.PUBLIC_ORIGIN}/management/staff-members/{self.id}/edit"
