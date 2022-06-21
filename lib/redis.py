__all__ = [
    "redis_client",
]

from django.conf import settings
from redis import Redis

redis_client = Redis(
    host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB
)
