import sqlite3
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext, CallbackQueryHandler
from telegram import InlineKeyboardMarkup, InlineKeyboardButton

# Подключение к базе данных SQLite
conn = sqlite3.connect('balances.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER)''')
conn.commit()

# Функция для проверки существования пользователя в базе данных
def user_exists(user_id):
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    return cursor.fetchone() is not None

# Функция для получения баланса пользователя
def get_balance(user_id):
    cursor.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
    result = cursor.fetchone()
    return result[0] if result else 0

# Функция для изменения баланса пользователя
def update_balance(user_id, amount):
    current_balance = get_balance(user_id)
    new_balance = current_balance + amount
    cursor.execute("INSERT OR REPLACE INTO users (user_id, balance) VALUES (?, ?)", (user_id, new_balance))
    conn.commit()

# Функция-обработчик команды /start
def start(update: Update, context: CallbackContext) -> None:
    user_id = update.message.from_user.id
    if not user_exists(user_id):
        cursor.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))
        conn.commit()

    user_balance = get_balance(user_id)
    keyboard = [
        [InlineKeyboardButton("Товары", callback_data='products')],
        [InlineKeyboardButton("Купить", callback_data='buy')],
        [InlineKeyboardButton("Баланс", callback_data='balance')],
        [InlineKeyboardButton("Пополнить баланс", url='ссылка_на_оплату')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text(f"Привет! Твой текущий баланс: {user_balance}. Выбери действие:", reply_markup=reply_markup)

# Функция-обработчик нажатий на кнопки
def button_click(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()
    user_id = query.from_user.id

    if query.data == 'buy':
        # Здесь можно добавить логику совершения покупки
        purchase_amount = 10
        update_balance(user_id, -purchase_amount)
        query.edit_message_text(text=f"Товар куплен! Баланс обновлен.")
    elif query.data == 'balance':
        user_balance = get_balance(user_id)
        query.edit_message_text(text=f"Твой текущий баланс: {user_balance}")
    else:
        query.edit_message_text(text=f"Выбрано действие: {query.data}")

def main() -> None:
    updater = Updater("YOUR_TOKEN", use_context=True)
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CallbackQueryHandler(button_click))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
