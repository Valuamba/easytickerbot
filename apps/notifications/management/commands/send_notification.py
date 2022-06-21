from django.core.management.base import BaseCommand

from apps.notifications.models import Notification


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("notification_id", type=int)

    def handle(self, *args, **options):
        notification_id = options["notification_id"]
        notification = Notification.objects.get(id=notification_id)
        notification.send()
