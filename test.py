import os
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from telegram.constants import ParseMode

# --- НАСТРОЙКИ ---
BOT_TOKEN = "8360251674:AAGvGDMudrgHwOYHX7ud01GL8S1Ww6ccZso"
ADMIN_FILE = "admins.txt"

# --- ЛОГИКА АДМИНИСТРАТОРОВ ---

def load_admins():
    if not os.path.exists(ADMIN_FILE):
        return []
    with open(ADMIN_FILE, 'r') as f:
        return [int(line.strip()) for line in f if line.strip().isdigit()]

def save_admins(admin_ids):
    with open(ADMIN_FILE, 'w') as f:
        for admin_id in admin_ids:
            f.write(str(admin_id) + '\n')

# --- ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ---

def parse_time(time_string: str) -> datetime.timedelta:
    """Парсит строку времени (10m, 2h, 1d) и возвращает timedelta."""
    unit = time_string[-1].lower()
    value = int(time_string[:-1])
    if unit == 'm':
        return datetime.timedelta(minutes=value)
    elif unit == 'h':
        return datetime.timedelta(hours=value)
    elif unit == 'd':
        return datetime.timedelta(days=value)
    else:
        return datetime.timedelta()

# --- ДЕКОРАТОР ДЛЯ ПРОВЕРКИ ПРАВ АДМИНА ---

