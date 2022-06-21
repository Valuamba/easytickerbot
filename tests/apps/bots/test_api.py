from apps.bots.models import Bot
from apps.bots.viewsets import BotViewSet
from apps.management.models import AdminAccount
from tests.base import BaseApiTestCase


class TestBotsApi(BaseApiTestCase):
    def test_list(self):
        list_view = BotViewSet.as_view({"get": "list"})

        self.check_entity_subset(list_view, self.super_admin, self.super_admin_bots)

        self.check_entity_subset(list_view, self.organizer1, self.organizer1_bots)
        self.check_entity_subset(list_view, self.organizer2, self.organizer2_bots)

        self.check_view_status(list_view, self.location_owner, 403)

    def test_retrieve(self):
        retrieve_view = BotViewSet.as_view({"get": "retrieve"})

        self.check_entity_access(retrieve_view, self.super_admin, self.super_admin_bots)

        self.check_entity_access(retrieve_view, self.organizer1, self.organizer1_bots)
        self.check_entity_access(
            retrieve_view, self.organizer1, self.aint_organizer1_bots, 404
        )

        self.check_entity_access(
            retrieve_view, self.location_owner, self.super_admin_bots, 403
        )

    def test_create(self):
        create_view = BotViewSet.as_view({"post": "create"})

        self.check_view_status(create_view, self.super_admin, 400, "post")
        self.check_view_status(create_view, self.organizer1, 400, "post")
        self.check_view_status(create_view, self.location_owner, 403, "post")

    def test_update(self):
        update_view = BotViewSet.as_view({"put": "update"})

        self.check_entity_access(
            update_view, self.super_admin, self.super_admin_bots, 400, "put"
        )

        self.check_entity_access(
            update_view, self.organizer1, self.organizer1_bots, 400, "put"
        )
        self.check_entity_access(
            update_view, self.organizer1, self.aint_organizer1_bots, 404, "put"
        )

        self.check_entity_access(
            update_view, self.location_owner, self.super_admin_bots, 403, "put"
        )

    def test_destroy(self):
        destroy_view = BotViewSet.as_view({"delete": "destroy"})

        self.check_entity_access_rollback(
            destroy_view, self.super_admin, self.super_admin_bots, 204, "delete"
        )

        self.check_entity_access_rollback(
            destroy_view, self.organizer1, self.organizer1_bots, 204, "delete"
        )
        self.check_entity_access_rollback(
            destroy_view, self.organizer1, self.aint_organizer1_bots, 404, "delete"
        )

        self.check_entity_access_rollback(
            destroy_view, self.location_owner, self.super_admin_bots, 403, "delete"
        )

    @classmethod
    def setUpTestData(cls):
        cls.super_admin = AdminAccount.objects.create_user(
            "super-admin@chatme.ai", role=AdminAccount.SUPER_ADMIN
        )

        cls.location_owner = AdminAccount.objects.create_user(
            "location-owner@chatme.ai", role=AdminAccount.LOCATION_OWNER
        )

        cls.organizer1 = AdminAccount.objects.create_user(
            "organizer1@chatme.ai", role=AdminAccount.ORGANIZER
        )
        cls.organizer2 = AdminAccount.objects.create_user(
            "organizer2@chatme.ai", role=AdminAccount.ORGANIZER
        )

        cls.bot1 = Bot.objects.create(
            username="Bot #1", token="top_secret_token_xxx", organizer=cls.organizer1
        )
        cls.bot2 = Bot.objects.create(
            username="Bot #2", token="very_strong_token_yyy", organizer=cls.organizer1
        )
        cls.bot3 = Bot.objects.create(
            username="Bot #3", token="awesome_token_zzz", organizer=cls.organizer2
        )

        cls.super_admin_bots = {cls.bot1, cls.bot2, cls.bot3}
        cls.organizer1_bots = {cls.bot1, cls.bot2}
        cls.aint_organizer1_bots = cls.super_admin_bots - cls.organizer1_bots
        cls.organizer2_bots = {cls.bot3}
