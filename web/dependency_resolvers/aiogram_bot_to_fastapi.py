from aiogram import Bot
from fastapi import Request

class AiogramBot:
    def __init__(self, request: Request):
        self.bot: Bot = request.state.bot
        self.bot_link: str = request.state.bot_link
    