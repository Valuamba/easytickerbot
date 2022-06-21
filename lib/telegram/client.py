import logging
import tempfile
from io import BufferedIOBase
from typing import Optional

import requests

logger = logging.getLogger(__name__)


class TelegramClient:
    def __init__(self, token, api_origin):
        self.api_origin = api_origin
        self.token = token

    def check_token(self) -> Optional[dict]:
        try:
            response = self.call_api("getMe")
            response.raise_for_status()
            json_data = response.json()
            return json_data
        except requests.RequestException as e:
            if (e.response is not None) and (e.response.status_code == 401):
                return None
            raise e

    def set_webhook(self, webhook_url):
        response = self.call_api("setWebhook", {"url": webhook_url})
        response.raise_for_status()
        return response

    def call_api(
        self, method_name: str, payload=None, files=None, params=None, data=None
    ):
        target_url = f"{self.api_origin}/bot{self.token}/{method_name}"

        logger.debug(
            f"Calling Telegram API: method_name={method_name} payload={payload}"
        )

        response = requests.post(
            target_url, json=payload, files=files, params=params, data=data
        )

        try:
            logger.debug(
                f"Response: status={response.status_code} data={response.json()}"
            )
        except Exception as e:
            logger.exception(e)

        try:
            response.raise_for_status()
        except Exception as e:
            logger.exception(e)

        return response

    def send_message(self, chat_id, text, inline_keyboard=None, **extras):
        if inline_keyboard:
            extra_data = {
                "reply_markup": {"inline_keyboard": inline_keyboard},
                **extras,
            }
        else:
            extra_data = {**extras}

        self.call_api("sendMessage", {"chat_id": chat_id, "text": text, **extra_data})

    def send_image(self, chat_id, file, **extras):
        if isinstance(file, str):
            data = {"photo": file, **extras}
            files = None
        else:
            files = {"photo": file}
            data = {**extras}

        return self.call_api(
            "sendPhoto", params={"chat_id": chat_id}, data=data, files=files,
        )

    def send_video(self, chat_id, file, **extras):
        if isinstance(file, str):
            data = {"video": file, **extras}
            files = None
        else:
            files = {"video": file}
            data = {**extras}

        return self.call_api(
            "sendVideo", params={"chat_id": chat_id}, data=data, files=files,
        )

    def download_file(self, file_id: str) -> BufferedIOBase:
        get_file_response = self.call_api("getFile", {"file_id": file_id})
        get_file_response.raise_for_status()

        response_data = get_file_response.json()

        file_path = response_data["result"]["file_path"]
        file_url = f"{self.api_origin}/file/bot{self.token}/{file_path}"

        download_file_response = requests.get(file_url)
        download_file_response.raise_for_status()

        downloaded_file: BufferedIOBase = tempfile.TemporaryFile()
        downloaded_file.write(download_file_response.content)

        return downloaded_file
