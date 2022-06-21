import json

from apps.bots.models import Bot
from apps.events.models import Event
from apps.tickets.models import Ticket, TicketCategory
from apps.tickets.renderers import render_ticket_category_card
from lib.telegram import IncomingData
from lib.telegram.datatypes import ParseMode


def _display_ticket_category_with_action(
    bot: Bot,
    incoming_data: IncomingData,
    ticket_category: TicketCategory,
    action_text: str,
):
    bot.client.send_message(
        incoming_data.from_id,
        render_ticket_category_card(ticket_category),
        inline_keyboard=[
            [
                {
                    "text": action_text,
                    "callback_data": (f"buy_tickets:for_category|{ticket_category.id}"),
                }
            ],
        ],
        parse_mode=ParseMode.MARKDOWN_V2,
    )


def _display_ticket_category(
    bot: Bot, incoming_data: IncomingData, ticket_category: TicketCategory
):
    if ticket_category.is_free() or ticket_category.with_manual_confirmation:
        if ticket_category.is_free():
            _display_ticket_category_with_action(
                bot, incoming_data, ticket_category, "Получить билет"
            )
        elif ticket_category.selfie_required:
            if ticket_category.avoid_selfie_reconfirmation:
                _display_ticket_category_with_action(
                    bot, incoming_data, ticket_category, "Получить билет"
                )
            else:
                _display_ticket_category_with_action(
                    bot, incoming_data, ticket_category, "Загрузить селфи"
                )
        else:
            _display_ticket_category_with_action(
                bot, incoming_data, ticket_category, "Отправить скрин подтверждения"
            )

    else:
        if ticket_category.selfie_required:
            if ticket_category.avoid_selfie_reconfirmation:
                _display_ticket_category_with_action(
                    bot, incoming_data, ticket_category, "Получить билет"
                )
            else:
                _display_ticket_category_with_action(
                    bot, incoming_data, ticket_category, "Загрузить селфи"
                )
        else:
            if ticket_category.with_auto_confirmation():
                if ticket_category.event.payment_type == Event.YOOMONEY_TELEGRAM:
                    ticket_category.send_telegram_yoomoney_invoice(
                        incoming_data.from_id
                    )
                elif ticket_category.event.payment_type in (
                    Event.FONDY,
                    Event.YOOMONEY,
                ):
                    _display_ticket_category_with_action(
                        bot, incoming_data, ticket_category, "Купить билет"
                    )


def _display_event(
    bot: Bot, incoming_data: IncomingData, event: Event, display_actions: bool = True
):
    poster_file = event.get_poster_file_or_file_id()

    brief_info = event.get_brief_info()

    if display_actions:
        inline_keyboard = [
            [{"text": "Билеты", "callback_data": f"buy_tickets|{event.id}"}]
        ]
    else:
        inline_keyboard = None

    if poster_file:
        if display_actions:
            reply_markup = json.dumps({"inline_keyboard": inline_keyboard})
        else:
            reply_markup = None

        if not event.poster_is_video():
            response = bot.client.send_image(
                incoming_data.from_id,
                poster_file,
                caption=brief_info,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            json_data = response.json()
            new_telegram_poster_id = json_data["result"]["photo"][-1]["file_id"]
        else:
            response = bot.client.send_video(
                incoming_data.from_id,
                poster_file,
                caption=brief_info,
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN_V2,
            )

            json_data = response.json()
            new_telegram_poster_id = json_data["result"]["video"]["file_id"]

        event.update_telegram_poster_id(new_telegram_poster_id)
    else:
        bot.client.send_message(
            incoming_data.from_id,
            brief_info,
            inline_keyboard=inline_keyboard,
            parse_mode=ParseMode.MARKDOWN_V2,
        )


def _check_ticket_category_availability(bot, incoming_data, ticket_category):
    if ticket_category.available_ticket_count <= 0:
        bot.client.send_message(
            incoming_data.from_id, "Билеты в данной категории закончились.",
        )
        return False
    return True


def _check_event_availability(bot, incoming_data, event):
    if not event.is_available():
        bot.client.send_message(incoming_data.from_id, "Мероприятие недоступно.")
        return False
    return True


def _check_participant_ticket_limit(bot, incoming_data, participant, ticket_category):
    participant_tickets_for_this_event = Ticket.objects.filter(
        participant=participant, category=ticket_category
    ).filter(status=Ticket.PAYED)

    if (
        participant_tickets_for_this_event.count()
        >= ticket_category.per_participant_limit
    ):
        bot.client.send_message(
            incoming_data.from_id,
            "Вы исчерпали лимит покупки билетов данной категории.",
        )
        return False

    return True


def _check_participant_is_blocked(bot, incoming_data, participant):
    if participant.is_blocked:
        bot.client.send_message(
            incoming_data.from_id, "Вы не можете осуществлять покупку билетов."
        )
        return True
    return False
