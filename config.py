from os import getenv
from aiogram.types.chat_permissions import ChatPermissions
from enum import Enum

POEDITOR_ID = int(getenv("POEDITOR_PROJECT_ID", 0))
POEDITOR_TOKEN = getenv("POEDITOR_TOKEN", "")

TOKEN = getenv("TOKEN", "")
ENVIRONMENT = getenv("ENVIRONMENT", "debug")

RECAPTCHA_PUBLIC_KEY = getenv(
    "RECAPTCHA_PUBLIC_KEY", "6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI"
)
RECAPTCHA_PRIVATE_KEY = getenv(
    "RECAPTCHA_PRIVATE_KEY", "6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe"
)

HCAPTCHA_PUBLIC_KEY = getenv("HCAPTCHA_PUBLIC_KEY", "")
HCAPTCHA_PRIVATE_KEY = getenv("HCAPTCHA_PRIVATE_KEY", "")

HOST = getenv("HOST", "")
RECAPTCHA_ROUTE = getenv("RECAPTCHA_ROUTE", "")
HCAPTCHA_ROUTE = getenv("HCAPTCHA_ROUTE", "")
ANGLE_ROUTE = getenv("ANGLE_ROUTE", "")
PROXY_PREFIX = getenv("PROXY_PREFIX", "")

REDIS_HOST = getenv("REDIS_HOST", "redis")
CONNECTION_STRING = getenv("CONNECTION_STRING", "")

INVALIDATE_STATE_MINUTES = 1


def is_debug() -> bool:
    return ENVIRONMENT == "debug"


RESTRICT_ALL = ChatPermissions(
    can_send_messages=False,
    can_send_media_messages=False,
    can_send_polls=False,
    can_send_other_messages=False,
    can_add_web_page_previews=False,
    can_change_info=False,
    can_invite_users=False,
    can_pin_messages=False,
)

UNRESTRICT_ALL = ChatPermissions(
    can_send_messages=True,
    can_send_media_messages=True,
    can_send_polls=True,
    can_send_other_messages=True,
    can_add_web_page_previews=True,
    can_change_info=True,
    can_invite_users=True,
    can_pin_messages=True,
)


class Lang(Enum):
    en = 1
    ru = 2


DEFAULT_LANG = Lang.en

all_language_codes = [item.name for item in Lang]

language_map = {
    "ru": "Русский",
    "en": "English",
}


class CaptchaType(Enum):
    Re = 1
    H = 2
    Angle = 3


class MessageType(Enum):
    Welcome = 1
    Captcha = 2
