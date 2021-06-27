from typing import Any

from aiogram.contrib.fsm_storage.redis import RedisStorage2
from aiogram.dispatcher.middlewares import LifetimeControllerMiddleware

class RedisProviderMiddleware(LifetimeControllerMiddleware):
    """
    Redis provider middleware middleware
    """
    skip_patterns = ["error", "update"]

    def __init__(self,):
        super(RedisProviderMiddleware, self).__init__()
        self.storage = RedisStorage2(db=8, prefix='captcha_service')

    async def pre_process(self, message: Any, data: dict, *args, **kwargs,):
        data['storage'] = self.storage
    


        