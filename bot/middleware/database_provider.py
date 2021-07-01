from typing import Any, Awaitable, Callable, Dict
from aiogram.types import Update


async def database_connection_provider(
    handler: Callable[[Update, Dict[str, Any]], Awaitable[Any]],
    event: Update,
    data: Dict[str, Any],
) -> Any:
    conn = await data['context']['db_pool'].acquire()
    data["db_conn"] = conn
    await handler(event, data)
    await data['context']['db_pool'].release(conn)