import json
import logging

from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from apps.tickets.models import Ticket
from lib.fondy import get_fondy_signature

logger = logging.getLogger(__name__)


@csrf_exempt
def fondy_payment_webhook(request):
    # TODO: verify signature
    try:
        incoming_data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        logger.error("Invalid JSON input for Fondy webhook.", exc_info=True)
        return HttpResponse(status=400)

    signature = incoming_data.get("signature")
    order_id = incoming_data.get("order_id")
    payment_id = incoming_data.get("payment_id")

    if not signature or not order_id or not payment_id:
        logger.error(
            (
                "One of required data unavailable: "
                f"signature={signature} order_id={order_id} payment_id={payment_id}"
            )
        )

    ticket_id = order_id.partition(":")[2]

    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        logger.error(
            (
                "No ticket with such ID found for payment "
                f"confirmation via Fondy: id={ticket_id}"
            )
        )
        return HttpResponse(status=400)

    merchant_password = (
        ticket.category.event.organizer.organizer_fondy_merchant_password
    )
    target_signature = get_fondy_signature(
        {k: v for k, v in incoming_data.items() if not k == "signature"},
        merchant_password=merchant_password,
    )

    if signature != target_signature:
        logger.error("Invalid signature.")
        return HttpResponse(status=400)

    order_status = incoming_data.get("order_status")
    if order_status == "approved":
        ticket.send_to_participant(payment_id=payment_id)

    return HttpResponse()
