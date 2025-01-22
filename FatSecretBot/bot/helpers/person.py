from pydantic import BaseModel
from typing import List, Optional, Dict
import aiohttp

from config import WEATHER_TOKEN, WEATHER_API_URL

from bot.models.models import *


class Person(BaseModel):
    weight: int
    height: int
    age: int
    activity: int
    city: str
    diet: str
    gender: str
    water_goal: Optional[List[int]] = []
    calorie_goal: Optional[List[int]] = []
    logged_water: Optional[List[int]] = []
    logged_calories: Optional[List[int]] = []
    burned_calories: Optional[List[int]] = []

    def _get_tdee(self, activity) -> float:
        if activity < 5000:
            return 1.2
        elif 5000 <= activity < 7000:
            return 1.375
        elif 7000 <= activity < 10000:
            return 1.55
        elif 10000 <= activity < 12000:
            return 1.725
        else:
            return 1.9

    def count_daily_calorie_rate(self) -> int:
        tdee = self._get_tdee(self.activity)
        if self.gender == 'male':
            return int(tdee * (88.362 + (13.397 * self.weight) + (4.799 * self.height) - (
                    5.677 * self.age)))
        elif self.gender == 'female':
            return int(tdee * (447.593 + (9.247 * self.weight) + (3.098 * self.height) - (
                    4.330 * self.age)))
        else:
            raise ValueError('Gender is not valid')

    async def count_daily_water_rate(self) -> int:
        weather_response = await self.fetch_weather()
        temperature = weather_response.main.temp

        if temperature > 25:
            return 30 * self.weight + 500
        return 30 * self.weight

    async def fetch_weather(self) -> WeatherResponse:
        try:
            url = f"{WEATHER_API_URL}?q={self.city}&appid={WEATHER_TOKEN}&units=metric"

            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        response = await response.json()
                        return WeatherResponse(**response)
                    else:
                        return None
        except aiohttp.ClientError as e:
            raise ValidationError(f"Failed to fetch weather data: {e}")
        except ValidationError as e:
            raise ValidationError(f"Invalid weather data: {e}")
