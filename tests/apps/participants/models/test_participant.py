from decimal import Decimal

from django.test import TestCase

from apps.participants.models import Participant


class TestParticipant(TestCase):
    def test_change_balance(self):
        self.participant1.change_balance(Decimal(200))
        self.assertEqual(self.participant1.balance, Decimal(200))

        with self.assertRaises(Participant.BalanceChangeError):
            self.participant1.change_balance(Decimal(-300))

        self.participant1.refresh_from_db()
        self.assertEqual(self.participant1.balance, Decimal(200))

        self.participant1.change_balance(Decimal(-200))

        self.assertEqual(self.participant1.balance, Decimal(0))

    @classmethod
    def setUpTestData(cls):
        cls.participant1 = Participant.objects.create(telegram_id=9876543210)
