import telebot
from telebot import types
import logging
import time
from datetime import datetime
import os

# --- Настройка логирования ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# --- Константы ---
ADMIN_ID = "1172834372"  # ID вашего администратора
BOT_TOKEN = "7970523336:AAFDbO8hOSjo5QVMYHILPlU-K5YJDzc3ihk"
BANNED_USERS_FILE = "banned_users.txt" # File to store banned user IDs

# --- Инициализация бота ---
bot = telebot.TeleBot(BOT_TOKEN)

# --- Словари для хранения информации в оперативной памяти ---
# Dictionary to store user conversations for replies (admin_message_id: user_id)
user_conversations = {}
# Set to store banned user IDs in memory
banned_users = set()
# Dictionary to store username-to-ID mapping (username: user_id)
# This is volatile and will reset on bot restart
username_to_id = {}


# --- Вспомогательные функции ---
def read_banned_users():
    """Reads banned user IDs from the file into the banned_users set."""
    if not os.path.exists(BANNED_USERS_FILE):
        with open(BANNED_USERS_FILE, 'w') as f:
            pass # Create the file if it doesn't exist
    with open(BANNED_USERS_FILE, 'r') as f:
        for line in f:
            try:
                banned_users.add(int(line.strip()))
            except ValueError:
                logger.warning(f"Некорректный ID пользователя в файле бан-листа: {line.strip()}")
    logger.info(f"Загружено забаненных пользователей: {banned_users}")

def write_banned_users():
    """Writes banned user IDs from the banned_users set to the file."""
    with open(BANNED_USERS_FILE, 'w') as f:
        for user_id in banned_users:
            f.write(f"{user_id}\n")
    logger.info(f"Сохранен список забаненных пользователей: {banned_users}")

def is_user_banned(user_id):
    """Checks if a user is banned."""
    return user_id in banned_users

def get_user_info(user):
    """
    Helper function to get user info string with a clickable user ID.
    If the user has a username, it will prioritize that.
    """
    user_id_str = str(user.id)
    # Create a clickable link for the user ID
    clickable_user_id = f"<a href='tg://user?id={user_id_str}'>{user_id_str}</a>"

    if user.username:
        return f"@{user.username} ({clickable_user_id})"
    else:
        name = user.first_name if user.first_name else ""
        if user.last_name:
            name += f" {user.last_name}"
        if not name: # Fallback if no first_name or last_name
            name = "Скрытый пользователь"
        return f"{name} ({clickable_user_id})"

def create_reply_keyboard(user_id):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Ответить", callback_data=f"reply_{user_id}"))
    return markup

def send_to_admin(content, caption, user_id, content_type='text'):
    """Helper function to send content to admin"""
    sent_msg = None
    try:
        reply_markup = create_reply_keyboard(user_id)
        # Use parse_mode='HTML' to make the clickable user ID work
        if content_type == 'text':
            sent_msg = bot.send_message(ADMIN_ID, f"{caption}", reply_markup=reply_markup, parse_mode='HTML')
        elif content_type == 'photo':
            sent_msg = bot.send_photo(ADMIN_ID, content, caption=f"{caption}", reply_markup=reply_markup, parse_mode='HTML')
        elif content_type == 'voice':
            sent_msg = bot.send_voice(ADMIN_ID, content, caption=f"{caption}", reply_markup=reply_markup, parse_mode='HTML')
        elif content_type == 'video':
            sent_msg = bot.send_video(ADMIN_ID, content, caption=f"{caption}", reply_markup=reply_markup, parse_mode='HTML')
        elif content_type == 'video_note':
            # Video notes don't have a direct caption, the caption should precede it
            bot.send_message(ADMIN_ID, f"{caption}", parse_mode='HTML') # Send caption as a separate message first
            sent_msg = bot.send_video_note(ADMIN_ID, content, reply_markup=reply_markup)
        elif content_type == 'sticker':
            # Stickers also don't have a direct caption, the caption should precede it
            bot.send_message(ADMIN_ID, f"{caption}", parse_mode='HTML') # Send caption as a separate message first
            sent_msg = bot.send_sticker(ADMIN_ID, content, reply_markup=reply_markup)
        elif content_type == 'document':
            sent_msg = bot.send_document(ADMIN_ID, content, caption=f"{caption}", reply_markup=reply_markup, parse_mode='HTML')
        elif content_type == 'gif': # animation type
            sent_msg = bot.send_animation(ADMIN_ID, content, caption=f"{caption}", reply_markup=reply_markup, parse_mode='HTML')

        if sent_msg:
            # Сохраняем в оперативную память
            user_conversations[sent_msg.message_id] = user_id
            logger.info(f"Сохранена беседа в RAM: admin_msg_id={sent_msg.message_id}, user_id={user_id}")
        return True
    except telebot.apihelper.ApiTelegramException as e:
        logger.error(f"Telegram API Error при пересылке {content_type} админу ({ADMIN_ID}): {e}")
        bot.send_message(ADMIN_ID, f"⚠️ Ошибка Telegram API при пересылке {content_type} от пользователя {user_id}: {e.description}", parse_mode='HTML')
        return False
    except Exception as e:
        logger.error(f"Общая ошибка при пересылке {content_type} админу: {e}")
        bot.send_message(ADMIN_ID, f"⚠️ Общая ошибка при пересылке {content_type} от пользователя {user_id}: {e}", parse_mode='HTML')
        return False

