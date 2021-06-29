import datetime

from fastapi import Depends, Request
from starlette.responses import Response

from config import (
    INVALIDATE_STATE_MINUTES,
    RECAPTCHA_PUBLIC_KEY,
)
from web.dependency_resolvers.aiogram_fsm_context_to_fastapi import AiogramFSMContext
from utils.security import generate_user_secret
from web.templates import templates


async def get_captcha_page(
    request: Request,
    user_id: int,
    first_name: str,
    public_key: str = "",
    storage: AiogramFSMContext = Depends(AiogramFSMContext),
) -> Response:
    user_data = await storage.user_context.get_data()
    user_secret_data = user_data.get("secret", {})

    passed_at = user_secret_data.get("passed_time", 0)

    if passed_at > 1:
        pass_again = datetime.datetime.fromtimestamp(passed_at) + datetime.timedelta(
            minutes=INVALIDATE_STATE_MINUTES
        )
        if datetime.datetime.utcnow() > pass_again:
            user_secret_data = generate_user_secret()
            user_data["secret"] = user_secret_data

            await storage.user_context.set_data(user_data)
        else:
            return templates.TemplateResponse(
                "passed.html",
                {
                    "request": request,
                    "first_name": first_name,
                    "passed_at": datetime.datetime.fromtimestamp(
                        user_secret_data.get("passed_time", 0)
                    ),
                    "pass_again": pass_again,
                    "current_utc_time": datetime.datetime.utcnow(),
                },
            )

    if public_key != user_secret_data["public_key"]:
        return templates.TemplateResponse(
            "wrong_origin.html",
            {
                "request": request,
            },
        )

    return templates.TemplateResponse(
        "captcha.html",
        {
            "request": request,
            "recaptcha_public_key": RECAPTCHA_PUBLIC_KEY,
            "first_name": first_name,
            "user_id": user_id,
            "user_public_key": user_secret_data["public_key"],
        },
    )
