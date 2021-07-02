from typing import Optional
from database.models.user_security import UserSecurity
import hashlib
from datetime import datetime, timedelta
from secrets import token_urlsafe
from urllib.parse import quote

from config import HOST, INVALIDATE_STATE_MINUTES, PROXY_PREFIX


def calculate_hash(
    private_key: str,
    public_key: str,
) -> str:
    m = hashlib.sha256()
    m.update(private_key.encode("utf-8"))
    m.update(public_key.encode("utf-8"))

    return m.digest().hex()


def verify_hash(private_key: str, user_public_key: str, our_public_key: str) -> bool:
    return calculate_hash(private_key, user_public_key,) == calculate_hash(
        private_key,
        our_public_key,
    )


def generate_user_secret() -> dict:
    user_private_key = token_urlsafe(16)
    user_public_key = token_urlsafe(16)

    return {
        "private_key": user_private_key,
        "public_key": user_public_key,
        "hash_key": calculate_hash(user_private_key, user_public_key),
        "generated_time": datetime.utcnow().timestamp(),
        "passed_time": 0,
    }


def is_need_to_pass_captcha(user_data: Optional[UserSecurity]):
    if not user_data or not user_data.PassedDateTime:
        return True

    return datetime.utcnow() > (
        user_data.PassedDateTime + timedelta(minutes=INVALIDATE_STATE_MINUTES)
    )


def generate_game_url(route: str, user_id: int, first_name: str, public_key: str):
    return f"{HOST}{PROXY_PREFIX}{route}?user_id={user_id}&first_name={quote(first_name)}&public_key={public_key}"
