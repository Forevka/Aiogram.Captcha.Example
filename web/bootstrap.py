from web.middleware.database_provider import DatabaseProviderMiddleware
from web.controllers.hcaptcha.post import validate_hcaptcha_page
from web.controllers.hcaptcha.get import get_hcaptcha_page
from web.controllers.angle.post import validate_angle_page
from web.controllers.angle.get import get_angle_page
from web.controllers.recaptcha.get import get_recaptcha_page
from web.controllers.recaptcha.post import validate_recaptcha_page

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

from config import is_debug
from web.middleware.bot_provider import BotProviderMiddleware
from web.middleware.captcha_storage_provider import CaptchaStorageProviderMiddleware


def register_middlewares(app: FastAPI):
    if is_debug():
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
        DatabaseProviderMiddleware,
    )

    app.add_middleware(
        CaptchaStorageProviderMiddleware,
    )


def register_routes(app: FastAPI):
    app.add_api_route(
        "/recaptcha",
        get_recaptcha_page,
        tags=["reCaptcha"],
        methods=["GET"],
        response_class=HTMLResponse,
    )

    app.add_api_route(
        "/recaptcha",
        validate_recaptcha_page,
        tags=["reCaptcha"],
        methods=["POST"],
    )

    app.add_api_route(
        "/angle",
        get_angle_page,
        tags=["Angle"],
        methods=["GET"],
        response_class=HTMLResponse,
    )

    app.add_api_route(
        "/angle",
        validate_angle_page,
        tags=["Angle"],
        methods=["POST"],
    )

    app.add_api_route(
        "/hcaptcha",
        get_hcaptcha_page,
        tags=["hCaptcha"],
        methods=["GET"],
        response_class=HTMLResponse,
    )

    app.add_api_route(
        "/hcaptcha",
        validate_hcaptcha_page,
        tags=["hCaptcha"],
        methods=["POST"],
    )


app = FastAPI(
    root_path="" if is_debug() else "/api/captcha",
)
