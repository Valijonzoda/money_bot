import logging
import json
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, ReplyKeyboardMarkup, KeyboardButton

TOKEN = '6562742616:AAEahEb3TdScf5jSqtsFxQVdsMU8SufZrbc'

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

DATA_FILE = "savings_data.json"

# Загрузка данных из файла
try:
    with open(DATA_FILE, 'r') as f:
        user_data = json.load(f)
except (FileNotFoundError, json.JSONDecodeError):
    user_data = {}

def save_data_to_file():
    """Сохраняет данные в файл."""
    with open(DATA_FILE, 'w') as f:
        json.dump(user_data, f)

keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
keyboard.row(
    KeyboardButton("3"),
    KeyboardButton("5"),
    KeyboardButton("10"),
    KeyboardButton("20")
)
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
    """Проверяет, является ли значение целым числом."""
    try:
        int(value)
        return True
    except ValueError:
        return False

@dp.message_handler(lambda message: message.text in ['3', '5', '10', '20'])
async def handle_preset_values(message: types.Message):
    user_id = str(message.from_user.id)
    number = int(message.text)
    current_date = datetime.now().strftime("%d-%m-%Y")

    if user_id not in user_data:
        user_data[user_id] = []

    user_data[user_id].append({"amount": number, "date": current_date})
    save_data_to_file()

    total = sum(item["amount"] for item in user_data[user_id])
    await message.answer(f"Успешно добавлена! Текущая сумма: {total}c", reply_markup=keyboard)

@dp.message_handler(lambda message: is_integer(message.text))
async def handle_custom_value(message: types.Message):
    user_id = str(message.from_user.id)
    number = int(message.text)
    current_date = datetime.now().strftime("%d-%m-%Y")

    if user_id not in user_data:
        user_data[user_id] = []

    user_data[user_id].append({"amount": number, "date": current_date})
    save_data_to_file()

    total = sum(item["amount"] for item in user_data[user_id])
    await message.answer(f"Текущая сумма: {total}c", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in ['Показать сбережения', 'Неделя', 'Месяц', 'Обнулить'])
async def handle_buttons(message: types.Message):
    # ... [Оставить этот код без изменений]

@dp.message_handler(lambda message: not is_integer(message.text))
async def non_integer_message(message: types.Message):
    await message.answer("Введите только целые числа.", reply_markup=keyboard)

if __name__ == "__main__":
    from aiogram import executor
    executor.start_polling(dp, skip_updates=True)

