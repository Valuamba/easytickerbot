import base64
import secrets
from io import BytesIO

import qrcode
from django.db import models

from apps.generic.models import TimeStamped


class QrCode(TimeStamped):
    TOKEN_SIZE = 32
    TICKET = "ticket"
    STAFF = "staff"
    STAFF_INVITE = "staff_invite"
    GUEST_INVITE = "guest_invite"
    UNIFIED_PASS = "unified_pass"
    TYPE_CHOICES = (
        (TICKET, "Билет"),
        (STAFF, "Персонал"),
        (STAFF_INVITE, "Инвайт для персонала"),
        (GUEST_INVITE, "Инвайт для гостей"),
        (UNIFIED_PASS, "Универсальный пропуск"),
    )

    type = models.CharField(choices=TYPE_CHOICES, max_length=100)
    token = models.CharField(max_length=500, unique=True)

    @property
    def type_label(self):
        return self.get_type_display()

    def save(self, *args, **kwargs):
        # TODO: add collision protection
        if not self.token:
            self.token = secrets.token_urlsafe(self.TOKEN_SIZE)
        super(QrCode, self).save(*args, **kwargs)

    def get_start_url(self, bot_name):
        return f"https://t.me/{bot_name}?start={self.token}"

    def get_image(self, bot_name):
        internal_image = qrcode.make(self.get_start_url(bot_name))
        file_like_image = BytesIO()
        internal_image.save(file_like_image, format="PNG")
        file_like_image.seek(0)
        return file_like_image

    def get_base64_image(self, bot_name):
        image = self.get_image(bot_name)
        base64_image_data = base64.b64encode(image.read()).decode("utf-8")
        return f"data:image/png;base64,{base64_image_data}"


class QrCodeBound(models.Model):
    qr_code = models.OneToOneField(QrCode, on_delete=models.CASCADE)

    @property
    def qr_code_data(self):
        return self.qr_code

    @classmethod
    def get_by_qr_code(cls, qr_code: QrCode):
        try:
            return cls.objects.get(qr_code=qr_code)
        except cls.DoesNotExist:
            pass

    class Meta:
        abstract = True
