from apps.locations.models import Location
from apps.locations.viewsets import LocationViewSet
from apps.management.models import AdminAccount
from tests.base import BaseApiTestCase


class TestLocationsApi(BaseApiTestCase):
    def test_list(self):
        list_view = LocationViewSet.as_view({"get": "list"})

        self.check_entity_subset(
            list_view, self.super_admin, self.super_admin_locations
        )

        self.check_entity_subset(
            list_view, self.location_owner1, self.location_owner1_locations
        )
        self.check_entity_subset(
            list_view, self.location_owner2, self.location_owner2_locations
        )

        self.check_entity_subset(list_view, self.organizer1, self.organizer1_locations)
        self.check_entity_subset(list_view, self.organizer2, self.organizer2_locations)

    def test_retrieve(self):
        retrieve_view = LocationViewSet.as_view({"get": "retrieve"})

        # Test super_admin access
        self.check_entity_access(
            retrieve_view, self.super_admin, self.super_admin_locations
        )

        # Test location owner access
        self.check_entity_access(
            retrieve_view, self.location_owner1, self.location_owner1_locations
        )
        self.check_entity_access(
            retrieve_view, self.location_owner1, self.location_owner2_locations, 404
        )

        # Test organizer access
        self.check_entity_access(
            retrieve_view, self.organizer1, self.organizer1_locations
        )
        self.check_entity_access(
            retrieve_view,
            self.organizer1,
            (self.super_admin_locations - self.organizer1_locations),
            404,
        )

    def test_create(self):
        create_view = LocationViewSet.as_view({"post": "create"})

        self.check_view_status(create_view, self.super_admin, 400, "post")
        self.check_view_status(create_view, self.location_owner1, 400, "post")
        self.check_view_status(create_view, self.organizer1, 403, "post")

    def test_update(self):
        update_view = LocationViewSet.as_view({"put": "update"})

        self.check_entity_access(
            update_view, self.super_admin, self.super_admin_locations, 400, method="put"
        )

        self.check_entity_access(
            update_view,
            self.location_owner1,
            self.location_owner1_locations,
            400,
            method="put",
        )
        self.check_entity_access(
            update_view,
            self.location_owner1,
            self.location_owner2_locations,
            404,
            method="put",
        )

        self.check_entity_access(
            update_view, self.organizer1, self.organizer1_locations, 403, method="put"
        )
        self.check_entity_access(
            update_view,
            self.organizer1,
            (self.super_admin_locations - self.organizer1_locations),
            404,
            method="put",
        )

    def test_destroy(self):
        destroy_view = LocationViewSet.as_view({"delete": "destroy"})

        self.check_entity_access_rollback(
            destroy_view,
            self.super_admin,
            self.super_admin_locations,
            204,
            method="delete",
        )

        self.check_entity_access_rollback(
            destroy_view,
            self.location_owner1,
            self.location_owner1_locations,
            204,
            method="delete",
        )

        self.check_entity_access_rollback(
            destroy_view,
            self.location_owner1,
            self.location_owner2_locations,
            404,
            method="delete",
        )

        self.check_entity_access_rollback(
            destroy_view,
            self.organizer1,
            self.organizer1_locations,
            403,
            method="delete",
        )
        self.check_entity_access_rollback(
            destroy_view,
            self.organizer1,
            (self.super_admin_locations - self.organizer1_locations),
            404,
            method="delete",
        )

    @classmethod
    def setUpTestData(cls):
        cls.super_admin = AdminAccount.objects.create_user(
            "super-admin@chatme.ai", role=AdminAccount.SUPER_ADMIN
        )

        cls.location_owner1 = AdminAccount.objects.create_user(
            "location-owner1@chatme.ai", role=AdminAccount.LOCATION_OWNER
        )
        cls.location_owner2 = AdminAccount.objects.create_user(
            "location-owner2@chatme.ai", role=AdminAccount.LOCATION_OWNER
        )
        cls.organizer1 = AdminAccount.objects.create_user(
            "organizer1@chatme.ai", role=AdminAccount.ORGANIZER
        )
        cls.organizer2 = AdminAccount.objects.create_user(
            "organizer2@chatme.ai", role=AdminAccount.ORGANIZER
        )

        cls.location1 = Location.objects.create(
            name="Location #1", location_owner=cls.location_owner1,
        )

        cls.location2 = Location.objects.create(
            name="Location #2", location_owner=cls.location_owner2
        )
        cls.location2.organizers.add(cls.organizer1)

        cls.location3 = Location.objects.create(
            name="Location #3", location_owner=cls.location_owner2
        )

        cls.super_admin_locations = {cls.location1, cls.location2, cls.location3}
        cls.location_owner1_locations = {cls.location1}
        cls.location_owner2_locations = {cls.location2, cls.location3}
        cls.organizer1_locations = {cls.location2}
        cls.organizer2_locations = {}
