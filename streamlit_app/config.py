import os
from dotenv import load_dotenv
load_dotenv()

TOKEN = os.getenv('TOKEN')

if not TOKEN:
    print("Error: token not found in environment variables.")