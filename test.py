import logging
import json
from datetime import datetime, timedelta
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton
from aiogram.contrib.middlewares.logging import LoggingMiddleware

TOKEN = '6562742616:AAEahEb3TdScf5jSqtsFxQVdsMU8SufZrbc'

# Initialize bot and dispatcher
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

DATA_FILE = "savings_data.json"

try:
    with open(DATA_FILE, 'r') as f:
        user_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    user_data = {}

def save_data_to_file():
    with open(DATA_FILE, 'w') as f:
        json.dump(user_data, f)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
keyboard.add(
    KeyboardButton("Показать сбережения"),
    KeyboardButton("Неделя"),
    KeyboardButton("Месяц"),
    KeyboardButton("Обнулить")
)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer('Пожалуйста, отправьте сумму, которую вы хотите добавить.', reply_markup=keyboard)

def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False

@dp.message_handler(lambda message: message.text in ['Показать сбережения', 'Неделя', 'Месяц', 'Обнулить'])
async def handle_buttons(message: types.Message):
    user_id = str(message.from_user.id)
    today = datetime.now()
    action = message.text

    if action == 'Неделя':
        end_date = today
        start_date = today - timedelta(days=7)
        title = "<i>За неделю</i>"
    elif action == 'Месяц':
        end_date = today
        start_date = today - timedelta(days=30)
        title = "<i>За месяц</i>"
    elif action == 'Обнулить':
        user_data[user_id] = []
        save_data_to_file()
        await message.answer("Ваши сбережения были обнулены.", reply_markup=keyboard)
        return
    else:
        start_date = None

        end_date = None
        title = "<i>Ваши сбережения:</>"

    if user_id not in user_data or not user_data[user_id]:
        await message.answer("У вас пока нет сбережений.", reply_markup=keyboard)
        return

    savings_list = [f"{idx+1}. {item['amount']}{' ' * (15 - len(str(item['amount'])))}<i>{item['date']}</i>" 
                    for idx, item in enumerate(user_data[user_id]) 
                    if not start_date or (datetime.strptime(item['date'], "%d-%m-%Y") >= start_date and datetime.strptime(item['date'], "%d-%m-%Y") <= end_date)]
    total_sum = sum(item["amount"] for item in user_data[user_id] if not start_date or (datetime.strptime(item['date'], "%d-%m-%Y") >= start_date and datetime.strptime(item['date'], "%d-%m-%Y") <= end_date))
    infotext = "\n<b>Сумма        Дата</b>\n"
    text = title + infotext + "\n".join(savings_list) + f"\n\nИтого: <b>{total_sum}</b><i>cомон</i>"
    await message.answer(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

@dp.message_handler(lambda message: not is_integer(message.text))
async def non_integer_message(message: types.Message):
    await message.answer("Введите только целые числа.", reply_markup=keyboard)

@dp.message_handler(lambda message: is_integer(message.text))
async def sum_numbers(message: types.Message):

    user_id = str(message.from_user.id)
    number = int(message.text)
    current_date = datetime.now().strftime("%d-%m-%Y")

    if user_id not in user_data:
        user_data[user_id] = []

    user_data[user_id].append({"amount": number, "date": current_date})
    save_data_to_file()

    total = sum(item["amount"] for item in user_data[user_id])
    await message.answer(f"Текущая сумма: {total}c", reply_markup=keyboard)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

