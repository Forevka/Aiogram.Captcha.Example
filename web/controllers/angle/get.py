from web.utils.validation_state import ValidationStateEnum
from web.utils.validate_user_state import validate_user_state

from fastapi import Depends, Request
from starlette.responses import Response
from random import choice

from web.dependency_resolvers.aiogram_fsm_context_to_fastapi import UserRepoResolver
from web.templates import templates
import json

poks = json.loads(
    open(
        "list-of-pokemons.json",
        "r",
    ).read()
)


async def get_angle_page(
    request: Request,
    user_id: int,
    first_name: str,
    public_key: str = "",
    storage: UserRepoResolver = Depends(UserRepoResolver),
) -> Response:
    user_validation_result, data = await validate_user_state(
        storage.user_repo, user_id, public_key,
    )

    if user_validation_result == ValidationStateEnum.NeedToPass:
        return templates.TemplateResponse(
            "captcha/angle.html",
            {
                "request": request,
                "first_name": first_name,
                "user_id": user_id,
                "image_list": json.dumps([choice(poks) for _ in range(15)]),
                **data.dict(),
            },
        )
    elif user_validation_result == ValidationStateEnum.Passed:
        return templates.TemplateResponse(
            "passed.html",
            {
                "request": request,
                "first_name": first_name,
                **data.dict(),
            },
        )

    return templates.TemplateResponse(
        "wrong_origin.html",
        {
            "request": request,
            **data.dict(),
        },
    )
