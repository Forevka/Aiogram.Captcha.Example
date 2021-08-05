import logging
from typing import Any
from asyncio import gather

from aiogram import Bot, Dispatcher, types
from aiogram.types import Message

TOKEN = "666922879:AAEWkOwKYH-Sz7pBm9fLtXDlDV1fSGiNbwo"
dp = Dispatcher()

logger = logging.getLogger(__name__)


@dp.message(commands={"e"})
async def command_start_handler(message: Message,) -> None:
    '''
    TypeError: unhashable type: 'SendMessage'
        Traceback (most recent call last):
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/dispatcher.py", line 279, in _process_update
            response = await self.feed_update(bot, update, **kwargs)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/dispatcher.py", line 101, in feed_update
            response = await self.update.trigger(update, bot=bot, **kwargs)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/event/telegram.py", line 135, in trigger
            return await wrapped_outer(event, kwargs)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/middlewares/error.py", line 24, in __call__
            return await handler(event, data)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/middlewares/user_context.py", line 21, in __call__
            return await handler(event, data)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/fsm/middleware.py", line 38, in __call__
            return await handler(event, data)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/event/telegram.py", line 146, in _trigger
            return await wrapped_inner(event, kwargs)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/event/handler.py", line 40, in call
            return await wrapped()
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/dispatcher.py", line 241, in _listen_update
            response = await observer.trigger(event, update=update, **kwargs)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/event/telegram.py", line 135, in trigger
            return await wrapped_outer(event, kwargs)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/event/telegram.py", line 146, in _trigger
            return await wrapped_inner(event, kwargs)
        File "/workspaces/Aiogram.Captcha.Example/.venv/lib/python3.8/site-packages/aiogram/dispatcher/event/handler.py", line 40, in call
            return await wrapped()
        File "/workspaces/Aiogram.Captcha.Example/test.py", line 16, in command_start_handler
            gather(
        File "/opt/python/3.8.6/lib/python3.8/asyncio/tasks.py", line 820, in gather
            if arg not in arg_to_fut:
        TypeError: unhashable type: 'SendMessage'
    '''
    gather(
        *[
            message.answer('qwe1'),
            message.answer('qwe2'),
        ]
    )


@dp.message(commands={"a"})
async def echo_handler(message: types.Message, bot: Bot,) -> None:
    gather(
        *[
            bot.send_message(text='qwe1', chat_id=message.from_user.id,),
            bot.send_message(text='qwe2', chat_id=message.from_user.id,),
        ]
    )



def main() -> None:
    bot = Bot(TOKEN, parse_mode="HTML")
    dp.run_polling(bot)


if __name__ == "__main__":
    main()