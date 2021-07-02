from database.repository.user_repository import UserRepository
from database.models.user_security import UserSecurity
from typing import Optional, Tuple
from web.utils.validation_state import ValidationResponseData, ValidationStateEnum
from config import INVALIDATE_STATE_MINUTES
import datetime
from utils.security import generate_user_secret


async def validate_user_state(
    user_repo: UserRepository,
    user_id: int,
    public_key: str,
) -> Tuple[ValidationStateEnum, ValidationResponseData]:
    user_data = await user_repo.get_security(user_id)

    if not user_data or public_key != user_data.PublicKey:
        return (
            ValidationStateEnum.WrongOrigin,
            ValidationResponseData(
                user_public_key=public_key,
            ),
        )

    if (not user_data.PassedDateTime 
        or 
        datetime.datetime.utcnow() > user_data.PassedDateTime + datetime.timedelta(minutes=INVALIDATE_STATE_MINUTES)
    ):
        new_user_secret_data = generate_user_secret()

        await user_repo.update_security(user_id, new_user_secret_data['public_key'], new_user_secret_data['private_key'], None)

        return (
            ValidationStateEnum.NeedToPass,
            ValidationResponseData(
                user_public_key=new_user_secret_data["public_key"],
            ),
        )

    return (
        ValidationStateEnum.Passed,
        ValidationResponseData(
            user_public_key=user_data.PublicKey,
            passed_at=user_data.PassedDateTime,
            pass_again=user_data.PassedDateTime + datetime.timedelta(minutes=INVALIDATE_STATE_MINUTES),
            current_utc_time=datetime.datetime.utcnow(),
        ),
    )
