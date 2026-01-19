#!/usr/bin/env python3
"""
Скрипт для ручного добавления проекта в базу данных
"""
import asyncio
import asyncpg
from config import DATABASE_URL

async def add_project():
    """Добавить новый проект в базу данных"""
    
    # Данные нового проекта
    title = "Название вашего проекта"
    description = "Описание проекта - что он делает, какие технологии использованы"
    project_url = "https://ваш-сайт.com"
    image_url = "https://ссылка-на-изображение.com/image.png"  # Или None если нет изображения
    
    try:
        # Подключаемся к базе данных
        conn = await asyncpg.connect(DATABASE_URL)
        
        # Добавляем проект
        result = await conn.fetchrow("""
            INSERT INTO projects (title, description, image_url, project_url) 
            VALUES ($1, $2, $3, $4)
            RETURNING id, title, created_at
        """, title, description, image_url, project_url)
        
        print(f"✅ Проект успешно добавлен!")
        print(f"   ID: {result['id']}")
        print(f"   Название: {result['title']}")
        print(f"   Создан: {result['created_at']}")
        
        # Закрываем соединение
        await conn.close()
        
    except Exception as e:
        print(f"❌ Ошибка при добавлении проекта: {e}")

if __name__ == "__main__":
    asyncio.run(add_project())
