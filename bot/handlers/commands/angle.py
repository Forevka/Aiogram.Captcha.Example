from aiogram import types, Bot


async def cmd_angle(message: types.Message, bot: Bot):
    await bot.send_game(
        message.chat.id,
        "angle",
    )
