import json

from django.db import transaction
from django.test import TestCase
from rest_framework.test import APIRequestFactory, force_authenticate


class BaseApiTestCase(TestCase):
    def setUp(self) -> None:
        self.factory = APIRequestFactory()

    def contact_view(
        self,
        view,
        user=None,
        url="",
        method="get",
        view_args=None,
        view_kwargs=None,
        data=None,
    ):
        request = getattr(self.factory, method)(url, data=data, format="json")
        if user:
            force_authenticate(request, user=user)
        response = view(request, *(view_args or []), **(view_kwargs or {}))
        return response

    def check_view_status(
        self, view, user, expected_status_code=200, method="get", url="", data=None
    ):
        response = self.contact_view(view, user, method=method, url=url, data=data)
        self.assertEqual(response.status_code, expected_status_code)
        return response

    def check_entity_access(
        self, view, user, entities, expected_status_code=200, method="get"
    ):
        for entity in entities:
            response = self.contact_view(
                view, user, view_kwargs={"pk": entity.id}, method=method
            )
            self.assertEqual(response.status_code, expected_status_code)

    def check_entity_access_rollback(
        self, view, user, entities, expected_status_code=200, method="get"
    ):
        with transaction.atomic():
            self.check_entity_access(view, user, entities, expected_status_code, method)
            transaction.set_rollback(True)

    def check_entity_subset(self, view, user, expected_entity_subset, url=""):
        response = self.check_view_status(view, user, url=url)
        response_data = self.get_response_data(response)
        self.assertEqual(
            {item["id"] for item in response_data},
            {item.id for item in expected_entity_subset},
        )

    @staticmethod
    def get_response_data(response):
        response.render()
        return json.loads(response.content)["results"]
