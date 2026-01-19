"""
Модуль для загрузки изображений в imgbb
"""
import aiohttp
import aiofiles
import base64
import logging
from typing import Optional

logger = logging.getLogger(__name__)

class ImgBBUploader:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.imgbb.com/1/upload"
    
    async def upload_from_bytes(self, image_bytes: bytes, name: str = "image") -> Optional[str]:
        """Загрузить изображение из байтов"""
        try:
            # Кодируем изображение в base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            data = {
                'key': self.api_key,
                'image': image_base64,
                'name': name
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(self.base_url, data=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        if result.get('success'):
                            return result['data']['url']
                        else:
                            logger.error(f"Ошибка загрузки в imgbb: {result.get('error', {}).get('message', 'Unknown error')}")
                    else:
                        logger.error(f"HTTP ошибка при загрузке в imgbb: {response.status}")
                        
        except Exception as e:
            logger.error(f"Исключение при загрузке в imgbb: {e}")
        
        return None
    
    async def upload_from_telegram_photo(self, bot, file_id: str, name: str = "telegram_photo") -> Optional[str]:
        """Загрузить фото из Telegram"""
        try:
            # Получаем файл из Telegram
            file = await bot.get_file(file_id)
            
            # Скачиваем файл
            async with aiohttp.ClientSession() as session:
                file_url = f"https://api.telegram.org/file/bot{bot.token}/{file.file_path}"
                async with session.get(file_url) as response:
                    if response.status == 200:
                        image_bytes = await response.read()
                        return await self.upload_from_bytes(image_bytes, name)
                    else:
                        logger.error(f"Не удалось скачать файл из Telegram: {response.status}")
        
        except Exception as e:
            logger.error(f"Ошибка при загрузке фото из Telegram: {e}")
        
        return None

# Глобальный экземпляр (будет инициализирован в config.py)
imgbb_uploader: Optional[ImgBBUploader] = None
