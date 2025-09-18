from telegram.ext import Application, CommandHandler, MessageHandler, filters
import sqlite3
import asyncio
import pytz

# Замените 'YOUR_BOT_TOKEN' на токен, который вы получили от BotFather
BOT_TOKEN = '7617013549:AAEKxF6qIe3PiQswp_XG3R5wAI3Mx2VWaEc'
DATABASE_NAME = 'user.bd'

# Определите ваш часовой пояс. Для Сочи это 'Europe/Moscow'
TIMEZONE = 'Europe/Moscow'

def start(update, context):
    user = update.message.from_user
    chat_id = update.message.chat_id

    # Подключение к базе данных
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    # Проверка, есть ли пользователь уже в базе
    cursor.execute("SELECT user_id FROM users WHERE user_id=?", (user.id,))
    existing_user = cursor.fetchone()

    if not existing_user:
        # Добавление пользователя в базу данных
        cursor.execute("INSERT INTO users (user_id, username, first_name, last_name, chat_id) VALUES (?, ?, ?, ?, ?)",
                       (user.id, user.username, user.first_name, user.last_name, chat_id))
        conn.commit()
        update.message.reply_text(f"Привет, {user.first_name}! Вы успешно добавлены в базу данных.")
    else:
        update.message.reply_text(f"Привет, {user.first_name}! Вы уже есть в базе данных.")

    conn.close()

async def main():
    # Создаем объект Application и передаем ему токен и часовой пояс
    application = Application.builder().token(BOT_TOKEN).timezone(pytz.timezone(TIMEZONE)).build()

    # Добавляем обработчик команды /start
    application.add_handler(CommandHandler("start", start))

    # Запускаем бота
    await application.run_polling()

if __name__ == '__main__':
    # Подключение к базе данных и создание таблицы, если ее нет
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            chat_id INTEGER
        )
    """)
    conn.commit()
    conn.close()

    asyncio.run(main())
