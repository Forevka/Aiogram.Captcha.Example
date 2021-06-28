import html
import logging
from asyncio import gather
from datetime import datetime, timedelta
from urllib.parse import quote

from aiogram import Bot, Dispatcher, F, types
from aiogram.dispatcher.fsm.context import FSMContext
from aiogram.dispatcher.fsm.storage.redis import RedisStorage
from aiogram.types.chat_permissions import ChatPermissions
from aioredis import Redis

from config import (CAPTCHA_ROUTE, HOST, INVALIDATE_STATE_MINUTES,
                    PROXY_PREFIX, REDIS_HOST, TOKEN)
from middleware.bot.captcha_storage_provider import CaptchaStorageProviderMiddleware
from utils import generate_user_secret, is_need_to_pass_captcha

logging.basicConfig(level=logging.INFO)

dp = Dispatcher()
dp.update.middleware(
    CaptchaStorageProviderMiddleware(
        storage=RedisStorage(
            Redis(host=REDIS_HOST, db=8,),
            prefix='captcha_service',
        )
    )
)


@dp.message(commands={'start', 'help',})
async def cmd_start(message: types.Message):
    await message.answer(
        'Привет, я капча бот.\n\nТы можешь пригласить меня в свою группу что-бы посмотреть как я работаю или войти в тестовую - @reCaptchaTest\n<a href="https://github.com/Forevka/Aiogram.Captcha.Example">Исходный код</a>\nКоманды:\n/captcha - пройти капчу в лс',
        parse_mode='HTML', 
        disable_web_page_preview=True,
    )

@dp.message(commands={'captcha',})
async def cmd_start(message: types.Message, bot: Bot):
    await bot.send_game(message.chat.id, 'captcha',)

@dp.message(F.content_type == 'new_chat_members')
async def chat_member_status_change(message: types.Message, captcha_storage: RedisStorage, bot: Bot):
    chat_admins = await bot.get_chat_administrators(message.chat.id)
    if (any((i for i in chat_admins if all([i.user.id == bot.id, i.can_restrict_members])))):
        for member in message.new_chat_members:
            user_data = await captcha_storage.get_data(bot, member.id, member.id)
            user_secret_data = user_data.get('secret', {})
            user_chats = user_data.get('chats', {})

            if any([is_need_to_pass_captcha(user_secret_data), str(message.chat.id) not in user_chats]):
                hey_msg = await message.answer(f'Hey, <a href="tg://user?id={member.id}">{html.escape(member.first_name, quote=False)}</a> please pass the captcha!', parse_mode='HTML')
                game_msg = await message.answer_game('captcha',)
                await bot.restrict_chat_member(message.chat.id, member.id, ChatPermissions(**{
                    "can_send_messages": False,
                    "can_send_media_messages": False,
                    "can_send_polls": False,
                    "can_send_other_messages": False,
                    "can_add_web_page_previews": False,
                    "can_change_info": False,
                    "can_invite_users": False,
                    "can_pin_messages": False,
                }), until_date=datetime.utcnow() + timedelta(days=365),)

                user_chats[message.chat.id] = [
                    hey_msg.message_id,
                    game_msg.message_id,
                ]

                user_data['chats'] = user_chats

                await captcha_storage.set_data(bot, member.id, member.id, user_data,)
    else:
        gather(
            *[bot.send_message(i.user.id, f'Я не администратор в этом чате: {message.chat.id}') for i in chat_admins]
        )


@dp.callback_query(F.game_short_name == 'captcha')
async def send_recaptcha(query: types.CallbackQuery, captcha_storage: RedisStorage, captcha_state: FSMContext):
    user_data = await captcha_storage.get_data(bot, query.from_user.id, query.from_user.id,)

    user_secret_data = user_data.get('secret', {})

    if (user_secret_data.get('passed_time', 0) == 0 or datetime.utcnow() > (datetime.fromtimestamp(user_secret_data.get('passed_time')) + timedelta(minutes=INVALIDATE_STATE_MINUTES))):
        user_data['secret'] = generate_user_secret()

    await captcha_storage.set_data(bot, query.from_user.id, query.from_user.id, user_data,)

    await query.answer(url=f"{HOST}{PROXY_PREFIX}{CAPTCHA_ROUTE}?user_id={query.from_user.id}&first_name={quote(query.from_user.first_name)}&public_key={user_data['secret']['public_key']}",)


if __name__ == '__main__':
    bot = Bot(token=TOKEN)

    dp.run_polling(bot)
