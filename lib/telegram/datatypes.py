import logging
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

logger = logging.getLogger(__name__)


class ParseMode:
    MARKDOWN_V2 = "MarkdownV2"


@dataclass
class MessageDocument:
    mime_type: str
    file_name: str
    file_id: str
    file_unique_id: str
    file_size: int


@dataclass
class MessagePhoto:
    file_unique_id: str
    file_id: str
    file_size: int
    width: int
    height: int


class IncomingDataType(Enum):
    UNKNOWN = None
    MESSAGE = "message"
    CHAT_MEMBER_UPDATED = "chat_member_updated"
    CALLBACK_QUERY = "callback_query"
    PRE_CHECKOUT_QUERY = "pre_checkout_query"


@dataclass
class IncomingData:
    type: IncomingDataType

    original_data: dict

    from_id: Optional[int] = None

    # Message-related
    message_id: Optional[int] = None
    message_text: Optional[str] = None
    message_document: Optional[MessageDocument] = None
    message_photo: Optional[MessagePhoto] = None
    message_entities: Optional[List[dict]] = None

    # Callback query-related
    callback_query_id: Optional[str] = None
    callback_data: Optional[str] = None

    # Checkout related
    pre_checkout_query_id: Optional[str] = None
    pre_checkout_query: Optional[dict] = None
    successful_payment: Optional[dict] = None

    @classmethod
    def parse(cls, json_data: dict) -> "IncomingData":
        from_id = None
        message_id = None
        message_text = None
        message_document = None
        message_photo = None
        message_entities = None
        callback_query_id = None
        callback_data = None
        pre_checkout_query = None
        pre_checkout_query_id = None
        successful_payment = None

        if (message_data := json_data.get("message")) :
            from_id = message_data["from"]["id"]
            data_type = IncomingDataType.MESSAGE
            message_id = message_data["message_id"]
            message_text = message_data.get("text")
            if (document_data := message_data.get("document")) :
                message_document = MessageDocument(
                    mime_type=document_data["mime_type"],
                    file_name=document_data["file_name"],
                    file_id=document_data["file_id"],
                    file_unique_id=document_data["file_unique_id"],
                    file_size=document_data["file_size"],
                )
            if (photo_data := message_data.get("photo")) :
                top_photo = photo_data[-1]
                message_photo = MessagePhoto(
                    file_unique_id=top_photo["file_unique_id"],
                    file_id=top_photo["file_id"],
                    file_size=top_photo["file_size"],
                    width=top_photo["width"],
                    height=top_photo["height"],
                )
            if "entities" in message_data:
                message_entities = message_data["entities"]
            successful_payment = message_data.get("successful_payment")
        elif (callback_query_data := json_data.get("callback_query")) :
            from_id = callback_query_data["from"]["id"]
            data_type = IncomingDataType.CALLBACK_QUERY
            callback_query_id = callback_query_data["id"]
            callback_data = callback_query_data["data"]
        elif (pre_checkout_query := json_data.get("pre_checkout_query")) :
            print("Pre checkout")
            data_type = IncomingDataType.PRE_CHECKOUT_QUERY
            pre_checkout_query_id = pre_checkout_query["id"]
            from_id = pre_checkout_query["from"]["id"]
        elif (my_chat_member_data := json_data.get("my_chat_member")) :
            from_id = my_chat_member_data["from"]["id"]
            data_type = IncomingDataType.CHAT_MEMBER_UPDATED
        else:
            data_type = IncomingDataType.UNKNOWN
            logger.error("Unknown incoming message data type.")

        return cls(
            type=data_type,
            original_data=json_data,
            from_id=from_id,
            callback_query_id=callback_query_id,
            callback_data=callback_data,
            message_text=message_text,
            message_id=message_id,
            message_document=message_document,
            message_photo=message_photo,
            message_entities=message_entities,
            pre_checkout_query=pre_checkout_query,
            pre_checkout_query_id=pre_checkout_query_id,
            successful_payment=successful_payment,
        )
