from typing import Callable, Dict, Any, Awaitable

import aiohttp
from aiogram import BaseMiddleware
from aiogram import types
from aiogram.types import Message
import urllib.parse

from bot.storage import update_profile_params, get_profile_params_by_id


class FatSecretMiddleware(BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        telegram_id = event.from_user.id
        user_state = get_profile_params_by_id(telegram_id)
        print(f"User state in middleware: {user_state}")
            # weight = user_state.get('weight')
            # height = user_state.get('height')
            # age = user_state.get('age')
            # activity = user_state.get('activity')
            # gender = user_state.get('gender')
            # calorie_goal = self.count_daily_calorie_rate(gender, age, weight, height, activity)
            # update_profile_params(event.from_user.id, calorie_goal=calorie_goal)
            # print('my params', get_profile_params_by_id(event.from_user.id))
        return await handler(event, data)


