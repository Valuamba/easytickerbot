import logging
import time

from django.core.management import BaseCommand

from apps.tickets.models import Ticket

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        while True:
            tickets = Ticket.objects.filter(status=Ticket.PENDING)
            logger.info("Running scheduler %d pending tickets found.", tickets.count())

            for ticket in tickets:
                ticket.check_yoomoney_payment()

            time.sleep(3)
