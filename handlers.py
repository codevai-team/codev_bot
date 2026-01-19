import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InputMediaPhoto
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from database import db
from config import imgbb_uploader
from keyboards import (
    get_admin_menu, get_projects_menu, get_project_menu, 
    get_edit_project_menu, get_confirm_delete_menu, 
    get_cancel_menu, get_back_to_main_menu, get_admin_management_menu,
    get_admin_list_menu, get_admin_delete_menu, get_confirm_delete_admin_menu
)

logger = logging.getLogger(__name__)

# Состояния для FSM
class ProjectStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_description = State()
    waiting_for_project_url = State()
    waiting_for_image = State()
    editing_title = State()
    editing_description = State()
    editing_project_url = State()
    editing_image = State()

class AdminStates(StatesGroup):
    adding_admin = State()
    editing_admin = State()

router = Router()

# Проверка на админа
async def is_admin_user(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом"""
    return await db.is_admin(user_id)

# Вспомогательные функции для отправки сообщений с фото
async def send_message_with_menu_photo(message: Message, text: str, reply_markup=None, parse_mode=None):
    """Отправляет сообщение с фото из настроек menu_photo, если оно есть"""
    menu_photo = await db.get_menu_photo()
    
    if menu_photo:
        try:
            return await message.answer_photo(
                photo=menu_photo,
                caption=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode
            )
        except Exception as e:
            logger.error(f"Ошибка отправки фото: {e}")
            # Если не удалось отправить с фото, отправляем обычное сообщение
            return await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        return await message.answer(text, reply_markup=reply_markup, parse_mode=parse_mode)

async def edit_message_with_menu_photo(callback: CallbackQuery, text: str, reply_markup=None, parse_mode=None, save_message_id: bool = False, state: FSMContext = None):
    """Редактирует сообщение с фото из настроек menu_photo, если оно есть"""
    menu_photo = await db.get_menu_photo()
    
    if menu_photo:
        try:
            # Если в сообщении уже есть фото, редактируем медиа
            if callback.message.photo:
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=menu_photo, caption=text, parse_mode=parse_mode),
                    reply_markup=reply_markup
                )
                if save_message_id and state:
                    await save_bot_message_id(state, callback.message.message_id)
            else:
                # Если фото нет, удаляем старое сообщение и отправляем новое с фото
                await callback.message.delete()
                new_message = await callback.message.answer_photo(
                    photo=menu_photo,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
                if save_message_id and state:
                    await save_bot_message_id(state, new_message.message_id)
        except Exception as e:
            logger.error(f"Ошибка редактирования с фото: {e}")
            # Если не удалось отредактировать с фото, редактируем обычный текст
            await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
            if save_message_id and state:
                await save_bot_message_id(state, callback.message.message_id)
    else:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
        if save_message_id and state:
            await save_bot_message_id(state, callback.message.message_id)

async def edit_message_with_project_photo(callback: CallbackQuery, text: str, project_image_url: str = None, reply_markup=None, parse_mode=None):
    """Редактирует сообщение с фото проекта, если оно есть, иначе с фото меню"""
    photo_url = project_image_url or await db.get_menu_photo()
    
    if photo_url:
        try:
            # Если в сообщении уже есть фото, редактируем медиа
            if callback.message.photo:
                await callback.message.edit_media(
                    media=InputMediaPhoto(media=photo_url, caption=text, parse_mode=parse_mode),
                    reply_markup=reply_markup
                )
            else:
                # Если фото нет, удаляем старое сообщение и отправляем новое с фото
                await callback.message.delete()
                await callback.message.answer_photo(
                    photo=photo_url,
                    caption=text,
                    reply_markup=reply_markup,
                    parse_mode=parse_mode
                )
        except Exception as e:
            logger.error(f"Ошибка редактирования с фото: {e}")
            # Если не удалось отредактировать с фото, редактируем обычный текст
            await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)
    else:
        await callback.message.edit_text(text, reply_markup=reply_markup, parse_mode=parse_mode)

async def send_progress_message(message: Message, title: str = "", description: str = "", project_url: str = "", image_status: str = "", reply_markup=None):
    """Отправляет сообщение с прогрессом добавления проекта"""
    progress_text = "➕ **Добавление нового проекта**\n\n"
    
    if title:
        progress_text += f"✅ Название: {title}\n"
    else:
        progress_text += "⏳ Название: _ожидание ввода_\n"
    
    if description:
        progress_text += f"✅ Описание: {description[:50]}{'...' if len(description) > 50 else ''}\n"
    elif title:  # Показываем только если уже есть название
        progress_text += "⏳ Описание: _ожидание ввода_\n"
    
    if project_url:
        progress_text += f"✅ Ссылка на проект: {project_url}\n"
    elif description:  # Показываем только если уже есть описание
        progress_text += "⏳ Ссылка на проект: _ожидание ввода_\n"
    
    if image_status:
        progress_text += f"✅ Изображение: {image_status}\n"
    elif project_url:  # Показываем только если уже есть ссылка
        progress_text += "⏳ Изображение: _ожидание загрузки_\n"
    
    await send_message_with_menu_photo(
        message,
        progress_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def delete_previous_messages(message: Message, state: FSMContext):
    """Удаляет предыдущие сообщения пользователя и бота"""
    try:
        # Удаляем сообщение пользователя
        await message.delete()
        
        # Получаем данные из состояния
        data = await state.get_data()
        bot_message_ids = data.get('bot_message_ids', [])
        
        # Удаляем все предыдущие сообщения бота
        for bot_message_id in bot_message_ids:
            try:
                await message.bot.delete_message(message.chat.id, bot_message_id)
            except Exception as e:
                logger.debug(f"Не удалось удалить сообщение бота {bot_message_id}: {e}")
        
        # Очищаем список ID сообщений бота
        await state.update_data(bot_message_ids=[])
    
    except Exception as e:
        logger.debug(f"Не удалось удалить сообщения: {e}")

async def save_bot_message_id(state: FSMContext, message_id: int):
    """Сохраняет ID сообщения бота для последующего удаления"""
    await state.update_data(bot_message_ids=[message_id])

def escape_markdown(text: str) -> str:
    """Экранирует специальные символы Markdown"""
    if not text:
        return text
    
    # Символы, которые нужно экранировать в MarkdownV2 (убрали точку)
    escape_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '!']
    
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

# Команда /start
@router.message(Command("start"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    
    if await is_admin_user(user_id):
        await send_message_with_menu_photo(
            message,
            f"🎉 Добро пожаловать в админ-панель Codev!\n\n"
            f"👋 Привет, {message.from_user.first_name}!\n"
            f"Здесь вы можете управлять портфолио проектов компании.",
            reply_markup=get_admin_menu()
        )
    else:
        await send_message_with_menu_photo(
            message,
            "❌ У вас нет доступа к этому боту.\n"
            "Обратитесь к администратору для получения доступа."
        )

# Главное меню
@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    await edit_message_with_menu_photo(
        callback,
        "🏠 Главное меню администратора:",
        reply_markup=get_admin_menu()
    )
    await callback.answer()

# Просмотр проектов
@router.callback_query(F.data == "view_projects")
async def view_projects(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    await show_projects_page(callback, page=0)

# Просмотр проектов с пагинацией
@router.callback_query(F.data.startswith("projects_page_"))
async def view_projects_page(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    page = int(callback.data.split("_")[-1])
    await show_projects_page(callback, page)

# Обработчик для кнопки индикатора страницы (ничего не делает)
@router.callback_query(F.data == "current_page")
async def current_page_handler(callback: CallbackQuery):
    await callback.answer()

async def show_projects_page(callback: CallbackQuery, page: int):
    """Показать страницу проектов с пагинацией"""
    projects = await db.get_projects()
    
    if not projects:
        await edit_message_with_menu_photo(
            callback,
            "📂 Список проектов пуст.\n"
            "Добавьте первый проект!",
            reply_markup=get_back_to_main_menu()
        )
        await callback.answer()
        return
    
    # Пагинация: 10 проектов на страницу
    projects_per_page = 10
    total_pages = (len(projects) + projects_per_page - 1) // projects_per_page
    
    # Проверяем корректность номера страницы
    if page < 0:
        page = 0
    elif page >= total_pages:
        page = total_pages - 1
    
    # Получаем проекты для текущей страницы
    start_idx = page * projects_per_page
    end_idx = start_idx + projects_per_page
    page_projects = projects[start_idx:end_idx]
    
    await edit_message_with_menu_photo(
        callback,
        f"📂 Список проектов ({len(projects)} шт.)\n"
        f"Страница {page + 1} из {total_pages}:",
        reply_markup=get_projects_menu(page_projects, page, total_pages)
    )
    
    await callback.answer()

# Просмотр конкретного проекта
@router.callback_query(F.data.startswith("project_"))
async def view_project(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    project_id = int(callback.data.split("_")[1])
    project = await db.get_project(project_id)
    
    if not project:
        await callback.answer("❌ Проект не найден!", show_alert=True)
        return
    
    title_escaped = escape_markdown(project['title'])
    text = f"📄 **{title_escaped}**\n\n"
    
    if project['description']:
        desc_escaped = escape_markdown(project['description'])
        text += f"📝 Описание:\n{desc_escaped}\n\n"
    
    if project.get('project_url'):
        url_escaped = escape_markdown(project['project_url'])
        text += f"🔗 Ссылка на проект: {url_escaped}\n\n"
    
    text += f"📅 Создан: {project['created_at'].strftime('%d.%m.%Y %H:%M')}"
    
    await edit_message_with_project_photo(
        callback,
        text,
        project_image_url=project['image_url'],
        reply_markup=get_project_menu(project_id),
        parse_mode="Markdown"
    )
    await callback.answer()

# Добавление проекта
@router.callback_query(F.data == "add_project")
async def add_project_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    await state.set_state(ProjectStates.waiting_for_title)
    
    # Редактируем текущее сообщение
    await edit_message_with_menu_photo(
        callback,
        "➕ **Добавление нового проекта**\n\n"
        "📝 Введите название проекта:",
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown",
        save_message_id=True,
        state=state
    )
    await callback.answer()

@router.message(StateFilter(ProjectStates.waiting_for_title))
async def add_project_title(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    # Сохраняем название
    await state.update_data(title=message.text)
    await state.set_state(ProjectStates.waiting_for_description)
    
    # Отправляем прогресс с запросом описания
    title_escaped = escape_markdown(message.text)
    progress_text = ("➕ **Добавление нового проекта**\n\n"
                    f"✅ Название: {title_escaped}\n"
                    "⏳ Описание: _ожидание ввода_\n\n"
                    "📝 Введите описание проекта (или отправьте /skip чтобы пропустить):")
    
    bot_message = await send_message_with_menu_photo(
        message,
        progress_text,
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown"
    )
    
    # Сохраняем ID сообщения бота для последующего удаления
    if hasattr(bot_message, 'message_id'):
        await save_bot_message_id(state, bot_message.message_id)

@router.message(StateFilter(ProjectStates.waiting_for_description))
async def add_project_description(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    # Сохраняем описание
    description = None if message.text == "/skip" else message.text
    await state.update_data(description=description)
    await state.set_state(ProjectStates.waiting_for_project_url)
    
    # Получаем текущие данные
    data = await state.get_data()
    
    # Отправляем прогресс с запросом ссылки на проект
    title_escaped = escape_markdown(data['title'])
    progress_text = ("➕ **Добавление нового проекта**\n\n"
                    f"✅ Название: {title_escaped}\n")
    
    if description:
        desc_escaped = escape_markdown(description[:50] + ('...' if len(description) > 50 else ''))
        progress_text += f"✅ Описание: {desc_escaped}\n"
    else:
        progress_text += "✅ Описание: _пропущено_\n"
    
    progress_text += ("⏳ Ссылка на проект: _ожидание ввода_\n\n"
                     "🔗 Введите ссылку на проект (или отправьте /skip чтобы пропустить):")
    
    bot_message = await send_message_with_menu_photo(
        message,
        progress_text,
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown"
    )
    
    # Сохраняем ID сообщения бота
    if hasattr(bot_message, 'message_id'):
        await save_bot_message_id(state, bot_message.message_id)

@router.message(StateFilter(ProjectStates.waiting_for_project_url))
async def add_project_url(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    # Сохраняем ссылку на проект
    project_url = None if message.text == "/skip" else message.text
    await state.update_data(project_url=project_url)
    await state.set_state(ProjectStates.waiting_for_image)
    
    # Получаем текущие данные
    data = await state.get_data()
    
    # Отправляем прогресс с запросом изображения
    title_escaped = escape_markdown(data['title'])
    progress_text = ("➕ **Добавление нового проекта**\n\n"
                    f"✅ Название: {title_escaped}\n")
    
    description = data.get('description')
    if description:
        desc_escaped = escape_markdown(description[:50] + ('...' if len(description) > 50 else ''))
        progress_text += f"✅ Описание: {desc_escaped}\n"
    else:
        progress_text += "✅ Описание: _пропущено_\n"
    
    if project_url:
        url_escaped = escape_markdown(project_url)
        progress_text += f"✅ Ссылка на проект: {url_escaped}\n"
    else:
        progress_text += "✅ Ссылка на проект: _пропущено_\n"
    
    progress_text += ("⏳ Изображение: _ожидание загрузки_\n\n"
                     "📎 Отправьте изображение проекта (фото) или /skip чтобы пропустить:")
    
    bot_message = await send_message_with_menu_photo(
        message,
        progress_text,
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown"
    )
    
    # Сохраняем ID сообщения бота
    if hasattr(bot_message, 'message_id'):
        await save_bot_message_id(state, bot_message.message_id)

@router.message(StateFilter(ProjectStates.waiting_for_image))
async def add_project_image(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    image_url = None
    
    # Проверяем, отправил ли пользователь фото
    if message.photo and imgbb_uploader:
        try:
            # Показываем прогресс загрузки
            progress_message = await send_message_with_menu_photo(
                message,
                "📤 **Загрузка изображения...**\n\nПожалуйста, подождите.",
                parse_mode="Markdown"
            )
            
            # Получаем самое большое фото
            photo = message.photo[-1]
            
            # Загружаем в imgbb
            image_url = await imgbb_uploader.upload_from_telegram_photo(
                message.bot, 
                photo.file_id, 
                f"project_{message.from_user.id}_{photo.file_id}"
            )
            
            # Удаляем сообщение о загрузке
            if hasattr(progress_message, 'message_id'):
                try:
                    await message.bot.delete_message(message.chat.id, progress_message.message_id)
                except:
                    pass
                    
            if not image_url:
                await send_message_with_menu_photo(
                    message,
                    "❌ **Ошибка загрузки изображения**\n\n"
                    "Не удалось загрузить изображение. Проект будет создан без изображения.",
                    parse_mode="Markdown"
                )
                
        except Exception as e:
            logger.error(f"Ошибка загрузки изображения: {e}")
            
    elif message.text and message.text != "/skip":
        # Если отправлена ссылка вместо фото
        await send_message_with_menu_photo(
            message,
            "❌ **Неверный формат**\n\n"
            "Пожалуйста, отправьте изображение как фото, а не как ссылку.",
            reply_markup=get_cancel_menu(),
            parse_mode="Markdown"
        )
        return
    
    # Получаем данные и создаем проект
    data = await state.get_data()
    
    try:
        project_id = await db.add_project(
            title=data['title'],
            description=data.get('description'),
            project_url=data.get('project_url'),
            image_url=image_url
        )
        
        # Показываем итоговый результат
        result_text = "✅ **Проект успешно добавлен!**\n\n"
        result_text += f"🆔 ID: {project_id}\n"
        
        title_escaped = escape_markdown(data['title'])
        result_text += f"📄 Название: {title_escaped}\n"
        
        if data.get('description'):
            desc_escaped = escape_markdown(data['description'][:100] + ('...' if len(data['description']) > 100 else ''))
            result_text += f"📝 Описание: {desc_escaped}\n"
        
        if data.get('project_url'):
            url_escaped = escape_markdown(data['project_url'])
            result_text += f"🔗 Ссылка: {url_escaped}\n"
            
        if image_url:
            result_text += f"🖼️ Изображение: загружено\n"
        
        await send_message_with_menu_photo(
            message,
            result_text,
            reply_markup=get_back_to_main_menu(),
            parse_mode="Markdown"
        )
        
    except Exception as e:
        logger.error(f"Ошибка добавления проекта: {e}")
        await send_message_with_menu_photo(
            message,
            "❌ Произошла ошибка при добавлении проекта.",
            reply_markup=get_back_to_main_menu()
        )
    
    await state.clear()

# Редактирование проекта
@router.callback_query(F.data.startswith("edit_project_") & ~F.data.startswith("edit_project_url_"))
async def edit_project_menu(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    project_id = int(callback.data.split("_")[2])
    project = await db.get_project(project_id)
    
    if not project:
        await callback.answer("❌ Проект не найден!", show_alert=True)
        return
    
    # Редактируем текущее сообщение
    title_escaped = escape_markdown(project['title'])
    await edit_message_with_menu_photo(
        callback,
        f"✏️ **Редактирование проекта**\n\n"
        f"📄 {title_escaped}\n\n"
        f"Выберите что хотите изменить:",
        reply_markup=get_edit_project_menu(project_id),
        parse_mode="Markdown"
    )
    await callback.answer()

# Удаление проекта
@router.callback_query(F.data.startswith("delete_project_"))
async def delete_project_confirm(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    project_id = int(callback.data.split("_")[2])
    project = await db.get_project(project_id)
    
    if not project:
        await callback.answer("❌ Проект не найден!", show_alert=True)
        return
    
    await edit_message_with_menu_photo(
        callback,
        f"🗑️ **Удаление проекта**\n\n"
        f"📄 {project['title']}\n\n"
        f"⚠️ Вы уверены, что хотите удалить этот проект?\n"
        f"Это действие нельзя отменить!",
        reply_markup=get_confirm_delete_menu(project_id),
        parse_mode="Markdown"
    )
    await callback.answer()

@router.callback_query(F.data.regexp(r"^confirm_delete_\d+$"))
async def delete_project_final(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    project_id = int(callback.data.split("_")[2])
    
    if await db.delete_project(project_id):
        await edit_message_with_menu_photo(
            callback,
            "✅ Проект успешно удален!",
            reply_markup=get_back_to_main_menu()
        )
    else:
        await edit_message_with_menu_photo(
            callback,
            "❌ Ошибка при удалении проекта.",
            reply_markup=get_back_to_main_menu()
        )
    
    await callback.answer()

# Редактирование названия
@router.callback_query(F.data.startswith("edit_title_"))
async def edit_title_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    project_id = int(callback.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await state.set_state(ProjectStates.editing_title)
    
    # Редактируем текущее сообщение
    await edit_message_with_menu_photo(
        callback,
        "✏️ **Редактирование названия**\n\n"
        "📝 Введите новое название проекта:",
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown",
        save_message_id=True,
        state=state
    )
    await callback.answer()

@router.message(StateFilter(ProjectStates.editing_title))
async def edit_title_save(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    data = await state.get_data()
    project_id = data['project_id']
    
    if await db.update_project(project_id, title=message.text):
        title_escaped = escape_markdown(message.text)
        await send_message_with_menu_photo(
            message,
            f"✅ Название проекта обновлено!\n\n"
            f"📄 Новое название: {title_escaped}",
            reply_markup=get_back_to_main_menu(),
            parse_mode="Markdown"
        )
    else:
        await send_message_with_menu_photo(
            message,
            "❌ Ошибка при обновлении названия.",
            reply_markup=get_back_to_main_menu()
        )
    
    await state.clear()

# Редактирование ссылки на проект
@router.callback_query(F.data.startswith("edit_project_url_"))
async def edit_project_url_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    project_id = int(callback.data.split("_")[3])
    await state.update_data(project_id=project_id)
    await state.set_state(ProjectStates.editing_project_url)
    
    # Редактируем текущее сообщение
    await edit_message_with_menu_photo(
        callback,
        "🔗 **Редактирование ссылки на проект**\n\n"
        "Введите новую ссылку на проект:",
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown",
        save_message_id=True,
        state=state
    )
    await callback.answer()

@router.message(StateFilter(ProjectStates.editing_project_url))
async def edit_project_url_save(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    data = await state.get_data()
    project_id = data['project_id']
    
    if await db.update_project(project_id, project_url=message.text):
        url_escaped = escape_markdown(message.text)
        await send_message_with_menu_photo(
            message,
            f"✅ Ссылка на проект обновлена!\n\n"
            f"🔗 Новая ссылка: {url_escaped}",
            reply_markup=get_back_to_main_menu(),
            parse_mode="Markdown"
        )
    else:
        await send_message_with_menu_photo(
            message,
            "❌ Ошибка при обновлении ссылки.",
            reply_markup=get_back_to_main_menu()
        )
    
    await state.clear()

# Редактирование описания проекта
@router.callback_query(F.data.startswith("edit_description_"))
async def edit_description_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    project_id = int(callback.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await state.set_state(ProjectStates.editing_description)
    
    # Редактируем текущее сообщение
    await edit_message_with_menu_photo(
        callback,
        "📝 **Редактирование описания**\n\n"
        "Введите новое описание проекта:",
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown",
        save_message_id=True,
        state=state
    )
    await callback.answer()

@router.message(StateFilter(ProjectStates.editing_description))
async def edit_description_save(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    data = await state.get_data()
    project_id = data['project_id']
    
    if await db.update_project(project_id, description=message.text):
        desc_escaped = escape_markdown(message.text[:100] + ('...' if len(message.text) > 100 else ''))
        await send_message_with_menu_photo(
            message,
            f"✅ Описание проекта обновлено!\n\n"
            f"📝 Новое описание: {desc_escaped}",
            reply_markup=get_back_to_main_menu(),
            parse_mode="Markdown"
        )
    else:
        await send_message_with_menu_photo(
            message,
            "❌ Ошибка при обновлении описания.",
            reply_markup=get_back_to_main_menu()
        )
    
    await state.clear()

# Редактирование изображения проекта
@router.callback_query(F.data.startswith("edit_image_"))
async def edit_image_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    project_id = int(callback.data.split("_")[2])
    await state.update_data(project_id=project_id)
    await state.set_state(ProjectStates.editing_image)
    
    # Редактируем текущее сообщение
    await edit_message_with_menu_photo(
        callback,
        "🖼️ **Редактирование изображения**\n\n"
        "📎 Отправьте новое изображение проекта (фото):",
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown",
        save_message_id=True,
        state=state
    )
    await callback.answer()

@router.message(StateFilter(ProjectStates.editing_image))
async def edit_image_save(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    data = await state.get_data()
    project_id = data['project_id']
    
    image_url = None
    
    # Проверяем, отправил ли пользователь фото
    if message.photo and imgbb_uploader:
        try:
            # Показываем прогресс загрузки
            progress_message = await send_message_with_menu_photo(
                message,
                "📤 **Загрузка изображения...**\n\nПожалуйста, подождите.",
                parse_mode="Markdown"
            )
            
            # Получаем самое большое фото
            photo = message.photo[-1]
            
            # Загружаем в imgbb
            image_url = await imgbb_uploader.upload_from_telegram_photo(
                message.bot, 
                photo.file_id, 
                f"project_edit_{project_id}_{photo.file_id}"
            )
            
            # Удаляем сообщение о загрузке
            if hasattr(progress_message, 'message_id'):
                try:
                    await message.bot.delete_message(message.chat.id, progress_message.message_id)
                except:
                    pass
                    
            if not image_url:
                await send_message_with_menu_photo(
                    message,
                    "❌ **Ошибка загрузки изображения**\n\n"
                    "Не удалось загрузить изображение. Попробуйте еще раз.",
                    reply_markup=get_back_to_main_menu(),
                    parse_mode="Markdown"
                )
                await state.clear()
                return
                
        except Exception as e:
            logger.error(f"Ошибка загрузки изображения: {e}")
            await send_message_with_menu_photo(
                message,
                "❌ **Ошибка загрузки изображения**\n\n"
                "Произошла ошибка при загрузке. Попробуйте еще раз.",
                reply_markup=get_back_to_main_menu(),
                parse_mode="Markdown"
            )
            await state.clear()
            return
    else:
        # Если не отправлено фото
        await send_message_with_menu_photo(
            message,
            "❌ **Неверный формат**\n\n"
            "Пожалуйста, отправьте изображение как фото.",
            reply_markup=get_cancel_menu(),
            parse_mode="Markdown"
        )
        return
    
    # Обновляем проект
    if await db.update_project(project_id, image_url=image_url):
        await send_message_with_menu_photo(
            message,
            "✅ **Изображение проекта обновлено!**\n\n"
            "🖼️ Новое изображение успешно загружено.",
            reply_markup=get_back_to_main_menu(),
            parse_mode="Markdown"
        )
    else:
        await send_message_with_menu_photo(
            message,
            "❌ Ошибка при обновлении изображения в базе данных.",
            reply_markup=get_back_to_main_menu()
        )
    
    await state.clear()

# Команда для добавления админа (супер-секретная)
@router.message(Command("add_admin"))
async def add_admin_command(message: Message):
    # Эта команда доступна только если в базе вообще нет админов
    # или если команду вызывает уже существующий админ
    admin_ids = await db.get_admin_telegram_ids()
    
    # Убеждаемся что admin_ids это список
    if not isinstance(admin_ids, list):
        admin_ids = []
    
    user_id = str(message.from_user.id)
    
    if admin_ids and user_id not in admin_ids:
        await send_message_with_menu_photo(message, "❌ У вас нет прав для добавления админов!")
        return
    
    # Если передан аргумент (ID пользователя)
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    if args:
        try:
            new_admin_id = str(args[0])
            if await db.add_admin_telegram_id(new_admin_id):
                await send_message_with_menu_photo(message, f"✅ Пользователь {new_admin_id} добавлен в админы!")
            else:
                await send_message_with_menu_photo(message, f"ℹ️ Пользователь {new_admin_id} уже является админом!")
        except ValueError:
            await send_message_with_menu_photo(message, "❌ Неверный формат ID!")
    else:
        # Добавляем отправителя как админа
        if await db.add_admin_telegram_id(user_id):
            await send_message_with_menu_photo(message, f"✅ Вы добавлены в админы!")
            # Показываем главное меню
            await send_message_with_menu_photo(
                message,
                "🎉 Добро пожаловать в админ-панель Codev!",
                reply_markup=get_admin_menu()
            )
        else:
            await send_message_with_menu_photo(message, "ℹ️ Вы уже являетесь админом!")

# Отмена операции
@router.callback_query(F.data == "cancel", StateFilter("*"))
async def cancel_operation(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await back_to_main(callback)

# ================================
# УПРАВЛЕНИЕ АДМИНИСТРАТОРАМИ
# ================================

# Управление админами - главное меню
@router.callback_query(F.data == "manage_admins")
async def manage_admins(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    admin_ids = await db.get_admin_telegram_ids()
    
    # Формируем текст со списком админов
    admin_list_text = ""
    if admin_ids:
        for i, admin_id in enumerate(admin_ids, 1):
            admin_list_text += f"{i}. {admin_id}\n"
    else:
        admin_list_text = "Нет администраторов"
    
    await edit_message_with_menu_photo(
        callback,
        f"🔧 **Управление администраторами**\n\n"
        f"📋 **Список администраторов:**\n"
        f"{admin_list_text}\n"
        f"Выберите действие:",
        reply_markup=get_admin_management_menu(),
        parse_mode="Markdown"
    )
    await callback.answer()

# Редактирование админов - показать список
@router.callback_query(F.data == "edit_admins")
async def edit_admins(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    admin_ids = await db.get_admin_telegram_ids()
    
    if not admin_ids:
        await edit_message_with_menu_photo(
            callback,
            "❌ **Нет администраторов для редактирования**\n\n"
            "Сначала добавьте хотя бы одного администратора.",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    await edit_message_with_menu_photo(
        callback,
        "📝 **Редактирование администраторов**\n\n"
        "Выберите номер администратора для изменения:",
        reply_markup=get_admin_list_menu(admin_ids),
        parse_mode="Markdown"
    )
    await callback.answer()

# Редактирование конкретного админа
@router.callback_query(F.data.startswith("edit_admin_"))
async def edit_admin_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    admin_index = int(callback.data.split("_")[2])
    admin_ids = await db.get_admin_telegram_ids()
    
    if admin_index >= len(admin_ids):
        await callback.answer("❌ Администратор не найден!", show_alert=True)
        return
    
    current_admin_id = admin_ids[admin_index]
    await state.update_data(admin_index=admin_index, current_admin_id=current_admin_id)
    await state.set_state(AdminStates.editing_admin)
    
    await edit_message_with_menu_photo(
        callback,
        f"✏️ **Редактирование администратора**\n\n"
        f"📋 Текущий ID: {current_admin_id}\n\n"
        f"🔢 Введите новый Telegram ID:",
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown",
        save_message_id=True,
        state=state
    )
    await callback.answer()

# Сохранение изменений админа
@router.message(StateFilter(AdminStates.editing_admin))
async def edit_admin_save(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    new_admin_id = escape_markdown(message.text.strip())
    data = await state.get_data()
    admin_index = data.get('admin_index')
    current_admin_id = data.get('current_admin_id')
    
    # Проверяем валидность ID (должен быть числом)
    if not new_admin_id.isdigit():
        new_message = await send_message_with_menu_photo(
            message,
            "❌ **Ошибка!**\n\n"
            "Telegram ID должен содержать только цифры.\n\n"
            f"📋 Текущий ID: {current_admin_id}\n\n"
            "🔢 Введите корректный Telegram ID:",
            reply_markup=get_cancel_menu(),
            parse_mode="Markdown"
        )
        await save_bot_message_id(state, new_message.message_id)
        return
    
    # Обновляем админа
    success = await db.update_admin_telegram_id(admin_index, new_admin_id)
    
    if success:
        await send_message_with_menu_photo(
            message,
            f"✅ **Администратор обновлен!**\n\n"
            f"🔄 Изменено: {current_admin_id} → {new_admin_id}",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
    else:
        await send_message_with_menu_photo(
            message,
            f"❌ **Ошибка обновления!**\n\n"
            f"Не удалось обновить администратора.",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
    
    await state.clear()

# Добавление нового админа
@router.callback_query(F.data == "add_admin")
async def add_admin_start(callback: CallbackQuery, state: FSMContext):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    await state.set_state(AdminStates.adding_admin)
    
    await edit_message_with_menu_photo(
        callback,
        "➕ **Добавление администратора**\n\n"
        "🔢 Введите Telegram ID нового администратора:",
        reply_markup=get_cancel_menu(),
        parse_mode="Markdown",
        save_message_id=True,
        state=state
    )
    await callback.answer()

# Сохранение нового админа
@router.message(StateFilter(AdminStates.adding_admin))
async def add_admin_save(message: Message, state: FSMContext):
    if not await is_admin_user(message.from_user.id):
        await send_message_with_menu_photo(message, "❌ Нет доступа!")
        return
    
    # Удаляем предыдущие сообщения
    await delete_previous_messages(message, state)
    
    new_admin_id = escape_markdown(message.text.strip())
    
    # Проверяем валидность ID (должен быть числом)
    if not new_admin_id.isdigit():
        new_message = await send_message_with_menu_photo(
            message,
            "❌ **Ошибка!**\n\n"
            "Telegram ID должен содержать только цифры.\n\n"
            "🔢 Введите корректный Telegram ID:",
            reply_markup=get_cancel_menu(),
            parse_mode="Markdown"
        )
        await save_bot_message_id(state, new_message.message_id)
        return
    
    # Проверяем, не существует ли уже такой админ
    current_admins = await db.get_admin_telegram_ids()
    if new_admin_id in current_admins:
        await send_message_with_menu_photo(
            message,
            f"⚠️ **Администратор уже существует!**\n\n"
            f"ID {new_admin_id} уже есть в списке администраторов.",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
        await state.clear()
        return
    
    # Добавляем нового админа
    success = await db.add_admin_telegram_id(new_admin_id)
    
    if success:
        await send_message_with_menu_photo(
            message,
            f"✅ **Администратор добавлен!**\n\n"
            f"🆕 Новый админ: {new_admin_id}",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
    else:
        await send_message_with_menu_photo(
            message,
            f"❌ **Ошибка добавления!**\n\n"
            f"Не удалось добавить администратора.",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
    
    await state.clear()

# Удаление админа - показать список
@router.callback_query(F.data == "delete_admin")
async def delete_admin(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    admin_ids = await db.get_admin_telegram_ids()
    
    if not admin_ids:
        await edit_message_with_menu_photo(
            callback,
            "❌ **Нет администраторов для удаления**\n\n"
            "Сначала добавьте хотя бы одного администратора.",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    # Проверяем, что админов больше одного (нельзя удалить последнего)
    if len(admin_ids) <= 1:
        await edit_message_with_menu_photo(
            callback,
            "⚠️ **Нельзя удалить единственного администратора**\n\n"
            "В системе должен остаться хотя бы один администратор.",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    await edit_message_with_menu_photo(
        callback,
        "🗑️ **Удаление администратора**\n\n"
        "⚠️ **Внимание:** Удаление администратора нельзя отменить!\n\n"
        "Выберите номер администратора для удаления:",
        reply_markup=get_admin_delete_menu(admin_ids),
        parse_mode="Markdown"
    )
    await callback.answer()

# Подтверждение удаления конкретного админа
@router.callback_query(F.data.regexp(r"^delete_admin_\d+$"))
async def delete_admin_confirm(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    admin_index = int(callback.data.split("_")[2])
    admin_ids = await db.get_admin_telegram_ids()
    
    if admin_index >= len(admin_ids):
        await callback.answer("❌ Администратор не найден!", show_alert=True)
        return
    
    admin_to_delete = admin_ids[admin_index]
    current_user_id = str(callback.from_user.id)
    
    # Проверяем, не пытается ли пользователь удалить самого себя
    if admin_to_delete == current_user_id:
        await edit_message_with_menu_photo(
            callback,
            "❌ **Нельзя удалить самого себя**\n\n"
            "Вы не можете удалить свой собственный аккаунт администратора.",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
        await callback.answer()
        return
    
    await edit_message_with_menu_photo(
        callback,
        f"🗑️ **Подтверждение удаления**\n\n"
        f"📋 Администратор: {admin_to_delete}\n\n"
        f"⚠️ **Вы уверены, что хотите удалить этого администратора?**\n"
        f"Это действие нельзя отменить!",
        reply_markup=get_confirm_delete_admin_menu(admin_index),
        parse_mode="Markdown"
    )
    await callback.answer()

# Финальное удаление админа
@router.callback_query(F.data.startswith("confirm_delete_admin_"))
async def delete_admin_final(callback: CallbackQuery):
    if not await is_admin_user(callback.from_user.id):
        await callback.answer("❌ Нет доступа!", show_alert=True)
        return
    
    admin_index = int(callback.data.split("_")[3])
    admin_ids = await db.get_admin_telegram_ids()
    
    if admin_index >= len(admin_ids):
        await callback.answer("❌ Администратор не найден!", show_alert=True)
        return
    
    admin_to_delete = admin_ids[admin_index]
    
    # Удаляем администратора
    success = await db.remove_admin_telegram_id(admin_to_delete)
    
    if success:
        await edit_message_with_menu_photo(
            callback,
            f"✅ **Администратор удален!**\n\n"
            f"🗑️ Удален: {admin_to_delete}\n\n"
            f"📊 Осталось администраторов: {len(admin_ids) - 1}",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
    else:
        await edit_message_with_menu_photo(
            callback,
            f"❌ **Ошибка удаления!**\n\n"
            f"Не удалось удалить администратора.",
            reply_markup=get_admin_management_menu(),
            parse_mode="Markdown"
        )
    
    await callback.answer()

