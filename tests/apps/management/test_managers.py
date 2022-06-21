from django.test import TestCase

from apps.management.models import AdminAccount


class TestCustomUserManager(TestCase):
    def setUp(self):
        self.user_manager = AdminAccount.objects

    def test_create_user(self):
        with self.assertRaises(ValueError):
            self.user_manager.create_user(email=None)

        USER1_EMAIL = "user1@chatme.ai"

        user1 = self.user_manager.create_user(email=USER1_EMAIL)

        self.assertEqual(user1.email, USER1_EMAIL)
        self.assertEqual(user1.is_staff, False)
        self.assertEqual(user1.is_superuser, False)

    def test_create_superuser(self):
        SUPERUSER1_EMAIL = "superuser1@chatme.ai"

        with self.assertRaises(ValueError):
            self.user_manager.create_superuser(email=SUPERUSER1_EMAIL, is_staff=False)

        with self.assertRaises(ValueError):
            self.user_manager.create_superuser(
                email=SUPERUSER1_EMAIL, is_superuser=False
            )

        superuser1 = self.user_manager.create_superuser(email=SUPERUSER1_EMAIL)

        self.assertEqual(superuser1.email, SUPERUSER1_EMAIL)
        self.assertEqual(superuser1.is_staff, True)
        self.assertEqual(superuser1.is_superuser, True)
