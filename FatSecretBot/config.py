import os

from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.DEBUG)

aiohttp_logger = logging.getLogger("aiohttp")
aiohttp_logger.setLevel(logging.DEBUG)

load_dotenv()

API_TOKEN = os.getenv("BOT_TOKEN")
FAT_SECRET_PASSWORD = os.getenv("FAT_SECRET_PASSWORD")
WEATHER_TOKEN = os.getenv("WEATHER_TOKEN")
WEATHER_API_URL = "https://api.openweathermap.org/data/2.5/weather"

FAT_SECRET_TOKEN_URL = "https://oauth.fatsecret.com/connect/token"
FAT_SECRET_API_URL = "https://platform.fatsecret.com/rest/server.api"
FAT_SECRET_USERNAME="d4212cee75c249b7acfae27a1d0105d3"

if not API_TOKEN or not FAT_SECRET_PASSWORD or not WEATHER_TOKEN:
    raise NameError
