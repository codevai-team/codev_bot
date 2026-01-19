#!/usr/bin/env python3
"""
Пример добавления проекта Cosmonaft
Скопируйте этот файл и измените данные для вашего проекта
"""
import asyncio
import asyncpg
from config import DATABASE_URL

async def add_cosmonaft_project():
    """Добавить проект Cosmonaft в базу данных"""
    
    # ========================================
    # ИЗМЕНИТЕ ЭТИ ДАННЫЕ ДЛЯ ВАШЕГО ПРОЕКТА
    # ========================================
    
    project_data = {
        "title": "Cosmonaft",
        "description": "Интернет-магазин космической тематики с уникальным дизайном и широким ассортиментом товаров для любителей космоса",
        "project_url": "https://cosmonaft.vercel.app",
        "image_url": "https://i.ibb.co/xxx/cosmonaft.png"  # Замените на реальную ссылку
    }
    
    # ========================================
    
    print("=" * 70)
    print("🚀 Добавление проекта в портфолио")
    print("=" * 70)
    print()
    print(f"📄 Название: {project_data['title']}")
    print(f"📝 Описание: {project_data['description']}")
    print(f"🔗 Ссылка: {project_data['project_url']}")
    print(f"🖼️  Изображение: {project_data['image_url']}")
    print()
    print("-" * 70)
    
    try:
        # Подключаемся к базе данных
        print("🔄 Подключение к базе данных...")
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Проверяем, не существует ли уже проект с таким названием
        existing = await conn.fetchval(
            "SELECT id FROM projects WHERE title = $1",
            project_data['title']
        )
        
        if existing:
            print(f"⚠️  Проект '{project_data['title']}' уже существует (ID: {existing})")
            print("   Хотите обновить его? (y/n): ", end="")
            
            # В автоматическом режиме пропускаем
            print("n (автоматический режим)")
            await conn.close()
            return
        
        # Добавляем проект
        print("💾 Сохранение проекта в базу данных...")
        result = await conn.fetchrow("""
            INSERT INTO projects (title, description, image_url, project_url) 
            VALUES ($1, $2, $3, $4)
            RETURNING id, title, created_at
        """, 
            project_data['title'],
            project_data['description'],
            project_data['image_url'],
            project_data['project_url']
        )
        
        print()
        print("=" * 70)
        print("✅ Проект успешно добавлен!")
        print("=" * 70)
        print(f"  🆔 ID в базе данных: {result['id']}")
        print(f"  📄 Название: {result['title']}")
        print(f"  📅 Дата создания: {result['created_at'].strftime('%d.%m.%Y %H:%M:%S')}")
        print()
        print("🌐 Проект теперь виден на сайте в разделе 'Портфолио'")
        print("🔍 Проверить через API: GET /api/projects")
        print()
        
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
        asyncio.run(add_cosmonaft_project())
    except KeyboardInterrupt:
        print("\n\n❌ Прервано пользователем")
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
