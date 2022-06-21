import logging
from typing import Optional

import requests

from lib.payment import get_float_payment_amount

logger = logging.getLogger(__name__)


def call_kassa_api(
    method_name,
    json_data=None,
    username=None,
    password=None,
    idempotence_key=None,
    http_method="POST",
):
    response = requests.request(
        http_method,
        f"https://api.yookassa.ru/v3/{method_name}",
        json=json_data,
        auth=(username, password),
        headers=({"Idempotence-Key": idempotence_key} if idempotence_key else {}),
    )

    try:
        logger.info(f"Response: status={response.status_code} data={response.json()}")
    except Exception as e:
        logger.exception(e)

    try:
        response.raise_for_status()
    except Exception as e:
        logger.exception(e)

    return response


def make_api_refund(
    payment_id: str, amount: float, username, password, idempotence_key: str
):
    response = call_kassa_api(
        "refunds",
        {
            "amount": {"value": get_float_payment_amount(amount), "currency": "RUB"},
            "payment_id": payment_id,
        },
        username=username,
        password=password,
        idempotence_key=idempotence_key,
    )

    try:
        json_data = response.json()
    except Exception as e:
        return logger.exception(e)

    if json_data.get("status") == "succeeded":
        return True

    logger.error("Unable to make successful refund.")


def get_yoomoney_checkout_data(
    amount: int,
    order_id: str,
    order_desc: str,
    username: str,
    password: str,
    return_url: str,
):
    response = call_kassa_api(
        "payments",
        {
            "amount": {"value": get_float_payment_amount(amount), "currency": "RUB"},
            "description": order_desc,
            "capture": True,
            "metadata": {"order_id": order_id},
            "confirmation": {"type": "redirect", "return_url": return_url},
        },
        username=username,
        password=password,
        idempotence_key=order_id,
    )

    try:
        response_data = response.json()
    except Exception as e:
        return logger.exception(e)

    try:
        payment_id = response_data["id"]
        checkout_url = response_data["confirmation"]["confirmation_url"]
    except KeyError:
        return logger.error("Unable to extract some of response data.", exc_info=True)

    if not payment_id:
        return logger.error("Empty payment ID.")

    if not checkout_url:
        return logger.error("Empty checkout URL.")

    return {
        "payment_id": payment_id,
        "checkout_url": checkout_url,
    }


def check_yoomoney_payment(
    payment_id: str, username: str, password: str
) -> Optional[bool]:
    response = call_kassa_api(
        f"payments/{payment_id}",
        http_method="GET",
        username=username,
        password=password,
    )
    try:
        response_data = response.json()
    except Exception as e:
        return logger.exception(e)

    try:
        payment_status = response_data["status"]
    except KeyError as e:
        return logger.exception(e)

    if payment_status == "canceled":
        return False

    if payment_status == "succeeded":
        return True
