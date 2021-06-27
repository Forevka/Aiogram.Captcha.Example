from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from starlette.responses import Response


async def get_captcha_page(request: Request,) -> Response:
    return """
    <head>
        <script src='https://www.google.com/recaptcha/api.js'></script>
    </head>
    <body>
        <form method="post" action="/captcha">
            <div type="submit" class="g-recaptcha" data-sitekey="6LfIEV4bAAAAAKIMAQetUQ8-HD-53W5tsaFxn8LG" style="margin-bottom:1em";></div>
        </form>
    </body>
    """

async def validate_captcha_page(request: Request,) -> Response:
    print(1)
    return {

    }

app = FastAPI()


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