from aiogram import types


async def cmd_start(message: types.Message):
    await message.answer(
        'Привет, я капча бот.\n\nТы можешь пригласить меня в свою группу что-бы посмотреть как я работаю или войти в тестовую - @reCaptchaTest\n<a href="https://github.com/Forevka/Aiogram.Captcha.Example">Исходный код</a>\nКоманды:\n/captcha - пройти капчу в лс',
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