# --- Хендлеры сообщений ---

@bot.message_handler(commands=["start"])
def start(message):
    # Update username_to_id mapping
    if message.from_user.username:
        username_to_id[message.from_user.username.lower()] = message.from_user.id

    if is_user_banned(message.from_user.id):
        logger.info(f"Забаненный пользователь {get_user_info(message.from_user)} попытался использовать /start.")
        return
    bot.send_message(message.chat.id, "💬 Введите анонимное сообщение, 🖼 отправьте картинку, 📽 видео, 🗣 голосовое сообщение, видеосообщения, стикеры или GIF. ")

@bot.message_handler(commands=["ban"])
def ban_user(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    args = message.text.split(" ", 1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Использование: /ban &lt;username или ID пользователя&gt;") # Use HTML entities for < and >
        return

    target_identifier = args[1].strip()
    target_id = None

    try:
        # Try to ban by ID first
        target_id = int(target_identifier)
    except ValueError:
        # If not an ID, try to find by username
        # Normalize username for lookup (remove '@' if present, convert to lowercase)
        normalized_username = target_identifier.lstrip('@').lower()
        target_id = username_to_id.get(normalized_username)

    if target_id:
        if target_id == int(ADMIN_ID):
            bot.send_message(message.chat.id, "Вы не можете забанить самого себя.")
            return

        if target_id in banned_users:
            bot.send_message(message.chat.id, f"Пользователь с ID <a href='tg://user?id={target_id}'>{target_id}</a> уже забанен.", parse_mode='HTML')
            return

        banned_users.add(target_id)
        write_banned_users()
        bot.send_message(message.chat.id, f"Пользователь @{normalized_username if normalized_username else ''} <a href='tg://user?id={target_id}'>{target_id}</a> забанен.", parse_mode='HTML')
        logger.info(f"Админ {get_user_info(message.from_user)} забанил пользователя с ID {target_id}.")
    else:
        bot.send_message(message.chat.id, "Не удалось найти пользователя по указанному ID или имени пользователя. Убедитесь, что пользователь недавно взаимодействовал с ботом, если вы пытаетесь забанить по имени пользователя.")
        logger.warning(f"Админ {get_user_info(message.from_user)} попытался забанить по некорректному ID или неизвестному username: {target_identifier}")


@bot.message_handler(commands=["unban"])
def unban_user(message):
    if str(message.from_user.id) != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    args = message.text.split(" ", 1)
    if len(args) < 2:
        bot.send_message(message.chat.id, "Использование: /unban &lt;username или ID пользователя&gt;")
        return

    target_identifier = args[1].strip()
    target_id = None

    try:
        # Try to unban by ID first
        target_id = int(target_identifier)
    except ValueError:
        # If not an ID, try to find by username
        normalized_username = target_identifier.lstrip('@').lower()
        target_id = username_to_id.get(normalized_username)

    if target_id:
        if target_id in banned_users:
            banned_users.remove(target_id)
            write_banned_users()
            bot.send_message(message.chat.id, f"Пользователь @{normalized_username if normalized_username else ''} <a href='tg://user?id={target_id}'>{target_id}</a> разбанен.", parse_mode='HTML')
            logger.info(f"Админ {get_user_info(message.from_user)} разбанил пользователя с ID {target_id}.")
        else:
            bot.send_message(message.chat.id, f"Пользователь с ID <a href='tg://user?id={target_id}'>{target_id}</a> не найден в списке забаненных.", parse_mode='HTML')
    else:
        bot.send_message(message.chat.id, "Не удалось найти пользователя по указанному ID или имени пользователя. Убедитесь, что пользователь недавно взаимодействовал с ботом, если вы пытаетесь разбанить по имени пользователя.")
        logger.warning(f"Админ {get_user_info(message.from_user)} попытался разбанить по некорректному ID или неизвестному username: {target_identifier}")


@bot.message_handler(content_types=["text"])
def handle_text(message):
    # Update username_to_id mapping
    if message.from_user.username:
        username_to_id[message.from_user.username.lower()] = message.from_user.id

    if is_user_banned(message.from_user.id):
        logger.info(f"Забаненный пользователь {get_user_info(message.from_user)} попытался отправить текст.")
        return

    if str(message.from_user.id) == ADMIN_ID and message.reply_to_message:
        # Это ответ администратора на сообщение пользователя
        process_admin_reply(message)
        return

    # Это сообщение от пользователя к админу
    user_info = get_user_info(message.from_user)
    caption = f"{user_info}\n{message.text}"
    if send_to_admin(message.text, caption, message.from_user.id):
        bot.send_message(message.chat.id, "✅ Сообщение отправлено!")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось отправить ваше сообщение администратору. Пожалуйста, попробуйте позже.")

@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    # Update username_to_id mapping
    if message.from_user.username:
        username_to_id[message.from_user.username.lower()] = message.from_user.id

    if is_user_banned(message.from_user.id):
        logger.info(f"Забаненный пользователь {get_user_info(message.from_user)} попытался отправить фото.")
        return

    if str(message.from_user.id) == ADMIN_ID and message.reply_to_message:
        process_admin_reply(message)
        return

    user_info = get_user_info(message.from_user)
    caption = f"{user_info}\n"
    if message.caption:
        caption += f"Подпись: {message.caption}"

    if send_to_admin(message.photo[-1].file_id, caption, message.from_user.id, 'photo'):
        bot.send_message(message.chat.id, "✅ Фото отправлено!")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось отправить ваше фото администратору. Пожалуйста, попробуйте позже.")

@bot.message_handler(content_types=["video"])
def handle_video(message):
    # Update username_to_id mapping
    if message.from_user.username:
        username_to_id[message.from_user.username.lower()] = message.from_user.id

    if is_user_banned(message.from_user.id):
        logger.info(f"Забаненный пользователь {get_user_info(message.from_user)} попытался отправить видео.")
        return

    if str(message.from_user.id) == ADMIN_ID and message.reply_to_message:
        process_admin_reply(message)
        return

    user_info = get_user_info(message.from_user)
    caption = f"{user_info}\n"
    if message.caption:
        caption += f"Подпись: {message.caption}"

    if send_to_admin(message.video.file_id, caption, message.from_user.id, 'video'):
        bot.send_message(message.chat.id, "✅ Видео отправлено!")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось отправить ваше видео администратору. Пожалуйста, попробуйте позже.")

@bot.message_handler(content_types=["sticker"])
def handle_sticker(message):
    # Update username_to_id mapping
    if message.from_user.username:
        username_to_id[message.from_user.username.lower()] = message.from_user.id

    if is_user_banned(message.from_user.id):
        logger.info(f"Забаненный пользователь {get_user_info(message.from_user)} попытался отправить стикер.")
        return

    if str(message.from_user.id) == ADMIN_ID and message.reply_to_message:
        process_admin_reply(message)
        return

    user_info = get_user_info(message.from_user)
    caption = f"{user_info}" # Стикеры обычно без подписи
    if send_to_admin(message.sticker.file_id, caption, message.from_user.id, 'sticker'):
        bot.send_message(message.chat.id, "✅ Стикер отправлен!")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось отправить ваш стикер администратору. Пожалуйста, попробуйте позже.")

@bot.message_handler(content_types=["animation"])
def handle_gif(message):
    # Update username_to_id mapping
    if message.from_user.username:
        username_to_id[message.from_user.username.lower()] = message.from_user.id

    if is_user_banned(message.from_user.id):
        logger.info(f"Забаненный пользователь {get_user_info(message.from_user)} попытался отправить GIF.")
        return

    if str(message.from_user.id) == ADMIN_ID and message.reply_to_message:
        process_admin_reply(message)
        return

    user_info = get_user_info(message.from_user)
    caption = f"{user_info}\n"
    if message.caption:
        caption += f"Подпись: {message.caption}"

    if send_to_admin(message.animation.file_id, caption, message.from_user.id, 'gif'):
        bot.send_message(message.chat.id, "✅ GIF отправлен!")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось отправить ваш GIF администратору. Пожалуйста, попробуйте позже.")

@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    # Update username_to_id mapping
    if message.from_user.username:
        username_to_id[message.from_user.username.lower()] = message.from_user.id

    if is_user_banned(message.from_user.id):
        logger.info(f"Забаненный пользователь {get_user_info(message.from_user)} попытался отправить голосовое сообщение.")
        return

    if str(message.from_user.id) == ADMIN_ID and message.reply_to_message:
        process_admin_reply(message)
        return

    user_info = get_user_info(message.from_user)
    caption = f"От {user_info}" # Голосовые обычно без подписи
    if send_to_admin(message.voice.file_id, caption, message.from_user.id, 'voice'):
        bot.send_message(message.chat.id, "✅ Голосовое сообщение отправлено!")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось отправить ваше голосовое сообщение администратору. Пожалуйста, попробуйте позже.")

@bot.message_handler(content_types=["video_note"])
def handle_video_note(message):
    # Update username_to_id mapping
    if message.from_user.username:
        username_to_id[message.from_user.username.lower()] = message.from_user.id

    if is_user_banned(message.from_user.id):
        logger.info(f"Забаненный пользователь {get_user_info(message.from_user)} попытался отправить видеосообщение.")
        return

    if str(message.from_user.id) == ADMIN_ID and message.reply_to_message:
        process_admin_reply(message)
        return

    user_info = get_user_info(message.from_user)
    caption = f"{user_info}" # Видеосообщения обычно без подписи
    if send_to_admin(message.video_note.file_id, caption, message.from_user.id, 'video_note'):
        bot.send_message(message.chat.id, "✅ Видеосообщение отправлено!")
    else:
        bot.send_message(message.chat.id, "❌ Не удалось отправить ваше видеосообщение администратору. Пожалуйста, попробуйте позже.")

# Хендлер для неподдерживаемых типов контента от пользователя
@bot.message_handler(func=lambda message: True, content_types=telebot.util.content_type_media)
def handle_unsupported_content(message):
    # Update username_to_id mapping
    if message.from_user.username:
        username_to_id[message.from_user.username.lower()] = message.from_user.id

    if is_user_banned(message.from_user.id):
        logger.info(f"Забаненный пользователь {get_user_info(message.from_user)} попытался отправить неподдерживаемый контент.")
        return

    if str(message.from_user.id) == ADMIN_ID: # Админ может отправлять что угодно
        return

    logger.info(f"Получено неподдерживаемое сообщение от {get_user_info(message.from_user)}: {message.content_type}")
    bot.send_message(message.chat.id, "Извините, я пока не поддерживаю этот тип сообщений. Пожалуйста, отправьте текст, фото, видео, голосовое сообщение, видеосообщение, стикер или GIF.")


# --- Обработка ответов администратора ---

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def handle_reply_callback(call):
    try:
        user_id = call.data.split("_")[1]
        msg = bot.send_message(call.message.chat.id, f"✏️ Введите ответ:")
        # REMOVE OR COMMENT OUT THIS LINE to keep the button
        # bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id, reply_markup=None)
        bot.register_next_step_handler(msg, process_reply_step, int(user_id)) # Ensure user_id is an int
    except Exception as e:
        logger.error(f"Ошибка обработки callback (reply_): {e}")
        bot.send_message(call.message.chat.id, f"❌ Ошибка при подготовке ответа: {e}")

def process_admin_reply(message):
    # Эта функция вызывается, когда админ отвечает на сообщение, пересланное ботом
    try:
        # Получаем user_id из словаря в оперативной памяти
        original_user_id = user_conversations.get(message.reply_to_message.message_id)
        if original_user_id:
            # Вызываем основную логику отправки ответа, передавая ID исходного пользователя
            process_reply_step(message, original_user_id)
        else:
            logger.warning(f"Админ {ADMIN_ID} попытался ответить на сообщение {message.reply_to_message.message_id}, но user_id не найден в RAM (возможно, бот был перезапущен).")
            bot.send_message(ADMIN_ID, "❌ Не удалось найти пользователя для ответа. Возможно, это сообщение было отправлено до последнего запуска бота.")
    except Exception as e:
        logger.error(f"Ошибка в process_admin_reply: {e}")
        bot.send_message(ADMIN_ID, f"❌ Произошла ошибка при обработке вашего ответа: {e}")


def process_reply_step(message, user_id):
    """
    Отправляет ответ администратора пользователю.
    user_id здесь - это ID пользователя, которому нужно отправить ответ.
    """
    try:
        send_methods = {
            'text': bot.send_message,
            'photo': bot.send_photo,
            'video': bot.send_video,
            'sticker': bot.send_sticker,
            'animation': bot.send_animation, # GIF
            'voice': bot.send_voice,
            'video_note': bot.send_video_note,
            'document': bot.send_document # Добавляем для админа возможность отправлять документы
        }

        send_method = send_methods.get(message.content_type)
        if send_method:
            if message.content_type == 'text':
                send_method(user_id, f"🔵 Ответ администратора:\n{message.text}")
            elif message.content_type in ['photo', 'video', 'document', 'animation', 'voice']: # Эти типы могут иметь подпись
                caption_text = message.caption if message.caption else ""
                send_method(user_id, getattr(message, message.content_type).file_id, caption=f"🔵 Ответ администратора:\n{caption_text}")
            elif message.content_type in ['sticker', 'video_note']: # Эти типы обычно без подписи
                send_method(user_id, getattr(message, message.content_type).file_id)
            else:
                # На случай, если появился новый тип, который не был учтен выше
                send_method(user_id, getattr(message, message.content_type).file_id)

            bot.send_message(message.chat.id, f"✅ Ответ отправлен!") # Changed this line
            logger.info(f"Админ {message.from_user.id} отправил {message.content_type} ответ пользователю {user_id}")
        else:
            bot.send_message(message.chat.id, "❌ Можно ответить только текстом, фото, видео, стикером, GIF, голосовым или видеосообщением, или документом.")
            logger.warning(f"Админ {message.from_user.id} попытался отправить неподдерживаемый ответ ({message.content_type}) пользователю {user_id}")

    except telebot.apihelper.ApiTelegramException as e:
        if e.error_code == 403:
            logger.warning(f"Не удалось отправить ответ пользователю {user_id}: Пользователь заблокировал бота. Ошибка: {e}")
            bot.send_message(message.chat.id, f"❌ Пользователь <a href='tg://user?id={user_id}'>{user_id}</a> заблокировал бота, ответ не может быть отправлен.", parse_mode='HTML')
        elif e.error_code == 429:
            retry_after = e.result_json.get('parameters', {}).get('retry_after', 5) # По умолчанию 5 секунд
            logger.warning(f"Слишком много запросов. Повтор через {retry_after} секунд. Ошибка: {e}")
            bot.send_message(message.chat.id, f"⚠️ Слишком много запросов Telegram API. Повторите попытку через {retry_after} секунд.")
        else:
            logger.error(f"Telegram API Error при отправке ответа пользователю {user_id}: Код {e.error_code} - {e.description}")
            bot.send_message(message.chat.id, f"❌ Ошибка Telegram API при отправке ответа: {e.description}")
    except Exception as e:
        logger.error(f"Общая ошибка при отправке ответа пользователю {user_id}: {e}")
        bot.send_message(message.chat.id, f"❌ Общая ошибка при отправке ответа: {e}")

# --- Запуск бота ---
if __name__ == '__main__':
    read_banned_users() # Load banned users on startup
    logger.info("Бот запущен. Ожидание сообщений...")
    bot.polling(none_stop=True)
