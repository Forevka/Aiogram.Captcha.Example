from typing import Tuple
from web.utils.validation_state import ValidationResponseData, ValidationStateEnum
from aiogram.dispatcher.fsm.context import FSMContext
from config import INVALIDATE_STATE_MINUTES
import datetime
from utils.security import generate_user_secret


async def validate_user_state(
    user_context: FSMContext,
    public_key: str,
    available_context: dict = {},
) -> Tuple[ValidationStateEnum, ValidationResponseData]:
    user_data = available_context or await user_context.get_data()
    user_secret_data = user_data.get("secret", {})

    if (not user_secret_data or public_key != user_secret_data["public_key"]):
        return (
            ValidationStateEnum.WrongOrigin,
            ValidationResponseData(
                user_public_key=public_key,
            ),
        )

    passed_at = user_secret_data.get("passed_time", 0)

    pass_again = datetime.datetime.fromtimestamp(passed_at) + datetime.timedelta(
        minutes=INVALIDATE_STATE_MINUTES
    )

    if (passed_at == 0 or datetime.datetime.utcnow() > pass_again):
        user_secret_data = generate_user_secret()
        user_data["secret"] = user_secret_data

        await user_context.set_data(user_data)

        return (
            ValidationStateEnum.NeedToPass,
            ValidationResponseData(
                user_public_key=user_secret_data["public_key"],
            ),
        )

    return (
        ValidationStateEnum.Passed,
        ValidationResponseData(
            user_public_key=user_secret_data["public_key"],
            passed_at=datetime.datetime.fromtimestamp(
                user_secret_data.get("passed_time", 0)
            ),
            pass_again=pass_again,
            current_utc_time=datetime.datetime.utcnow(),
        ),
    )
