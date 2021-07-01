import datetime
from asyncio import gather
from contextlib import suppress
from itertools import chain
from web.utils.cleanup_chat_after_validation import cleanup_chat_after_validation
from web.models.angle_validation_model import AngleValidationModel

from fastapi import Depends, Request
from starlette.responses import JSONResponse, Response

from config import (
    UNRESTRICT_ALL,
)
from aiogram.utils.exceptions.base import TelegramAPIError
from web.dependency_resolvers.aiogram_bot_to_fastapi import AiogramBot
from web.dependency_resolvers.aiogram_fsm_context_to_fastapi import AiogramFSMContext
from utils.security import verify_hash



async def validate_angle_page(
    request: Request,
    validation_model: AngleValidationModel,
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

    user_secret_data["passed_time"] = datetime.datetime.utcnow().timestamp()

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
