import typing

from lib.telegram.textutils import escape_markdown

if typing.TYPE_CHECKING:
    from .models import Ticket, TicketCategory


def render_ticket_category_card(ticket_category: "TicketCategory"):
    return (
        f"*{escape_markdown(ticket_category.name)}*\n"
        f"Цена: {escape_markdown(ticket_category.get_base_price_label())}\n"
        f"{ticket_category.render_description()}"
    )


def render_ticket_info(ticket: "Ticket", access_control=False):
    if access_control:
        selfie = ticket.selfies.first()
    else:
        selfie = None

    return (
        f"*Билет \\#{ticket.id}*\n"
        f"Мероприятие: {escape_markdown(ticket.category.event.name)}\n"
        f"Категория: {escape_markdown(ticket.category.name)}\n"
        f"Цена при покупке: {escape_markdown(ticket.get_purchase_price_label())}\n"
        f"Статус: {escape_markdown(ticket.get_status_display())}\n"
    ) + (
        (
            "\n\n*Комментарий администратора:*"
            f"\n{escape_markdown(selfie.admin_comment)}"
        )
        if access_control and selfie and selfie.admin_comment
        else ""
    )
