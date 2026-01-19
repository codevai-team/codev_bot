# Деплой на Cloudflare Workers

## Важно!

Cloudflare Workers **не поддерживает Python напрямую**. Ваш бот написан на Python, но Workers работает только с JavaScript/TypeScript.

## Варианты решения:

### Вариант 1: Использовать другую платформу (РЕКОМЕНДУЕТСЯ)

Для Python Telegram ботов лучше подходят:

1. **Render.com** - бесплатный tier, простой деплой
   - Создайте аккаунт на render.com
   - Подключите GitHub репозиторий
   - Выберите "Web Service"
   - Команда запуска: `python main.py`

2. **Railway.app** - очень простой интерфейс
   - Подключите GitHub
   - Railway автоматически определит Python
   - Добавьте переменные окружения

3. **PythonAnywhere** - специально для Python
   - Бесплатный план доступен
   - Поддержка long-running процессов

### Вариант 2: Переписать бота на JavaScript

Если вы хотите использовать Cloudflare Workers, нужно:
1. Переписать всю логику на JavaScript
2. Использовать библиотеку `grammy` или `telegraf`
3. Настроить webhook вместо long polling
4. Использовать Cloudflare D1 вместо PostgreSQL

## Текущая конфигурация

Создан базовый JavaScript worker в `src/index.js`, но он пока не содержит логику вашего бота.

## Что делать дальше?

1. Выберите платформу для деплоя
2. Если выбрали Render/Railway - используйте файлы `render.yaml` или `railway.json`
3. Если хотите Cloudflare - нужно переписать на JavaScript

## Переменные окружения

Не забудьте добавить в выбранной платформе:
- `BOT_TOKEN` - токен Telegram бота
- `DATABASE_URL` - URL PostgreSQL базы
- `IMGBB_API_KEY` - ключ API ImgBB
- `ADMIN_IDS` - ID администраторов (через запятую)
