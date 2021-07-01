import datetime
from asyncio import gather
from contextlib import suppress
from itertools import chain
from third_party.captcha.client import CaptchaClient

from yarl import URL
from web.utils.cleanup_chat_after_validation import cleanup_chat_after_validation

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


async def validate_recaptcha_page(
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

    async with CaptchaClient(URL("https://www.google.com/recaptcha/api/")) as client:
        result = await client.validate_token(validation_model.token, RECAPTCHA_PRIVATE_KEY)
        if (result):
            if (result.success):
                user_secret_data[
                    "passed_time"
                ] = datetime.datetime.utcnow().timestamp()

                user_data["secret"] = user_secret_data

                await cleanup_chat_after_validation(bot.bot, validation_model.user_id, user_data.get('chats', {}))

                await storage.user_context.set_data(data=user_data)

                return JSONResponse(  # everything is ok
                    status_code=200,
                    content={
                        "detail": "Now you can close this tab. Or it will close in: {0}",
                        "redirectTo": bot.bot_link,
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
