from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def get_admin_menu() -> InlineKeyboardMarkup:
    """Главное меню администратора"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📂 Просмотреть проекты", callback_data="view_projects")],
        [InlineKeyboardButton(text="➕ Добавить проект", callback_data="add_project")],
        [InlineKeyboardButton(text="🔧 Управление админами", callback_data="manage_admins")]
    ])
    return keyboard

def get_projects_menu(projects_list, page: int = 0, total_pages: int = 1) -> InlineKeyboardMarkup:
    """Меню со списком проектов с пагинацией"""
    keyboard = []
    
    # Добавляем проекты
    for project in projects_list:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📄 {project['title']}", 
                callback_data=f"project_{project['id']}"
            )
        ])
    
    # Добавляем кнопки пагинации, если страниц больше одной
    if total_pages > 1:
        pagination_row = []
        
        # Кнопка "Назад"
        if page > 0:
            pagination_row.append(
                InlineKeyboardButton(text="⬅️ Назад", callback_data=f"projects_page_{page-1}")
            )
        
        # Индикатор страницы
        pagination_row.append(
            InlineKeyboardButton(text=f"{page+1}/{total_pages}", callback_data="current_page")
        )
        
        # Кнопка "Вперед"
        if page < total_pages - 1:
            pagination_row.append(
                InlineKeyboardButton(text="Вперед ➡️", callback_data=f"projects_page_{page+1}")
            )
        
        keyboard.append(pagination_row)
    
    # Кнопка возврата
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_project_menu(project_id: int) -> InlineKeyboardMarkup:
    """Меню для управления конкретным проектом"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        # Кнопки Редактировать и Удалить в одной строке
        [
            InlineKeyboardButton(text="✏️ Редактировать", callback_data=f"edit_project_{project_id}"),
            InlineKeyboardButton(text="🗑️ Удалить", callback_data=f"delete_project_{project_id}")
        ],
        [InlineKeyboardButton(text="🔙 К списку проектов", callback_data="view_projects")]
    ])
    return keyboard

def get_edit_project_menu(project_id: int) -> InlineKeyboardMarkup:
    """Меню для редактирования проекта"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Изменить название", callback_data=f"edit_title_{project_id}")],
        [InlineKeyboardButton(text="📄 Изменить описание", callback_data=f"edit_description_{project_id}")],
        [InlineKeyboardButton(text="🔗 Изменить ссылку", callback_data=f"edit_project_url_{project_id}")],
        [InlineKeyboardButton(text="🖼️ Изменить изображение", callback_data=f"edit_image_{project_id}")],
        [InlineKeyboardButton(text="🔙 Назад к проекту", callback_data=f"project_{project_id}")]
    ])
    return keyboard

def get_confirm_delete_menu(project_id: int) -> InlineKeyboardMarkup:
    """Меню подтверждения удаления"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_{project_id}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data=f"project_{project_id}")
        ]
    ])
    return keyboard

def get_cancel_menu() -> InlineKeyboardMarkup:
    """Меню отмены операции"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="back_to_main")]
    ])
    return keyboard

def get_back_to_main_menu() -> InlineKeyboardMarkup:
    """Кнопка возврата в главное меню"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 В главное меню", callback_data="back_to_main")]
    ])
    return keyboard

def get_admin_management_menu() -> InlineKeyboardMarkup:
    """Меню управления администраторами"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Редактировать админов", callback_data="edit_admins")],
        [InlineKeyboardButton(text="➕ Добавить админа", callback_data="add_admin")],
        [InlineKeyboardButton(text="🗑️ Удалить админа", callback_data="delete_admin")],
        [InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main")]
    ])
    return keyboard

def get_admin_list_menu(admin_ids: list) -> InlineKeyboardMarkup:
    """Меню со списком админов для редактирования"""
    keyboard = []
    
    # Добавляем админов с нумерацией
    for i, admin_id in enumerate(admin_ids, 1):
        keyboard.append([
            InlineKeyboardButton(
                text=f"{i}. {admin_id}", 
                callback_data=f"edit_admin_{i-1}"  # Используем индекс
            )
        ])
    
    # Кнопка возврата
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="manage_admins")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_admin_delete_menu(admin_ids: list) -> InlineKeyboardMarkup:
    """Меню со списком админов для удаления"""
    keyboard = []
    
    # Добавляем админов с нумерацией для удаления
    for i, admin_id in enumerate(admin_ids, 1):
        keyboard.append([
            InlineKeyboardButton(
                text=f"🗑️ {i}. {admin_id}", 
                callback_data=f"delete_admin_{i-1}"  # Используем индекс
            )
        ])
    
    # Кнопка возврата
    keyboard.append([
        InlineKeyboardButton(text="🔙 Назад", callback_data="manage_admins")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def get_confirm_delete_admin_menu(admin_index: int) -> InlineKeyboardMarkup:
    """Меню подтверждения удаления администратора"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Да, удалить", callback_data=f"confirm_delete_admin_{admin_index}"),
            InlineKeyboardButton(text="❌ Отмена", callback_data="delete_admin")
        ]
    ])
    return keyboard

