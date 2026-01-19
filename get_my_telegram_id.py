#!/usr/bin/env python3
"""
Скрипт для получения вашего Telegram ID
Запустите бота и отправьте ему любое сообщение
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем бота
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user_id = message.from_user.id
    username = message.from_user.username or "не указан"
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip()
    
    response = (
        f"👤 <b>Ваша информация:</b>\n\n"
        f"🆔 <b>Telegram ID:</b> <code>{user_id}</code>\n"
        f"👤 <b>Имя:</b> {full_name}\n"
        f"📝 <b>Username:</b> @{username}\n\n"
        f"📋 <b>Скопируйте ваш ID:</b> <code>{user_id}</code>\n\n"
        f"Используйте этот ID для добавления себя как админа."
    )
    
    await message.answer(response)
    
    # Выводим в консоль
    print("=" * 70)
    print(f"👤 Пользователь подключился:")
    print(f"   ID: {user_id}")
    print(f"   Имя: {full_name}")
    print(f"   Username: @{username}")
    print("=" * 70)

@dp.message()
async def any_message(message: types.Message):
    """Обработчик любого сообщения"""
    user_id = message.from_user.id
    username = message.from_user.username or "не указан"
    first_name = message.from_user.first_name or ""
    
    response = (
        f"👋 Привет, {first_name}!\n\n"
        f"🆔 Ваш Telegram ID: <code>{user_id}</code>\n\n"
        f"Отправьте /start для получения полной информации."
    )
    
    await message.answer(response)
    
    print(f"📨 Сообщение от {first_name} (ID: {user_id}): {message.text}")

async def main():
    """Основная функция"""
    print("=" * 70)
    print("🤖 Бот запущен для получения Telegram ID")
    print("=" * 70)
    print("📱 Отправьте боту /start или любое сообщение")
    print("🆔 Ваш Telegram ID будет показан в ответе")
    print("=" * 70)
    print()
    
    try:
        await dp.start_polling(bot)
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Бот остановлен")
