import datetime

from yarl import URL
from third_party.captcha.client import CaptchaClient
from web.utils.cleanup_chat_after_validation import cleanup_chat_after_validation

from fastapi import Depends, Request
from starlette.responses import JSONResponse, Response

from config import (
    HCAPTCHA_PRIVATE_KEY,
    MessageType,
)
from web.dependency_resolvers.aiogram_bot_to_fastapi import AiogramBot
from web.dependency_resolvers.aiogram_fsm_context_to_fastapi import UserRepoResolver
from web.models.recaptcha_validation_model import RecaptchaValidationModel
from utils.security import verify_hash


async def validate_hcaptcha_page(
    request: Request,
    validation_model: RecaptchaValidationModel,
    storage: UserRepoResolver = Depends(UserRepoResolver),
    bot: AiogramBot = Depends(AiogramBot),
) -> Response:
    user_secret_data = await storage.user_repo.get_security(validation_model.user_id)

    if not all(
        [
            user_secret_data,
            verify_hash(
                user_secret_data.PrivateKey,
                validation_model.public_key,
                user_secret_data.PublicKey,
            ),
        ],
    ):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Can't verify your attempt. Probably you are bot :)",
            },
        )

    async with CaptchaClient(URL("https://hcaptcha.com/")) as client:
        result = await client.validate_token(validation_model.token, HCAPTCHA_PRIVATE_KEY)
        if (result):
            if (result.success):
                chats = await storage.user_repo.get_chat_messages(
                    validation_model.user_id, 
                    False,
                    [MessageType.Welcome.value, MessageType.Captcha.value, MessageType.UserJoinServiceMessage.value,],
                )
                await cleanup_chat_after_validation(bot.bot, validation_model.user_id, chats)
                await storage.user_repo.cleanup_messages(validation_model.user_id,)

                await storage.user_repo.update_security(
                    validation_model.user_id, 
                    user_secret_data.PublicKey, 
                    user_secret_data.PrivateKey, 
                    datetime.datetime.utcnow(),
                )

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

            
