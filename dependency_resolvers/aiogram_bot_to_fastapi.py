from aiogram import Bot
from fastapi import Request

class AiogramBot:
    def __init__(self, request: Request):
        self.bot: Bot = request.state.bot