def admin_required(func):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        ADMIN_IDS = load_admins()
        user_id = update.effective_user.id
        if not ADMIN_IDS and func.__name__ not in ['start', 'show_menu', 'init_super_admin']:
             await update.callback_query.answer("Администратор еще не назначен. Используйте /init.", show_alert=True)
             return

        if user_id not in ADMIN_IDS:
            # Отвечаем по-разному в зависимости от типа апдейта (сообщение или кнопка)
            if update.callback_query:
                await update.callback_query.answer("У вас нет прав для выполнения этого действия.", show_alert=True)
            else:
                await update.message.reply_text("У вас нет прав для выполнения этой команды.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

# --- ОСНОВНЫЕ КОМАНДЫ И МЕНЮ ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение и меню."""
    await show_menu(update, context)

@admin_required
async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает главное меню с кнопками."""
    keyboard = [
        [InlineKeyboardButton("👮‍♀️ Модерация", callback_data='menu_moderation')],
        [InlineKeyboardButton("👑 Управление админами", callback_data='menu_admins')],
        [InlineKeyboardButton("ℹ️ Информация", callback_data='menu_info')],
        [InlineKeyboardButton("❌ Закрыть", callback_data='close_menu')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = f"👋 **Привет, {update.effective_user.first_name}!**\n\nЯ бот-модератор, готовый к работе. Выберите действие:"
    
    # Если это сообщение, отправляем новое. Если это нажатие кнопки, редактируем старое.
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)

# --- ОБРАБОТЧИКИ КОМАНД МОДЕРАЦИИ (вызываются через reply) ---

@admin_required
async def handle_moderation_command(update: Update, context: ContextTypes.DEFAULT_TYPE, action: str):
    """Общая функция для бана, мута, кика и варна."""
    if not update.message.reply_to_message:
        await update.message.reply_text("⚠️ **Ошибка:** Эту команду нужно использовать в ответ на сообщение пользователя.")
        return

    target_user = update.message.reply_to_message.from_user
    admin_user = update.message.from_user
    chat_id = update.message.chat_id
    reason = " ".join(context.args) if context.args else "Не указана"

    try:
        if action == 'kick':
            await context.bot.kick_chat_member(chat_id, target_user.id)
            await update.message.reply_text(f"👟 Пользователь {target_user.full_name} был исключен админом {admin_user.full_name}.\nПричина: {reason}")
        
        elif action == 'ban':
            await context.bot.ban_chat_member(chat_id, target_user.id)
            await update.message.reply_text(f"🔨 Пользователь {target_user.full_name} забанен навсегда админом {admin_user.full_name}.\nПричина: {reason}")

        elif action == 'mute':
            if not context.args:
                await update.message.reply_text("⚠️ **Ошибка:** Укажите время мута (например, `/mute 10m` или `/mute 2h`).")
                return
            
            duration_str = context.args[0]
            reason = " ".join(context.args[1:]) if len(context.args) > 1 else "Не указана"
            duration = parse_time(duration_str)
            
            if duration.total_seconds() == 0:
                await update.message.reply_text("⚠️ **Ошибка:** Неверный формат времени. Используйте `m` (минуты), `h` (часы), `d` (дни).")
                return

            until_date = datetime.datetime.now() + duration
            await context.bot.restrict_chat_member(
                chat_id, 
                target_user.id, 
                ChatPermissions(can_send_messages=False),
                until_date=until_date
            )
            await update.message.reply_text(f"🔇 Пользователю {target_user.full_name} запрещено писать до {until_date.strftime('%Y-%m-%d %H:%M')}.\nАдмин: {admin_user.full_name}\nПричина: {reason}")

        elif action == 'unmute':
             await context.bot.restrict_chat_member(
                chat_id, 
                target_user.id, 
                ChatPermissions(can_send_messages=True, can_send_media_messages=True, can_send_polls=True, can_send_other_messages=True)
            )
             await update.message.reply_text(f"🔊 Мут с пользователя {target_user.full_name} снят.")

    except Exception as e:
        await update.message.reply_text(f"❌ **Не удалось выполнить действие:** {e}\n\nВозможно, у меня недостаточно прав в этом чате.")

async def kick_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await handle_moderation_command(update, context, 'kick')
async def ban_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await handle_moderation_command(update, context, 'ban')
async def mute_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await handle_moderation_command(update, context, 'mute')
async def unmute_command(update: Update, context: ContextTypes.DEFAULT_TYPE): await handle_moderation_command(update, context, 'unmute')

# --- КОМАНДЫ УПРАВЛЕНИЯ АДМИНАМИ ---
@admin_required
async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код из предыдущей версии) ...
    pass

@admin_required
async def list_admins(update: Update, context: ContextTypes.DEFAULT_TYPE):
    ADMIN_IDS = load_admins()
    if not ADMIN_IDS:
        await update.message.reply_text("Список админов пуст.")
        return
    
    admin_list_text = "👑 **Текущие администраторы бота:**\n"
    for admin_id in ADMIN_IDS:
        try:
            user = await context.bot.get_chat(admin_id)
            admin_list_text += f"- {user.full_name} (`{admin_id}`)\n"
        except Exception:
            admin_list_text += f"- *Не удалось получить инфо* (`{admin_id}`)\n"
            
    await update.message.reply_text(admin_list_text, parse_mode=ParseMode.MARKDOWN)

# --- ИНИЦИАЛИЗАЦИЯ И ИНФО ---

async def init_super_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # ... (код из предыдущей версии) ...
    pass

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет ID пользователя и чата."""
    await update.message.reply_text(f"👤 Ваш ID: `{update.effective_user.id}`\n💬 ID чата: `{update.effective_chat.id}`", parse_mode=ParseMode.MARKDOWN)


# --- ОБРАБОТЧИК НАЖАТИЙ НА КНОПКИ (CALLBACKS) ---

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает все нажатия на inline-кнопки."""
    query = update.callback_query
    await query.answer()  # Обязательно, чтобы у пользователя пропала анимация загрузки
    
    data = query.data

    if data == 'close_menu':
        await query.edit_message_text("Меню закрыто.")
        return
        
    if data == 'main_menu':
        await show_menu(update, context)
        return

    # --- Навигация по меню ---
    if data == 'menu_moderation':
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data='main_menu')]
        ]
        text = """
👮‍♀️ **Меню модерации**

Используйте эти команды в ответ на сообщение пользователя:
- `/kick [причина]` - исключить
- `/ban [причина]` - забанить навсегда
- `/mute <время> [причина]` - замутить (e.g. `/mute 10m`)
- `/unmute` - размутить
        """
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)

    elif data == 'menu_admins':
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data='main_menu')]
        ]
        text = """
👑 **Управление администраторами**

- `/addadmin` - сделать админом (в ответ на сообщение)
- `/removeadmin` - забрать права (в ответ на сообщение)
- `/listadmins` - показать список админов бота
        """
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)
    
    elif data == 'menu_info':
        keyboard = [
            [InlineKeyboardButton("⬅️ Назад", callback_data='main_menu')]
        ]
        text = """
ℹ️ **Информационные команды**

- `/id` - Узнать свой ID и ID чата
- `/menu` - Открыть это меню
        """
        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode=ParseMode.HTML)


def main():
    print("Бот запускается...")
    application = Application.builder().token(BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", show_menu))
    application.add_handler(CommandHandler("init", init_super_admin))
    application.add_handler(CommandHandler("id", get_id))
    
    # Команды модерации
    application.add_handler(CommandHandler("kick", kick_command))
    application.add_handler(CommandHandler("ban", ban_command))
    application.add_handler(CommandHandler("mute", mute_command))
    application.add_handler(CommandHandler("unmute", unmute_command))
    
    # Команды админов
    application.add_handler(CommandHandler("listadmins", list_admins))
    # ... добавьте сюда add_admin и remove_admin из предыдущих версий
    
    # Обработчик кнопок
    application.add_handler(CallbackQueryHandler(button_handler))

    application.run_polling()

if __name__ == "__main__":
    # Код для add_admin, remove_admin, init_super_admin нужно скопировать
    # из предыдущих ответов, т.к. он не изменился.
    # Я опустил его здесь для краткости.
    main()