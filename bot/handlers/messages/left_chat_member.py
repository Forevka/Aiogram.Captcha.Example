from database.repository.chat_settings_repository import ChatSettingsRepository
from database.repository.user_repository import UserRepository
from aiogram import Bot, types
from asyncio import gather


async def left_chat_member(
    message: types.Message,
    bot: Bot,
    user_repo: UserRepository,
):
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    if any(
        (i for i in chat_admins if all([i.user.id == bot.id, i.can_delete_messages]))
    ):
        chat_settings_repo = ChatSettingsRepository(user_repo.conn)
        chat_setting = await chat_settings_repo.get(message.chat.id)

        if chat_setting and chat_setting.IsNeedToDeleteServiceMessageOnLeave:
            await message.delete()
    else:
        gather(
            *[
                bot.send_message(
                    i.user.id,
                    f"Please promote me to administrator in this chat: {message.chat.title}\nAlso i need permission to delete messages.",
                )
                for i in chat_admins
            ]
        )
