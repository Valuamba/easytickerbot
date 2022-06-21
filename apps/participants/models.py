from decimal import Decimal
from typing import Optional

from django.db import models, transaction
from django.db.models import F
from django.utils import timezone

from apps.generic.models import TimeStamped


class Participant(TimeStamped):
    telegram_id = models.PositiveBigIntegerField(unique=True)
    first_name = models.CharField(max_length=500, blank=True, default="")
    last_name = models.CharField(max_length=500, blank=True, default="")
    username = models.CharField(max_length=500, blank=True, default="")
    balance = models.DecimalField(blank=True, default=0, decimal_places=2, max_digits=9)
    is_blocked = models.BooleanField(default=False)

    def change_balance(self, delta: Decimal):
        with transaction.atomic():
            self.balance = F("balance") + delta
            self.save(update_fields=["balance"])
            self.refresh_from_db()
            if self.balance < 0:
                raise self.BalanceChangeError

    @classmethod
    def get_or_create(
        cls, telegram_id: int, first_name: str, last_name: str, username: str
    ) -> "Participant":
        instance, created = cls.objects.get_or_create(telegram_id=telegram_id)
        if created:
            instance.first_name = first_name
            instance.last_name = last_name
            instance.username = username
            instance.save()
        return instance

    @classmethod
    def get_by_telegram_id(cls, telegram_id: int) -> Optional["Participant"]:
        try:
            return cls.objects.get(telegram_id=telegram_id)
        except cls.DoesNotExist:
            pass

    @property
    def label(self):
        parts = [
            f"#{self.id}",
        ]
        if self.username:
            parts.append(f"@{self.username}")
        full_name = " ".join(
            filter(lambda v: bool(v), [self.first_name, self.last_name])
        )
        if full_name:
            parts.append(f"({full_name})")
        return " ".join(parts)

    def have_confirmed_selfie(self):
        return bool(self.get_confirmed_selfie())

    def get_confirmed_selfie(self):
        from apps.tickets.models import TicketSelfie

        for ticket in self.ticket_set.order_by("-id"):
            for ticket_selfie in ticket.selfies.order_by("-id"):
                if ticket_selfie.status == TicketSelfie.CONFIRMED:
                    return ticket_selfie

    def get_active_tickets(self):
        from apps.tickets.models import Ticket

        return self.ticket_set.filter(
            category__event__time_end__gt=timezone.now(),
            status__in=(Ticket.USED, Ticket.PAYED),
        ).order_by("category__event__time_start")

    class BalanceChangeError(Exception):
        pass
