from datetime import timedelta

from django.test import TestCase
from django.utils import timezone

from apps.bots.models import Bot
from apps.events.models import Event
from apps.management.models import AdminAccount


class TestBot(TestCase):
    def test_get_nearest_events(self):
        self.assertEqual(
            list(self.bot1.get_nearest_events()),
            [self.event2, self.event3, self.event4],
        )
        self.assertEqual(list(self.bot2.get_nearest_events()), [self.event5])
        self.assertEqual(list(self.bot3.get_nearest_events()), [])

    @classmethod
    def setUpTestData(cls):
        now = timezone.now()

        cls.organizer1 = AdminAccount.objects.create_user(
            "organizer1@chatme.ai", role=AdminAccount.ORGANIZER
        )

        cls.bot1 = Bot(
            username="Test1Bot", token="xxx_secret_token1", organizer=cls.organizer1
        )
        cls.bot1.save()

        cls.bot2 = Bot(
            username="Test2Bot", token="xxx_secret_token2", organizer=cls.organizer1
        )
        cls.bot2.save()

        cls.bot3 = Bot(
            username="Test3Bot", token="xxx_secret_token3", organizer=cls.organizer1
        )
        cls.bot3.save()

        cls.event1 = Event.objects.create(
            name="Test event #1",
            time_start=(now - timedelta(days=1, hours=3)),
            time_end=(now - timedelta(days=1, hours=1)),
            organizer=cls.organizer1,
            bot=cls.bot1,
        )
        cls.event2 = Event.objects.create(
            name="Test event #2",
            time_start=(now - timedelta(hours=1)),
            time_end=(now + timedelta(hours=2)),
            organizer=cls.organizer1,
            bot=cls.bot1,
        )
        cls.event3 = Event.objects.create(
            name="Test event #3",
            time_start=(now + timedelta(days=1)),
            time_end=(now + timedelta(days=1, hours=2)),
            organizer=cls.organizer1,
            bot=cls.bot1,
        )
        cls.event4 = Event.objects.create(
            name="Test event #4",
            time_start=(now + timedelta(days=1, minutes=1)),
            time_end=(now + timedelta(days=1, hours=2, minutes=1)),
            organizer=cls.organizer1,
            bot=cls.bot1,
        )

        cls.event5 = Event.objects.create(
            name="Test event #5",
            time_start=(now + timedelta(days=1)),
            time_end=(now + timedelta(days=1, hours=2)),
            organizer=cls.organizer1,
            bot=cls.bot2,
        )
