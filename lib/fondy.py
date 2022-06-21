import hashlib
import logging
from typing import Optional

import requests

from lib.payment import get_integer_big_payment_amount

logger = logging.getLogger(__name__)


def get_fondy_signature(parameters: dict, merchant_password: str) -> str:
    base_string = "|".join(
        [merchant_password]
        + [
            str(v)
            for k, v in sorted(parameters.items())
            if v and k not in ("signature", "response_signature_string")
        ]
    )
    return hashlib.sha1(base_string.encode("utf-8")).hexdigest()


def call_fondy_api(target_url, merchant_password, parameters):
    signature = get_fondy_signature(parameters, merchant_password)

    json_data = {
        "request": {**parameters, "signature": signature},
    }

    logger.debug(f"Request: url={target_url} data={json_data}")

    response = requests.post(target_url, json=json_data)

    try:
        logger.debug(f"Response: status={response.status_code} data={response.json()}")
    except Exception as e:
        logger.exception(e)

    try:
        response.raise_for_status()
    except Exception as e:
        return logger.exception(e)

    return response


def get_fondy_checkout_url(
    server_callback_url: str,
    order_id: str,
    order_desc: str,
    amount: int,
    merchant_id: int,
    merchant_password: str,
) -> Optional[str]:
    base_parameters = {
        "server_callback_url": server_callback_url,
        "order_id": order_id,
        "currency": "RUB",
        "merchant_id": merchant_id,
        "order_desc": order_desc,
        "amount": amount,
    }

    response = call_fondy_api(
        "https://pay.fondy.eu/api/checkout/url", merchant_password, base_parameters
    )

    try:
        response_json = response.json()
    except Exception as e:
        return logger.exception(e)

    try:
        return response_json["response"]["checkout_url"]
    except KeyError:
        return logger.error("Unable to extract checkout URL.")


def make_fondy_refund(
    order_id: str, amount: float, merchant_id: int, merchant_password: str,
):
    base_parameters = {
        "order_id": order_id,
        "currency": "RUB",
        "merchant_id": merchant_id,
        "amount": get_integer_big_payment_amount(amount),
    }

    response = call_fondy_api(
        "https://pay.fondy.eu/api/reverse/order_id", merchant_password, base_parameters
    )

    try:
        response.raise_for_status()
    except Exception:
        return logger.error("Unable to make Fondy API refund.", exc_info=True)

    try:
        if response.json()["response"].get("response_status") == "failure":
            return False
    except KeyError:
        return False

    return True
