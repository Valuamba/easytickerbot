from django.urls import path

from . import views

app_name = "bots"

urlpatterns = [
    path("<bot_secret>/webhook", views.webhook_view, name="webhook"),
]
