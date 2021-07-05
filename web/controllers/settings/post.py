from config import CAPTCHA_ID_TO_NAME
import datetime
from web.models.settings_model import SettingsModel

from bs4 import BeautifulSoup

from fastapi import Depends, Request
from starlette.responses import JSONResponse, Response

from web.dependency_resolvers.aiogram_bot_to_fastapi import AiogramBot
from web.dependency_resolvers.aiogram_fsm_context_to_fastapi import UserRepoResolver
import html
from utils.security import generate_user_secret, verify_hash

VALID_TAGS = ['b', 'i', 'u', 's']

def sanitize_html(value):
    soup = BeautifulSoup(value, features="html.parser")

    for tag in soup.findAll(True):
        if tag.name not in VALID_TAGS:
            tag.extract()

    return soup.encode_contents(encoding="utf-8")

async def settings_post(
    request: Request,
    settings_model: SettingsModel,
    storage: UserRepoResolver = Depends(UserRepoResolver),
    bot: AiogramBot = Depends(AiogramBot),
) -> Response:
    pre = settings_model.welcome_message.replace('</div>', '')
    pre = pre.replace('<br>', '')
    pre = pre.replace('<div>', '\n')

    valid_welcome_msg = str(sanitize_html(html.unescape(pre)), encoding="utf-8")
    if (not valid_welcome_msg):
        return JSONResponse(
            status_code=406,
            content={
                "detail": "Message must be not null",
            },
        )

    if settings_model.captcha_type not in CAPTCHA_ID_TO_NAME:
        return JSONResponse(
            status_code=406,
            content={
                "detail": "Captcha type must be valid value",
            },
        )

    
    user_secret_data = await storage.user_repo.get_security(settings_model.user_id)

    if not user_secret_data or not all(
        [
            user_secret_data,
            verify_hash(
                user_secret_data.PrivateKey,
                settings_model.public_key,
                user_secret_data.PublicKey,
            ),
        ],
    ):
        return JSONResponse(
            status_code=403,
            content={
                "detail": "Reopen this page through bot.",
            },
        )
    
    new_user_secret_data = generate_user_secret()

    await storage.user_repo.update_security(settings_model.user_id, new_user_secret_data['public_key'], new_user_secret_data['private_key'], datetime.datetime.now())

    await storage.chat_setting_repo.update(settings_model.chat_id, valid_welcome_msg, settings_model.captcha_type, settings_model.user_id)

    return JSONResponse(  # everything is ok
        status_code=200,
        content={
            "detail": "ok",
            "publicKey": new_user_secret_data['public_key'],
        },
    )
