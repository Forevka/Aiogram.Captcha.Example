from secrets import token_urlsafe
from typing import Dict
from aiogram.bot.bot import Bot

import aiohttp
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from starlette.responses import JSONResponse, Response

from config import RECAPTCHA_PRIVATE_KEY, RECAPTCHA_PUBLIC_KEY, TOKEN
from models import RecaptchaSiteverifyModel, RecaptchaValidationModel
from utils import calculate_hash, verify_hash

bot = Bot(token=TOKEN)
user_storage: Dict[int, Dict[str, str]] = {}


async def get_captcha_page(request: Request, user_id: int, first_name: str) -> Response:
    user_private_key = token_urlsafe(16)
    user_public_key = token_urlsafe(16)

    user_storage[user_id] = {
        'private_key': user_private_key,
        'public_key': user_public_key,
        'hash_key': calculate_hash(user_private_key, user_public_key),
    }

    return templates.TemplateResponse("captcha.html", {
        "request": request,
        "recaptcha_public_key": RECAPTCHA_PUBLIC_KEY,
        "first_name": first_name,
        "user_id": user_id,
        "user_public_key": user_storage[user_id]['public_key'],
    })


async def validate_captcha_page(request: Request, validation_model: RecaptchaValidationModel) -> Response:
    user_secret_data = user_storage.get(validation_model.user_id)

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
                    await bot.send_message(validation_model.user_id, 'Turing test succesfully passed')
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

app = FastAPI()

templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
