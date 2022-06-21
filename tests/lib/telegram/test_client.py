import unittest

from lib.telegram import IncomingData
from lib.telegram.client import TelegramClient
from lib.telegram.datatypes import IncomingDataType


class TestTelegramClient(unittest.TestCase):
    def test_init(self):
        self.assertEqual(self.client.api_origin, self.telegram_api_origin)
        self.assertEqual(self.client.token, self.bot_token)

    def test_parse_incoming_data(self):
        FROM_ID = 100
        MESSAGE_ID = 27
        MESSAGE_TEXT = "Hello"
        MESSAGE_DOCUMENT_FILE_ID = (
            "BQACAgIAAxkBAANGX8JrlgSRWx9sKP-GbrKngCxLdYgAAm8IAAJPChBKU0IZNGr2okweBA"
        )
        MESSAGE_DOCUMENT_FILE_UNIQUE_ID = "AQADYelinS4AA7scAAI"
        MESSAGE_DOCUMENT_FILE_SIZE = 44988
        MESSAGE_DOCUMENT_MIME_TYPE = "image/png"
        MESSAGE_DOCUMENT_FILE_NAME = "telegram-keyboard-toggle-button-outlined-2.png"
        MESSAGE_PHOTO_FILE_UNIQUE_ID = "AQADifbVli4AAxxJBAAB"
        MESSAGE_PHOTO_FILE_SIZE = 20119
        MESSAGE_PHOTO_WIDTH = 595
        MESSAGE_PHOTO_HEIGHT = 408
        MESSAGE_PHOTO_FILE_ID = (
            "AgACAgIAAxkBAANCX8Jqa7cLSI3JMvp_Fzr03xxTf6gAAhavMRtPChBK1roTqpUwFPmJ9tWW"
            "LgADAQADAgADeAADHkkEAAEeBA"
        )

        # Text message
        incoming_data1 = IncomingData.parse(
            {
                "message": {
                    "from": {"id": FROM_ID},
                    "message_id": MESSAGE_ID,
                    "text": MESSAGE_TEXT,
                }
            }
        )
        self.assertEqual(incoming_data1.from_id, FROM_ID)
        self.assertEqual(incoming_data1.message_id, MESSAGE_ID)
        self.assertEqual(incoming_data1.message_text, MESSAGE_TEXT)
        self.assertEqual(incoming_data1.type, IncomingDataType.MESSAGE)

        # Document message
        incoming_data2 = IncomingData.parse(
            {
                "message": {
                    "from": {"id": FROM_ID},
                    "message_id": MESSAGE_ID,
                    "document": {
                        "file_name": MESSAGE_DOCUMENT_FILE_NAME,
                        "mime_type": MESSAGE_DOCUMENT_MIME_TYPE,
                        "thumb": {
                            "file_id": (
                                "AAMCAgADGQEAA0ZfwmuWBJFbH2wo_4ZusqeALEt1iAAC"
                                "bwgAAk8KEEpTQhk0avaiTGHpYp0uAAMBAAdtAAO7HAACHgQ"
                            ),
                            "file_unique_id": "AQADYelinS4AA7scAAI",
                            "file_size": 2629,
                            "width": 320,
                            "height": 44,
                        },
                        "file_id": MESSAGE_DOCUMENT_FILE_ID,
                        "file_unique_id": MESSAGE_DOCUMENT_FILE_UNIQUE_ID,
                        "file_size": MESSAGE_DOCUMENT_FILE_SIZE,
                    },
                }
            }
        )
        self.assertEqual(incoming_data2.from_id, FROM_ID)
        self.assertEqual(incoming_data2.message_id, MESSAGE_ID)
        self.assertEqual(incoming_data2.message_text, None)
        self.assertEqual(incoming_data2.type, IncomingDataType.MESSAGE)
        self.assertEqual(
            incoming_data2.message_document.file_id, MESSAGE_DOCUMENT_FILE_ID
        )
        self.assertEqual(
            incoming_data2.message_document.file_name, MESSAGE_DOCUMENT_FILE_NAME
        )
        self.assertEqual(
            incoming_data2.message_document.file_size, MESSAGE_DOCUMENT_FILE_SIZE
        )
        self.assertEqual(
            incoming_data2.message_document.file_unique_id,
            MESSAGE_DOCUMENT_FILE_UNIQUE_ID,
        )

        # Photo message
        incoming_data3 = IncomingData.parse(
            {
                "message": {
                    "from": {"id": FROM_ID},
                    "message_id": MESSAGE_ID,
                    "photo": [
                        {
                            "file_id": (
                                "AgACAgIAAxkBAANCX8Jqa7cLSI3JMvp_Fzr03xxTf6gAAhavMRtP"
                                "ChBK1roTqpUwFPmJ9tWWLgADAQADAgADbQADHEkEAAEeBA"
                            ),
                            "file_unique_id": MESSAGE_PHOTO_FILE_UNIQUE_ID,
                            "file_size": 9335,
                            "width": 320,
                            "height": 219,
                        },
                        {
                            "file_id": MESSAGE_PHOTO_FILE_ID,
                            "file_unique_id": MESSAGE_PHOTO_FILE_UNIQUE_ID,
                            "file_size": MESSAGE_PHOTO_FILE_SIZE,
                            "width": MESSAGE_PHOTO_WIDTH,
                            "height": MESSAGE_PHOTO_HEIGHT,
                        },
                    ],
                }
            }
        )
        self.assertEqual(incoming_data3.from_id, FROM_ID)
        self.assertEqual(incoming_data3.message_id, MESSAGE_ID)
        self.assertEqual(incoming_data3.message_text, None)
        self.assertEqual(incoming_data3.type, IncomingDataType.MESSAGE)
        self.assertEqual(incoming_data3.message_photo.file_id, MESSAGE_PHOTO_FILE_ID)
        self.assertEqual(
            incoming_data3.message_photo.file_unique_id, MESSAGE_PHOTO_FILE_UNIQUE_ID
        )
        self.assertEqual(
            incoming_data3.message_photo.file_size, MESSAGE_PHOTO_FILE_SIZE
        )
        self.assertEqual(incoming_data3.message_photo.width, MESSAGE_PHOTO_WIDTH)
        self.assertEqual(incoming_data3.message_photo.height, MESSAGE_PHOTO_HEIGHT)

        # Unknown data type
        incoming_data4 = IncomingData.parse({})
        self.assertEqual(incoming_data4.type, IncomingDataType.UNKNOWN)

    @classmethod
    def setUpClass(cls) -> None:
        cls.telegram_api_origin = "https://telegram-api-origin"
        cls.bot_token = "xxx_abc_secret"

        cls.client = TelegramClient(
            token=cls.bot_token, api_origin=cls.telegram_api_origin
        )
