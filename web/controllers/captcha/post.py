import datetime
from asyncio import gather
from contextlib import suppress
from itertools import chain

import aiohttp
from fastapi import Depends, Request
from starlette.responses import JSONResponse, Response

from config import (
    RECAPTCHA_PRIVATE_KEY,
    UNRESTRICT_ALL,
)
from aiogram.utils.exceptions.base import TelegramAPIError
from web.dependency_resolvers.aiogram_bot_to_fastapi import AiogramBot
from web.dependency_resolvers.aiogram_fsm_context_to_fastapi import AiogramFSMContext
from web.models.recaptcha_siteverify_model import RecaptchaSiteverifyModel
from web.models.recaptcha_validation_model import RecaptchaValidationModel
from utils.security import verify_hash


async def validate_captcha_page(
    request: Request,
    validation_model: RecaptchaValidationModel,
    storage: AiogramFSMContext = Depends(AiogramFSMContext),
    bot: AiogramBot = Depends(AiogramBot),
) -> Response:
    user_data = await storage.user_context.get_data()
    user_secret_data = user_data.get("secret", {})

    if not all(
        [
            user_secret_data,
            verify_hash(
                user_secret_data["private_key"],
                validation_model.public_key,
                user_secret_data["hash_key"],
            ),
        ],
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Can't verify your attempt. Probably you are bot :)",
            },
        )

    async with aiohttp.ClientSession() as session:
        async with session.get(
            "https://www.google.com/recaptcha/api/siteverify",
            params={
                "secret": RECAPTCHA_PRIVATE_KEY,
                "response": validation_model.token,
            },
        ) as resp:
            if resp.status == 200:
                verify_result = RecaptchaSiteverifyModel(**await resp.json())
                if verify_result.success:
                    user_secret_data[
                        "passed_time"
                    ] = datetime.datetime.utcnow().timestamp()

                    user_data["secret"] = user_secret_data
                    with suppress(TelegramAPIError):
                        tasks = [
                            [
                                *[
                                    bot.bot.delete_message(chat_id, msg_id)
                                    for msg_id in msg_ids
                                ],
                                bot.bot.restrict_chat_member(
                                    chat_id, validation_model.user_id, UNRESTRICT_ALL
                                ),
                            ]
                            for chat_id, msg_ids in user_data.get("chats", {}).items()
                        ]
                        flatten_tasks = list(chain(*tasks)) + [
                            bot.bot.send_message(
                                validation_model.user_id,
                                "Turing test succesfully passed",
                            )
                        ]
                        gather(*flatten_tasks)

                    await storage.user_context.set_data(data=user_data)

                    return JSONResponse(  # everything is ok
                        status_code=200,
                        content={
                            "detail": "Now you can close this tab",
                        },
                    )

                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": "Can't verify your attempt. Probably you are bot :)",
                    },
                )

            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Something went wrong. Please try later.",
                },
            )
