from django.conf import settings

DATETIME_FORMAT = "%d.%m.%Y %H:%M %Z"


def format_datetime(value):
    return value.strftime(DATETIME_FORMAT)


def as_timezone(value):
    return value.astimezone(settings.EVENT_TIMEZONE)
