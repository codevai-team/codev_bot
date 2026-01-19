#!/usr/bin/env python3
"""
Скрипт для инициализации первого администратора в боте Codev.
Используйте этот скрипт, если хотите добавить админа напрямую в базу данных.
"""

import asyncio
import sys
from database import db

async def init_admin():
    """Инициализация первого администратора"""
    
    if len(sys.argv) < 2:
        print("❌ Использование: python init_admin.py <telegram_user_id>")
        print("📝 Пример: python init_admin.py 123456789")
        return
    
    try:
        telegram_id = int(sys.argv[1])
    except ValueError:
        print("❌ Неверный формат Telegram ID. Должно быть число.")
        return
    
    try:
        print("🔗 Подключение к базе данных...")
        await db.connect()
        
        # Проверяем, есть ли уже админы
        current_admins = await db.get_admin_telegram_ids()
        
        if current_admins:
            print(f"ℹ️ В системе уже есть админы: {current_admins}")
            choice = input("❓ Добавить нового админа? (y/n): ").lower()
            if choice != 'y':
                print("❌ Операция отменена.")
                return
        
        # Добавляем админа
        if await db.add_admin_telegram_id(str(telegram_id)):
            print(f"✅ Пользователь с ID {telegram_id} успешно добавлен как администратор!")
            print(f"📱 Теперь этот пользователь может использовать команду /start в боте.")
        else:
            print(f"ℹ️ Пользователь с ID {telegram_id} уже является администратором.")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        await db.disconnect()
        print("🔌 Соединение с базой данных закрыто.")

if __name__ == "__main__":
    asyncio.run(init_admin())
