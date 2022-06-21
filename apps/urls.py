from django.contrib import admin
from django.urls import include, path

import apps.bots.urls
import apps.events.urls
import apps.fileuploads.urls
import apps.management.urls
import apps.payments.urls


def trigger_error(request):
    1 / 0


urlpatterns = [
    path("", include(apps.management.urls)),
    path("fileuploads/", include(apps.fileuploads.urls)),
    path("events/", include(apps.events.urls)),
    path("bots/", include(apps.bots.urls)),
    path("admin/", admin.site.urls),
    path("payments/", include(apps.payments.urls)),
    path("sentry-debug/", trigger_error),
]
