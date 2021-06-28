import datetime
from asyncio import gather
from contextlib import suppress
from itertools import chain

import aiohttp
from aiogram.types import ChatPermissions
from aiogram.utils.exceptions.base import TelegramAPIError
from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse, Response

from config import (ENVIRONMENT, INVALIDATE_STATE_MINUTES,
                    RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY, TOKEN,
                    is_debug)
from dependency_resolvers.aiogram_bot_to_fastapi import AiogramBot
from dependency_resolvers.aiogram_fsm_context_to_fastapi import \
    AiogramFSMContext
from middleware.web.bot_provider import BotProviderMiddleware
from middleware.web.captcha_storage_provider import \
    CaptchaStorageProviderMiddleware
from models import RecaptchaSiteverifyModel, RecaptchaValidationModel
from utils import generate_user_secret, verify_hash


async def get_captcha_page(request: Request, user_id: int, first_name: str, public_key: str = '', storage: AiogramFSMContext = Depends(AiogramFSMContext)) -> Response:
    user_data = await storage.user_context.get_data()
    user_secret_data = user_data.get('secret', {})

    passed_at = user_secret_data.get('passed_time', 0)

    if (passed_at > 1):
        pass_again = datetime.datetime.fromtimestamp(passed_at) + datetime.timedelta(minutes=INVALIDATE_STATE_MINUTES)
        if (datetime.datetime.utcnow() > pass_again):
            user_secret_data = generate_user_secret()
            user_data['secret'] = user_secret_data

            await storage.user_context.set_data(user_data)
        else:
            return templates.TemplateResponse("passed.html", {
                "request": request,
                "first_name": first_name,
                "passed_at": datetime.datetime.fromtimestamp(user_secret_data.get('passed_time')),
                "pass_again": pass_again,
                "current_utc_time": datetime.datetime.utcnow(),
            })

    if (public_key != user_secret_data['public_key']):
        return templates.TemplateResponse("wrong_origin.html", {
            "request": request,
        })


    return templates.TemplateResponse("captcha.html", {
        "request": request,
        "recaptcha_public_key": RECAPTCHA_PUBLIC_KEY,
        "first_name": first_name,
        "user_id": user_id,
        "user_public_key": user_secret_data['public_key'],
    })


async def validate_captcha_page(request: Request, validation_model: RecaptchaValidationModel, storage: AiogramFSMContext = Depends(AiogramFSMContext), bot: AiogramBot = Depends(AiogramBot)) -> Response:
    user_data = await storage.user_context.get_data()
    user_secret_data = user_data.get('secret', {})

    if not all([
        user_secret_data, verify_hash(user_secret_data['private_key'],
                                      validation_model.public_key, user_secret_data['hash_key']),
    ],):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Can't verify your attempt. Probably you are bot :)",
            }
        )

    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.google.com/recaptcha/api/siteverify', params={
            "secret": RECAPTCHA_PRIVATE_KEY,
            "response": validation_model.token,
        }) as resp:
            if (resp.status == 200):
                verify_result = RecaptchaSiteverifyModel(**await resp.json())
                if (verify_result.success):
                    user_secret_data['passed_time'] = datetime.datetime.utcnow().timestamp()

                    user_data['secret'] = user_secret_data
                    with suppress(TelegramAPIError):
                        tasks = [
                            [
                                *[
                                    bot.bot.delete_message(chat_id, msg_id) for msg_id in msg_ids
                                ], 
                                bot.bot.restrict_chat_member(chat_id, validation_model.user_id, ChatPermissions(**{
                                    "can_send_messages": True,
                                    "can_send_media_messages": True,
                                    "can_send_polls": True,
                                    "can_send_other_messages": True,
                                    "can_add_web_page_previews": True,
                                    "can_change_info": True,
                                    "can_invite_users": True,
                                    "can_pin_messages": True,
                                }))
                            ] for chat_id, msg_ids in user_data.get('chats', {}).items()
                        ]
                        flatten_tasks = list(chain(*tasks)) + [bot.bot.send_message(validation_model.user_id, 'Turing test succesfully passed')]
                        gather(*flatten_tasks)

                    await storage.user_context.set_data(data=user_data)

                    return JSONResponse(  # everything is ok
                        status_code=200,
                        content={
                            "detail": "Now you can close this tab",
                        }
                    )

                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": "Can't verify your attempt. Probably you are bot :)",
                    }
                )

            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Something went wrong. Please try later.",
                }
            )

app = FastAPI(
    root_path='' if is_debug() else '/api/captcha',
)

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    BotProviderMiddleware,
)

app.add_middleware(
    CaptchaStorageProviderMiddleware,
)


app.add_api_route(
    '/captcha',
    get_captcha_page,
    tags=['Captcha'],
    methods=['GET'],
    response_class=HTMLResponse,
)

app.add_api_route(
    '/captcha',
    validate_captcha_page,
    tags=['Captcha'],
    methods=['POST'],
)
