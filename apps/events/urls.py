from django.urls import path
from .views import MakeRefundForUnusedTicketsView, SendEventPassesView

app_name = "events"

urlpatterns = [
    path("send-event-passes/<id>", SendEventPassesView.as_view()),
    path(
        "make-refund-for-unused-tickets/<id>", MakeRefundForUnusedTicketsView.as_view()
    ),
]
