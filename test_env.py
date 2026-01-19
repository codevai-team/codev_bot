import os
from dotenv import load_dotenv

print("Текущая директория:", os.getcwd())
print("Файл .env существует:", os.path.exists('.env'))

load_dotenv()

bot_token = os.getenv('BOT_TOKEN')
db_url = os.getenv('DB')

print("BOT_TOKEN загружен:", "Да" if bot_token else "Нет")
if bot_token:
    print("Длина токена:", len(bot_token))
    print("Первые 10 символов:", bot_token[:10])
    
print("DB загружен:", "Да" if db_url else "Нет")
