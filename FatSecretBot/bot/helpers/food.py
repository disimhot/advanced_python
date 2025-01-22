import urllib
import re
from pydantic import BaseModel
from typing import Optional
import aiohttp
from datetime import datetime, timedelta
from config import FAT_SECRET_TOKEN_URL, FAT_SECRET_PASSWORD, FAT_SECRET_API_URL, \
    FAT_SECRET_USERNAME

from bot.models.models import *


class Food(BaseModel):
    expiration_time: Optional[datetime] = None
    bearer: Optional[str] = None

    async def _get_token(self) -> None:
        async with (aiohttp.ClientSession() as session):
            auth_url = f"{FAT_SECRET_TOKEN_URL}"
            data = aiohttp.FormData()
            data.add_field("grant_type", "client_credentials")
            data.add_field("scope", "basic")
            auth = aiohttp.BasicAuth(login=FAT_SECRET_USERNAME, password=FAT_SECRET_PASSWORD)
            async with session.post(auth_url, auth=auth, data=data) as response:
                if response.status == 200:
                    response_json = await response.json()
                    token, expires_in = response_json["access_token"], response_json["expires_in"]
                    self.bearer = f"Bearer {token}"
                    current_time = datetime.now()
                    expiration_time = current_time + timedelta(seconds=86400)
                    self.expiration_time = expiration_time
                else:
                    raise Exception(f"Failed to fetch token. Status code: {response.status}")

    async def fetch_fatsecret_data(self, food_name, amount):
        if self.expiration_time is None or self.expiration_time < datetime.now():
            await self._get_token()
        async with aiohttp.ClientSession() as session:
            fatsecret_url = f"{FAT_SECRET_API_URL}"
            headers = {
                "Authorization": self.bearer,
                "Content-Type": "application/json"
            }

            params = {
                'method': 'foods.search',
                'search_expression': food_name,
                'format': 'json',
                'max_results': 3
            }
            query_string = urllib.parse.urlencode(params)
            url_with_params = f"{fatsecret_url}?{query_string}"
            async with session.get(url_with_params, headers=headers) as response:
                if response.status == 200:
                    content_type = response.headers.get('Content-Type', '').lower()
                    if 'application/json' in content_type:
                        resp = await response.json()
                        food_description = resp['foods']['food'][0]['food_description']
                        nutritional_info = self.parse_nutritional_info(food_description)
                        return nutritional_info
                    else:
                        raise Exception(f"Failed to fetch data. Content-Type: {content_type}")
                else:
                    raise Exception(f"Failed to fetch data. Status code: {response.status}")

    def parse_nutritional_info(self, description):
        pattern = (r"Calories:\s*(\d+\.?\d*)kcal.*?Fat:\s*(\d+\.?\d*)g.*?Carbs:\s*("
                   r"\d+\.?\d*)g.*?Protein:\s*(\d+\.?\d*)g")

        match = re.search(pattern, description)

        if match:
            calories = float(match.group(1))
            fat = float(match.group(2))
            carbs = float(match.group(3))
            protein = float(match.group(4))

            return {
                'calories': calories,
                'fat': fat,
                'carbs': carbs,
                'protein': protein
            }
        else:
            return None
