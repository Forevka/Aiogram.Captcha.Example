from database.repository.chat_repository import ChatRepository
from database.repository.chat_settings_repository import ChatSettingsRepository
from aiogram.dispatcher.fsm.context import FSMContext
from config import TOKEN
from fastapi import Request
from aiogram import Bot
from database.repository.user_repository import UserRepository

class AiogramFSMContext:
    def __init__(self, user_id: int, request: Request):
        self.user_context = FSMContext(bot=request.state.bot, storage=request.state.storage, chat_id=user_id, user_id=user_id)

class UserRepoResolver:
    def __init__(self, request: Request):
        self.user_repo = UserRepository(request.state.connection)
        self.chat_repo = ChatRepository(request.state.connection)
        self.chat_setting_repo = ChatSettingsRepository(request.state.connection)