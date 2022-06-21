import os

from django.db import models
from sorl.thumbnail import get_thumbnail

from apps.generic.models import TimeStamped


# NOTE: to provide maximum flexibility for future,
#  image uploads are not user-bound. Instead we restrict deleting of image uploads.
class ImageUpload(TimeStamped):
    file = models.FileField(upload_to="image_uploads/%Y/%m/%d")

    @property
    def is_video(self):
        return os.path.splitext(self.file.name)[1] == ".mp4"

    @property
    def thumbnail_url(self):
        if self.is_video:
            return self.file.url

        return get_thumbnail(self.file, "200", crop="center").url


class HasPoster(models.Model):
    poster = models.ForeignKey(
        ImageUpload, on_delete=models.SET_NULL, blank=True, null=True
    )
    telegram_poster_id = models.CharField(max_length=1000, blank=True, default="")

    def __init__(self, *args, **kwargs):
        super(HasPoster, self).__init__(*args, **kwargs)
        self._original_poster = self.poster

    def save(self, force_insert=False, force_update=False, *args, **kwargs):
        if self.poster != self._original_poster:
            self.telegram_poster_id = ""

        super(HasPoster, self).save(force_insert, force_update, *args, **kwargs)
        self._original_poster = self.poster

    def get_poster_file(self):
        if not self.poster:
            return

        if self.poster.is_video:
            return self.poster.file
        else:
            return get_thumbnail(self.poster.file, "1024", scale=False)

    def get_poster_file_or_file_id(self):
        if self.telegram_poster_id:
            return self.telegram_poster_id
        else:
            return self.get_poster_file()

    def poster_is_video(self):
        return self.poster and self.poster.is_video

    def update_telegram_poster_id(self, new_telegram_poster_id):
        if new_telegram_poster_id and (
            new_telegram_poster_id != self.telegram_poster_id
        ):
            self.telegram_poster_id = new_telegram_poster_id
            self.save(update_fields=["telegram_poster_id"])

    class Meta:
        abstract = True
