from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from .managers import CustomUserManager


class AdminAccount(AbstractUser):
    ORGANIZER = "organizer"
    LOCATION_OWNER = "location_owner"
    SUPER_ADMIN = "super_admin"
    ROLE_CHOICES = (
        (SUPER_ADMIN, "Суперадмин"),
        (LOCATION_OWNER, "Владелец локации"),
        (ORGANIZER, "Организатор"),
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["role"]

    username = None
    email = models.EmailField(_("email address"), unique=True)
    role = models.CharField(max_length=100, choices=ROLE_CHOICES)
    telegram_id = models.CharField(max_length=1000, blank=True, default="")
    notification_bot = models.ForeignKey(
        "bots.Bot", blank=True, null=True, on_delete=models.SET_NULL
    )
    organizer_telegram_checkout_token = models.CharField(
        max_length=1000, blank=True, default=""
    )
    organizer_shop_id = models.CharField(max_length=1000, blank=True, default="")
    organizer_shop_secret = models.CharField(max_length=1000, blank=True, default="")
    organizer_fondy_merchant_id = models.PositiveBigIntegerField(blank=True, null=True)
    organizer_fondy_merchant_password = models.CharField(
        max_length=1000, blank=True, default=""
    )

    objects = CustomUserManager()

    @property
    def new_password(self):
        pass

    @new_password.setter
    def new_password(self, value):
        if value:
            self.set_password(value)

    @property
    def new_password_confirmation(self):
        pass

    @new_password_confirmation.setter
    def new_password_confirmation(self, value):
        pass

    @property
    def role_label(self):
        return self.get_role_display()

    @property
    def notification_bot_data(self):
        return self.notification_bot

    def send_notification(self, text):
        if not self.notification_bot or not self.telegram_id:
            return

        self.notification_bot.client.send_message(self.telegram_id, text)


class OrganizerBound(models.Model):
    organizer = models.ForeignKey(
        AdminAccount,
        limit_choices_to={"role": AdminAccount.ORGANIZER},
        on_delete=models.CASCADE,
    )

    @property
    def organizer_data(self):
        return self.organizer

    class Meta:
        abstract = True


class LocationOwnerBound(models.Model):
    location_owner = models.ForeignKey(
        AdminAccount,
        limit_choices_to={"role": AdminAccount.LOCATION_OWNER},
        on_delete=models.CASCADE,
    )

    @property
    def location_owner_data(self):
        return self.location_owner

    class Meta:
        abstract = True


class CreatedByAdmin(models.Model):
    created_by = models.ForeignKey(
        AdminAccount, on_delete=models.SET_NULL, null=True, blank=True
    )

    class Meta:
        abstract = True
