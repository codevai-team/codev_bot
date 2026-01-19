#!/usr/bin/env python3
"""
Интерактивный скрипт для добавления проекта в базу данных
"""
import asyncio
import asyncpg
from config import DATABASE_URL

async def add_project_interactive():
    """Интерактивное добавление проекта"""
    
    print("=" * 60)
    print("📝 Добавление нового проекта в портфолио")
    print("=" * 60)
    print()
    
    # Запрашиваем данные у пользователя
    title = input("📄 Введите название проекта: ").strip()
    if not title:
        print("❌ Название обязательно!")
        return
    
    description = input("📝 Введите описание проекта (Enter для пропуска): ").strip()
    description = description if description else None
    
    project_url = input("🔗 Введите ссылку на проект (Enter для пропуска): ").strip()
    project_url = project_url if project_url else None
    
    image_url = input("🖼️  Введите ссылку на изображение (Enter для пропуска): ").strip()
    image_url = image_url if image_url else None
    
    print()
    print("-" * 60)
    print("Проверьте данные:")
    print(f"  Название: {title}")
    print(f"  Описание: {description or '(не указано)'}")
    print(f"  Ссылка: {project_url or '(не указана)'}")
    print(f"  Изображение: {image_url or '(не указано)'}")
    print("-" * 60)
    
    confirm = input("\n✅ Добавить проект? (y/n): ").strip().lower()
    if confirm != 'y':
        print("❌ Отменено")
        return
    
    try:
        # Подключаемся к базе данных
        print("\n🔄 Подключение к базе данных...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Добавляем проект
        print("💾 Сохранение проекта...")
        result = await conn.fetchrow("""
            INSERT INTO projects (title, description, image_url, project_url) 
            VALUES ($1, $2, $3, $4)
            RETURNING id, title, created_at
        """, title, description, image_url, project_url)
        
        print()
        print("=" * 60)
        print("✅ Проект успешно добавлен!")
        print("=" * 60)
        print(f"  🆔 ID: {result['id']}")
        print(f"  📄 Название: {result['title']}")
        print(f"  📅 Создан: {result['created_at'].strftime('%d.%m.%Y %H:%M')}")
        print()
        print(f"🌐 Проект будет виден на сайте: https://ваш-домен.com")
        print()
        
        # Закрываем соединение
        await conn.close()
        
    except Exception as e:
        print()
        print(f"❌ Ошибка при добавлении проекта: {e}")
        print()

if __name__ == "__main__":
    try:
        asyncio.run(add_project_interactive())
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
