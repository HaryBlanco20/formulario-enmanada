from slowapi import Limiter
from slowapi.util import get_remote_address

from app.config import get_login_rate_limit

limiter = Limiter(key_func=get_remote_address, default_limits=[])


def login_rate_limit() -> str:
    return get_login_rate_limit()
