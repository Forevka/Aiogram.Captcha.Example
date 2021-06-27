from datetime import datetime
import hashlib
from secrets import token_urlsafe


def calculate_hash(private_key: str, public_key: str,) -> str:
    m = hashlib.sha256()
    m.update(private_key.encode('utf-8'))
    m.update(public_key.encode('utf-8'))

    return m.digest().hex()


def verify_hash(private_key: str, public_key: str, our_hash: str) -> bool:
    return calculate_hash(private_key, public_key,) == our_hash

def generate_user_secret() -> dict:
    user_private_key = token_urlsafe(16)
    user_public_key = token_urlsafe(16)

    return {
        'private_key': user_private_key,
        'public_key': user_public_key,
        'hash_key': calculate_hash(user_private_key, user_public_key),
        'generated_time': datetime.utcnow().timestamp(),
        'passed_time': 0,
    }