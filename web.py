from aiogram.bot.bot import Bot
from aiogram.contrib.fsm_storage.redis import RedisStorage2

import aiohttp
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse, Response
from middleware.web.redis_provider import RedisProviderMiddleware
import datetime

from config import ENVIRONMENT, RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY, TOKEN, is_debug
from models import RecaptchaSiteverifyModel, RecaptchaValidationModel
from utils import generate_user_secret, verify_hash

bot = Bot(token=TOKEN)

async def get_captcha_page(request: Request, user_id: int, first_name: str) -> Response:
    user_storage: RedisStorage2 = request.state.storage

    user_secret_data = await user_storage.get_data(chat=user_id, user=user_id)

    passed_at = user_secret_data.get('passed_time', 0)

    if (passed_at > 1):
        pass_again = datetime.datetime.fromtimestamp(passed_at) + datetime.timedelta(minutes=1)
        if (datetime.datetime.utcnow() > pass_again):
            user_secret_data = generate_user_secret()

            await user_storage.set_data(chat=user_id, user=user_id, data=user_secret_data)
        else:
            return templates.TemplateResponse("passed.html", {
                "request": request,
                "first_name": first_name,
                "passed_at": datetime.datetime.fromtimestamp(user_secret_data.get('passed_time')),
                "pass_again": pass_again,
                "current_utc_time": datetime.datetime.utcnow(),
            })

    return templates.TemplateResponse("captcha.html", {
        "request": request,
        "recaptcha_public_key": RECAPTCHA_PUBLIC_KEY,
        "first_name": first_name,
        "user_id": user_id,
        "user_public_key": user_secret_data['public_key'],
    })


async def validate_captcha_page(request: Request, validation_model: RecaptchaValidationModel) -> Response:
    user_storage: RedisStorage2 = request.state.storage

    user_secret_data = await user_storage.get_data(chat=validation_model.user_id, user=validation_model.user_id)

    if not all([
        user_secret_data, verify_hash(user_secret_data['private_key'],
                                      validation_model.public_key, user_secret_data['hash_key']),
    ],):
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Can't verify your attempt. Probably you are bot :)",
            }
        )

    async with aiohttp.ClientSession() as session:
        async with session.get('https://www.google.com/recaptcha/api/siteverify', params={
            "secret": RECAPTCHA_PRIVATE_KEY,
            "response": validation_model.token,
        }) as resp:
            if (resp.status == 200):
                verify_result = RecaptchaSiteverifyModel(**await resp.json())
                if (verify_result.success):
                    user_secret_data['passed_time'] = datetime.datetime.utcnow().timestamp()

                    await bot.send_message(validation_model.user_id, 'Turing test succesfully passed')

                    await user_storage.set_data(chat=validation_model.user_id, user=validation_model.user_id, data=user_secret_data)

                    return JSONResponse(  # everything is ok
                        status_code=200,
                        content={
                            "detail": "Now you can close this tab",
                        }
                    )

                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": "Can't verify your attempt. Probably you are bot :)",
                    }
                )

            return JSONResponse(
                status_code=400,
                content={
                    "detail": "Something went wrong. Please try later.",
                }
            )

app = FastAPI(
    root_path='' if is_debug() else '/api',
)

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    RedisProviderMiddleware,
)


app.add_api_route(
    '/captcha',
    get_captcha_page,
    tags=['Captcha'],
    methods=['GET'],
    response_class=HTMLResponse,
)

app.add_api_route(
    '/captcha',
    validate_captcha_page,
    tags=['Captcha'],
    methods=['POST'],
)
