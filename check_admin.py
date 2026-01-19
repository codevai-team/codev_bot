#!/usr/bin/env python3
"""
Скрипт для проверки админов в базе данных
"""
import asyncio
import asyncpg
from config import DATABASE_URL

async def check_admins():
    """Проверить список админов в базе данных"""
    
    print("=" * 70)
    print("🔍 Проверка админов в базе данных")
    print("=" * 70)
    print()
    
    try:
        # Подключаемся к базе данных
        print("🔄 Подключение к базе данных...")
        conn = await asyncpg.connect(DATABASE_URL)
        print("✅ Подключение успешно!")
        print()
        
        # Проверяем таблицу settings
        print("📋 Проверка таблицы settings...")
        settings = await conn.fetch("SELECT key, value FROM settings")
        
        if not settings:
            print("⚠️  Таблица settings пуста!")
            print()
            print("Создаем запись для admin_telegram_ids...")
            await conn.execute(
                "INSERT INTO settings (key, value) VALUES ('admin_telegram_ids', '[]')"
            )
            print("✅ Запись создана с пустым массивом админов")
        else:
            print(f"✅ Найдено {len(settings)} записей в settings:")
            for setting in settings:
                print(f"   - {setting['key']}: {setting['value']}")
        
        print()
        
        # Получаем список админов
        print("👥 Список админов:")
        admin_ids_json = await conn.fetchval(
            "SELECT value FROM settings WHERE key = 'admin_telegram_ids'"
        )
        
        if admin_ids_json:
            import json
            try:
                admin_ids = json.loads(admin_ids_json)
                if admin_ids:
                    print(f"✅ Найдено {len(admin_ids)} админов:")
                    for i, admin_id in enumerate(admin_ids, 1):
                        print(f"   {i}. Telegram ID: {admin_id}")
                else:
                    print("⚠️  Список админов пуст!")
                    print()
                    print("❗ Чтобы добавить себя как админа:")
                    print("   1. Узнайте свой Telegram ID (напишите @userinfobot)")
                    print("   2. Запустите: python init_admin.py")
                    print("   3. Или добавьте вручную в базу данных")
            except json.JSONDecodeError as e:
                print(f"❌ Ошибка парсинга JSON: {e}")
                print(f"   Значение: {admin_ids_json}")
        else:
            print("⚠️  Запись admin_telegram_ids не найдена!")
        
        print()
        
        # Проверяем таблицу projects
        print("📂 Проверка таблицы projects...")
        projects_count = await conn.fetchval("SELECT COUNT(*) FROM projects")
        print(f"✅ Найдено {projects_count} проектов в базе данных")
        
        print()
        print("=" * 70)
        print("✅ Проверка завершена!")
        print("=" * 70)
        
        # Закрываем соединение
        await conn.close()
        
    except asyncpg.exceptions.PostgresError as e:
        print()
        print(f"❌ Ошибка базы данных: {e}")
        print()
    except Exception as e:
        print()
        print(f"❌ Неожиданная ошибка: {e}")
        print()

if __name__ == "__main__":
    try:
        asyncio.run(check_admins())
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
