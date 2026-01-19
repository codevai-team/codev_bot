import os
from dotenv import load_dotenv
from imgbb_uploader import ImgBBUploader, imgbb_uploader

# Загружаем переменные окружения
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DB")
IMGBB_API_KEY = os.getenv("IMGBB_API_KEY")

if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN не найден в .env файле")

if not DATABASE_URL:
    raise ValueError("DB не найден в .env файле")

# Инициализируем imgbb uploader если есть API ключ
if IMGBB_API_KEY:
    imgbb_uploader = ImgBBUploader(IMGBB_API_KEY)
else:
    print("⚠️ IMGBB_API_KEY не найден в .env файле. Загрузка изображений будет недоступна.")

