from os import getenv

TOKEN = getenv('TOKEN', '')
ENVIRONMENT = getenv('ENVIRONMENT', 'debug')

RECAPTCHA_PUBLIC_KEY = getenv('RECAPTCHA_PUBLIC_KEY', '6LeIxAcTAAAAAJcZVRqyHh71UMIEGNQ_MXjiZKhI')
RECAPTCHA_PRIVATE_KEY = getenv('RECAPTCHA_PRIVATE_KEY', '6LeIxAcTAAAAAGG-vFI1TnRWxMZNFuojJ4WifJWe')

HOST = getenv('HOST', '')
CAPTCHA_ROUTE = getenv('CAPTCHA_ROUTE', '')
REDIS_HOST = getenv('REDIS_HOST', 'redis')

def is_debug() -> bool:
    return ENVIRONMENT == 'debug'