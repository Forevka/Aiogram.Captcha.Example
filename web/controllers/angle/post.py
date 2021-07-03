import datetime
from web.utils.cleanup_chat_after_validation import cleanup_chat_after_validation
from web.models.angle_validation_model import AngleValidationModel

from fastapi import Depends, Request
from starlette.responses import JSONResponse, Response

from web.dependency_resolvers.aiogram_bot_to_fastapi import AiogramBot
from web.dependency_resolvers.aiogram_fsm_context_to_fastapi import UserRepoResolver
from utils.security import verify_hash



async def validate_angle_page(
    request: Request,
    validation_model: AngleValidationModel,
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

    chats = await storage.user_repo.get_chat_messages(validation_model.user_id, False)
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
