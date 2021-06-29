from web.controllers.captcha.post import validate_captcha_page
from web.controllers.captcha.get import get_captcha_page

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import is_debug
from web.middleware.bot_provider import BotProviderMiddleware
from web.middleware.captcha_storage_provider import CaptchaStorageProviderMiddleware


def register_middlewares(app: FastAPI):
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.add_middleware(
        BotProviderMiddleware,
    )

    app.add_middleware(
        CaptchaStorageProviderMiddleware,
    )



def register_routes(app: FastAPI):
    app.add_api_route(
        "/captcha",
        get_captcha_page,
        tags=["Captcha"],
        methods=["GET"],
        response_class=HTMLResponse,
    )

    app.add_api_route(
        "/captcha",
        validate_captcha_page,
        tags=["Captcha"],
        methods=["POST"],
    )


app = FastAPI(
    root_path="" if is_debug() else "/api/captcha",
)

