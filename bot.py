import telebot
from telebot import types
import csv
import os
from datetime import datetime

TOKEN = "8320786387:AAFZYbucXnVD24JgBxiv9hDGCXM4j5kIXpY"

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "fleecing_test_results.csv"
user_data = {}

QUESTIONS = [
    ("sample", "Какой образец тестируете?", ["SAFEUP V1-HS0.7", "SAFEUP V1.1-HS0.7", "SAFEUP V2", "Другой образец"]),
    ("name", "Введите ваше имя:", None),
    ("gender", "Пол:", ["Женщина", "Мужчина"]),
    ("age", "Возраст:", None),
    ("hair_type", "Тип волос?", ["Тонкие", "Нормальные", "Густые"]),
    ("hair_condition", "Состояние волос?", ["Натуральные", "Окрашенные", "Осветленные", "Поврежденные", "Сухие", "Пористые"]),
    ("hair_length", "Длина волос?", ["Короткие", "Средние", "Длинные"]),
    ("application", "Как использовали средство?", ["Влажные волосы + фен", "Сухие волосы + фен", "Утюжок", "Плойка"]),

    ("spray", "Как вам распыление?", ["😍 Отлично", "🙂 Хорошо", "😐 Нормально", "🙁 Не очень", "😞 Плохо"]),
    ("comb", "Легкость расчесывания?", ["😍 Отлично", "🙂 Хорошо", "😐 Нормально", "🙁 Не очень", "😞 Плохо"]),
    ("smooth", "Гладкость волос?", ["😍 Отлично", "🙂 Хорошо", "😐 Нормально", "🙁 Не очень", "😞 Плохо"]),
    ("heat_protection", "Как вы оцените эффект термозащиты?", ["🔥 Очень заметен", "👍 Скорее заметен", "🤔 Не уверен(а)", "👎 Скорее не заметен", "❌ Не заметен"]),
    ("shine", "Блеск волос?", ["😍 Отлично", "🙂 Хорошо", "😐 Нормально", "🙁 Не очень", "😞 Плохо"]),
    ("frizz", "Снижение пушения?", ["😍 Отлично", "🙂 Хорошо", "😐 Нормально", "🙁 Не очень", "😞 Плохо"]),

    ("weight", "Есть ли утяжеление?", ["Нет", "Слабое", "Среднее", "Сильное"]),
    ("greasy", "Есть ли жирность/грязный эффект?", ["Нет", "Слабая", "Средняя", "Сильная"]),
    ("stickiness", "Есть ли липкость?", ["Нет", "Слабая", "Средняя", "Сильная"]),

    ("smell", "Как вам аромат продукта?", ["😍 Очень приятный", "🙂 Приятный", "😐 Нейтральный", "🙁 Не очень понравился", "😞 Неприятный"]),

    ("buy", "Купили бы такой продукт?", ["Да", "Нет", "Не уверен(а)"]),
    ("comment", "Что понравилось и что можно улучшить?", None),
]

def make_keyboard(options):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for option in options:
        markup.add(option)
    return markup

def ask_question(chat_id):
    data = user_data[chat_id]
    step = data["step"]

    if step >= len(QUESTIONS):
        save_result(chat_id)
        bot.send_message(chat_id, "Спасибо! Ваш отзыв сохранён ✅", reply_markup=types.ReplyKeyboardRemove())
        user_data.pop(chat_id, None)
        return

    key, text, options = QUESTIONS[step]
    if options:
        bot.send_message(chat_id, text, reply_markup=make_keyboard(options))
    else:
        bot.send_message(chat_id, text, reply_markup=types.ReplyKeyboardRemove())

def save_result(chat_id):
    data = user_data[chat_id]["answers"]
    file_exists = os.path.exists(DATA_FILE)

    fields = ["date", "telegram_id"] + [q[0] for q in QUESTIONS]

    row = {"date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "telegram_id": chat_id}
    row.update(data)

    with open(DATA_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)

@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_data[chat_id] = {"step": 0, "answers": {}}
    bot.send_message(chat_id, "🧪 Fleecing Test Lab\n\nНачинаем тестирование образца.")
    ask_question(chat_id)

@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        bot.send_message(chat_id, "Нажмите /start, чтобы начать тестирование.")
        return

    data = user_data[chat_id]
    step = data["step"]
    key = QUESTIONS[step][0]

    data["answers"][key] = message.text
    data["step"] += 1

    ask_question(chat_id)

print("Fleecing Test Lab Bot запущен")
while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Ошибка подключения, перезапуск через 10 секунд:", e)
        import time
        time.sleep(10)
