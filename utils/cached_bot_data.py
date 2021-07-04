from aiogram.client.bot import Bot

class CachedBotData:
    def __init__(
        self,
    ) -> None:
        self.usernames = {}

    async def cached_link_to_bot(self, bot: Bot) -> str:
        if (bot.token not in self.usernames):
            self.usernames[bot.token] = (await bot.get_me()).username

        return f'https://t.me/{self.usernames[bot.token]}'

cache = CachedBotData()