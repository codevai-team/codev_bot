#!/usr/bin/env python3
"""
Простой тест бота - проверяет работает ли бот вообще
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import BOT_TOKEN, DATABASE_URL
from database import db

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
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
    
    logger.info(f"Получена команда /start от {first_name} (ID: {user_id})")
    
    # Проверяем, является ли пользователь админом
    is_admin = await db.is_admin(user_id)
    
    if is_admin:
        response = (
            f"✅ <b>Добро пожаловать, {first_name}!</b>\n\n"
            f"🆔 Ваш ID: <code>{user_id}</code>\n"
            f"👑 Статус: <b>Администратор</b>\n\n"
            f"Бот работает корректно!"
        )
        logger.info(f"✅ Пользователь {user_id} является админом")
    else:
        response = (
            f"❌ <b>Доступ запрещен</b>\n\n"
            f"👤 {first_name}\n"
            f"🆔 Ваш ID: <code>{user_id}</code>\n"
            f"👑 Статус: <b>Не администратор</b>\n\n"
            f"Обратитесь к администратору для получения доступа.\n\n"
            f"<i>Текущие админы в базе данных:</i>\n"
        )
        
        # Получаем список админов
        admin_ids = await db.get_admin_telegram_ids()
        if admin_ids:
            response += f"<code>{', '.join(admin_ids)}</code>"
        else:
            response += "<i>Нет админов в базе данных</i>"
        
        logger.warning(f"❌ Пользователь {user_id} НЕ является админом")
    
    await message.answer(response)

@dp.message()
async def any_message(message: types.Message):
    """Обработчик любого сообщения"""
    user_id = message.from_user.id
    first_name = message.from_user.first_name or ""
    
    logger.info(f"Получено сообщение от {first_name} (ID: {user_id}): {message.text}")
    
    response = (
        f"👋 Привет, {first_name}!\n\n"
        f"🆔 Ваш ID: <code>{user_id}</code>\n\n"
        f"Отправьте /start для проверки доступа."
    )
    
    await message.answer(response)

async def main():
    """Основная функция"""
    print("=" * 70)
    print("🤖 ТЕСТОВЫЙ РЕЖИМ БОТА")
    print("=" * 70)
    print()
    
    try:
        # Подключаемся к базе данных
        logger.info("🔄 Подключение к базе данных...")
        await db.connect()
        logger.info("✅ Подключение к БД успешно!")
        
        # Получаем список админов
        admin_ids = await db.get_admin_telegram_ids()
        print(f"👥 Админы в базе данных: {admin_ids}")
        print()
        
        # Запускаем бота
        logger.info("🚀 Запуск бота...")
        print("📱 Отправьте боту /start")
        print("=" * 70)
        print()
        
        await dp.start_polling(bot)
        
    except Exception as e:
        logger.error(f"❌ Ошибка: {e}", exc_info=True)
    finally:
        await db.disconnect()
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Бот остановлен пользователем")
