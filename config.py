from os import getenv
from aiogram.types.chat_permissions import ChatPermissions

TOKEN = getenv('TOKEN', '')
ENVIRONMENT = getenv('ENVIRONMENT', 'debug')

RECAPTCHA_PUBLIC_KEY = getenv('RECAPTCHA_PUBLIC_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
RECAPTCHA_PRIVATE_KEY = getenv('RECAPTCHA_PRIVATE_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')

HOST = getenv('HOST', '')
CAPTCHA_ROUTE = getenv('CAPTCHA_ROUTE', '')
PROXY_PREFIX = getenv('PROXY_PREFIX', '')

REDIS_HOST = getenv('REDIS_HOST', 'redis')

INVALIDATE_STATE_MINUTES = 1

def is_debug() -> bool:
    return ENVIRONMENT == 'debug'

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