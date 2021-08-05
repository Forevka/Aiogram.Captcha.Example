from aiogram import types


async def cmd_start(message: types.Message, _):
    await message.answer(
        'Привет, я капча бот.\n\nТы можешь пригласить меня в свою группу что-бы посмотреть как я работаю или войти в тестовую - @reCaptchaTest\n<a href="https://github.com/Forevka/Aiogram.Captcha.Example">Исходный код</a>\nКоманды:\n/recaptcha - пройти рекапчу от гугла в лс\n/hcaptcha - пройти аналог рекапчи в лс\n/angle - пройти более интересную капчу в лс\n/minesweeper - минное поле, прям как в старой доброй винде',
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
