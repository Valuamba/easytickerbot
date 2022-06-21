from django.urls import reverse

from apps.management.models import AdminAccount
from apps.management.viewsets import AdminAccountViewSet
from tests.base import BaseApiTestCase


class TestAdminAccountApi(BaseApiTestCase):
    def test_list(self):
        list_view = AdminAccountViewSet.as_view({"get": "list"})

        self.check_entity_subset(list_view, self.super_admin1, self.all_admin_accounts)
        self.check_entity_subset(
            list_view,
            self.super_admin1,
            self.super_admins,
            url=f"{reverse('adminaccount-list')}?role=super_admin",
        )
        self.check_entity_subset(
            list_view,
            self.super_admin1,
            self.organizers,
            url=f"{reverse('adminaccount-list')}?role=organizer",
        )

    def test_create(self):
        create_view = AdminAccountViewSet.as_view({"post": "create"})

        self.check_view_status(create_view, self.super_admin1, 400, "post")
        self.check_view_status(
            create_view,
            self.super_admin1,
            400,
            "post",
            data={
                "email": "test@chatme.ai",
                "role": AdminAccount.ORGANIZER,
                "new_password": "secret",
                "new_password_confirmation": "secret2",
            },
        )
        self.check_view_status(
            create_view,
            self.super_admin1,
            201,
            "post",
            data={
                "email": "test@chatme.ai",
                "role": AdminAccount.ORGANIZER,
                "new_password": "secret",
                "new_password_confirmation": "secret",
            },
        )

    @classmethod
    def setUpTestData(cls):
        cls.super_admin1 = AdminAccount.objects.create_user(
            email="super_admin1@chatme.ai", role=AdminAccount.SUPER_ADMIN
        )
        cls.super_admin2 = AdminAccount.objects.create_user(
            email="super_admin2@chatme.ai", role=AdminAccount.SUPER_ADMIN
        )
        cls.organizer1 = AdminAccount.objects.create_user(
            email="organizer1@chatme.ai", role=AdminAccount.ORGANIZER
        )
        cls.location_owner1 = AdminAccount.objects.create_user(
            email="location_owner1@chatme.ai", role=AdminAccount.LOCATION_OWNER
        )

        cls.all_admin_accounts = {
            cls.super_admin1,
            cls.super_admin2,
            cls.organizer1,
            cls.location_owner1,
        }
        cls.super_admins = {cls.super_admin1, cls.super_admin2}
        cls.organizers = {cls.organizer1}
