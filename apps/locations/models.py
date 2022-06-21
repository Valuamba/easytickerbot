from django.db import models
from django.utils import timezone

from apps.generic.models import TimeStamped
from apps.management.models import AdminAccount, LocationOwnerBound


class Location(TimeStamped, LocationOwnerBound):
    name = models.CharField(max_length=1000)
    organizers = models.ManyToManyField(
        AdminAccount,
        limit_choices_to={"role": AdminAccount.ORGANIZER},
        related_name="organizer_locations",
        blank=True,
    )

    @property
    def organizers_data(self):
        return self.organizers

    def get_past_events(self):
        return self.events.filter(time_start__lte=timezone.now())

    class Meta:
        ordering = ("location_owner",)


class Sublocation(TimeStamped):
    location = models.ForeignKey(
        Location, on_delete=models.CASCADE, related_name="sublocations"
    )
    name = models.CharField(max_length=1000)

    @property
    def location_data(self):
        return self.location

    @property
    def location_owner_data(self):
        return self.location.location_owner

    @property
    def organizers_data(self):
        return self.location.organizers_data


class LocationBound(models.Model):
    available_locations = models.ManyToManyField(Location, blank=True)
    available_sublocations = models.ManyToManyField(Sublocation, blank=True)

    @property
    def available_locations_data(self):
        return self.available_locations

    @property
    def available_sublocations_data(self):
        return self.available_sublocations

    class Meta:
        abstract = True
