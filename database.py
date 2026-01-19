import asyncpg
import logging
from typing import Optional, List, Dict, Any
from config import DATABASE_URL

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self):
        """Подключение к базе данных"""
        try:
            self.pool = await asyncpg.create_pool(DATABASE_URL)
            logger.info("Подключение к базе данных установлено")
        except Exception as e:
            logger.error(f"Ошибка подключения к базе данных: {e}")
            raise
    
    async def disconnect(self):
        """Отключение от базы данных"""
        if self.pool:
            await self.pool.close()
            logger.info("Подключение к базе данных закрыто")
    
    async def get_admin_telegram_ids(self) -> List[str]:
        """Получить список Telegram ID администраторов из БД"""
        import json
        try:
            async with self.pool.acquire() as conn:
                result = await conn.fetchval(
                    "SELECT value FROM settings WHERE key = 'admin_telegram_ids'"
                )
                if result:
                    try:
                        parsed = json.loads(result)
                        # Убеждаемся что это список
                        if isinstance(parsed, list):
                            return [str(id) for id in parsed]  # Конвертируем все в строки
                        else:
                            logger.warning(f"admin_telegram_ids не является списком: {type(parsed)}")
                            return []
                    except (json.JSONDecodeError, TypeError) as e:
                        logger.error(f"Ошибка парсинга admin_telegram_ids: {e}")
                        return []
                return []
        except Exception as e:
            logger.error(f"Ошибка получения admin_telegram_ids: {e}")
            return []
    
    async def update_admin_telegram_ids(self, admin_ids: List[str]) -> bool:
        """Обновить список Telegram ID администраторов в БД"""
        import json
        try:
            async with self.pool.acquire() as conn:
                await conn.execute(
                    """
                    INSERT INTO settings (key, value) 
                    VALUES ('admin_telegram_ids', $1)
                    ON CONFLICT (key) 
                    DO UPDATE SET value = $1
                    """,
                    json.dumps(admin_ids)
                )
                return True
        except Exception as e:
            logger.error(f"Ошибка обновления админов: {e}")
            return False
    
    async def add_admin_telegram_id(self, telegram_id: str) -> bool:
        """Добавить новый Telegram ID администратора"""
        current_ids = await self.get_admin_telegram_ids()
        if telegram_id not in current_ids:
            current_ids.append(telegram_id)
            return await self.update_admin_telegram_ids(current_ids)
        return True
    
    async def remove_admin_telegram_id(self, telegram_id: str) -> bool:
        """Удалить Telegram ID администратора"""
        current_ids = await self.get_admin_telegram_ids()
        if telegram_id in current_ids:
            current_ids.remove(telegram_id)
            return await self.update_admin_telegram_ids(current_ids)
        return True
    
    async def update_admin_telegram_id(self, index: int, new_telegram_id: str) -> bool:
        """Обновить конкретный Telegram ID администратора по индексу"""
        current_ids = await self.get_admin_telegram_ids()
        if 0 <= index < len(current_ids):
            current_ids[index] = new_telegram_id
            return await self.update_admin_telegram_ids(current_ids)
        return False
    
    async def is_admin(self, telegram_id: int) -> bool:
        """Проверить, является ли пользователь админом"""
        admin_ids = await self.get_admin_telegram_ids()
        return str(telegram_id) in admin_ids
    
    async def get_menu_photo(self) -> Optional[str]:
        """Получить ссылку на фото меню из настроек"""
        async with self.pool.acquire() as conn:
            result = await conn.fetch(
                "SELECT value FROM settings WHERE key = 'menu_photo'"
            )
            if result and result[0]['value']:
                return result[0]['value']
            return None
    
    async def get_projects(self) -> List[Dict[str, Any]]:
        """Получить все проекты"""
        async with self.pool.acquire() as conn:
            result = await conn.fetch("""
                SELECT id, title, description, image_url, project_url, created_at, updated_at 
                FROM projects 
                ORDER BY created_at DESC
            """)
            return [dict(row) for row in result]
    
    async def get_project(self, project_id: int) -> Optional[Dict[str, Any]]:
        """Получить проект по ID"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                SELECT id, title, description, image_url, project_url, created_at, updated_at 
                FROM projects 
                WHERE id = $1
            """, project_id)
            return dict(result) if result else None
    
    async def add_project(self, title: str, description: str = None, image_url: str = None, project_url: str = None) -> int:
        """Добавить новый проект"""
        async with self.pool.acquire() as conn:
            result = await conn.fetchrow("""
                INSERT INTO projects (title, description, image_url, project_url) 
                VALUES ($1, $2, $3, $4)
                RETURNING id
            """, title, description, image_url, project_url)
            return result['id']
    
    async def update_project(self, project_id: int, title: str = None, 
                           description: str = None, image_url: str = None, project_url: str = None) -> bool:
        """Обновить проект"""
        try:
            async with self.pool.acquire() as conn:
                # Получаем текущие данные
                current = await self.get_project(project_id)
                if not current:
                    return False
                
                # Обновляем только переданные поля
                new_title = title if title is not None else current['title']
                new_description = description if description is not None else current['description']
                new_image_url = image_url if image_url is not None else current['image_url']
                new_project_url = project_url if project_url is not None else current.get('project_url')
                
                await conn.execute("""
                    UPDATE projects 
                    SET title = $1, description = $2, image_url = $3, project_url = $4
                    WHERE id = $5
                """, new_title, new_description, new_image_url, new_project_url, project_id)
                return True
        except Exception as e:
            logger.error(f"Ошибка обновления проекта: {e}")
            return False
    
    async def delete_project(self, project_id: int) -> bool:
        """Удалить проект"""
        try:
            async with self.pool.acquire() as conn:
                result = await conn.execute("DELETE FROM projects WHERE id = $1", project_id)
                return result.split()[-1] == '1'  # Проверяем, что удалили одну запись
        except Exception as e:
            logger.error(f"Ошибка удаления проекта: {e}")
            return False

# Глобальный экземпляр базы данных
db = Database()

