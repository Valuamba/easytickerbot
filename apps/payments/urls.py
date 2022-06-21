from django.urls import path

from . import views

app_name = "payments"

urlpatterns = [
    path("fondy_webhook", views.fondy_payment_webhook, name="fondy_webhook"),
]
