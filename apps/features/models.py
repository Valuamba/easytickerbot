from django.db import models

from apps.generic.models import TimeStamped


class Feature(TimeStamped):
    # category = ...
    name = models.CharField(max_length=500)
