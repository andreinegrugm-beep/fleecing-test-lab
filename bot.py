import telebot
from telebot import types
import csv
import os
from datetime import datetime

TOKEN = "PASTE_YOUR_TOKEN_HERE"

bot = telebot.TeleBot(TOKEN)

DATA_FILE = "fleecing_test_results.csv"
user_data = {}

INTRO_TEXT = """🧪 Fleecing Test Lab

Для получения корректного результата:

• Вымойте волосы шампунем.
• По возможности не используйте маски, бальзамы и кондиционеры перед тестированием.
• Нанесите тестовый образец на влажные волосы.
• Распределите средство расчёской.
• Выполните сушку феном или укладку горячим инструментом.
• Если обычно используете средство для объёма волос, например Fleecing Up&Up, нанесите его после завершения сушки.
• После этого заполните анкету.
"""

QUESTIONS = [
    {
        "key": "sample",
        "text": "Какой образец вы тестируете?",
        "options": [
            "Тестовый образец №1 — V1.1-HS0.7",
            "Тестовый образец №2 — V1.1-HS0.7",
            "Тестовый образец №3 — V1.2-DS02",
            "Тестовый образец №4 — V1.2-CP05",
        ],
    },
    {
        "key": "hair_condition",
        "text": "Состояние волос:",
        "options": ["Натуральные", "Окрашенные", "Осветлённые"],
    },
    {
        "key": "hair_structure",
        "text": "Структура волос:",
        "options": ["Нормальные", "Сухие", "Повреждённые", "Пористые"],
    },
    {
        "key": "before_fen_feel",
        "text": "После нанесения средства, ДО использования фена волосы стали:",
        "options": [
            "Ничего не изменилось",
            "Немного более гладкими",
            "Легче расчёсываться",
            "Более скользкими",
            "Тяжелее",
            "Липкими",
        ],
    },
    {
        "key": "distribution",
        "text": "Насколько легко средство распределилось по волосам?",
        "options": ["😡 Очень плохо", "😕 Скорее плохо", "😐 Нормально", "🙂 Хорошо", "🤩 Отлично"],
    },
    {
        "key": "comb_before_drying",
        "text": "Насколько легко волосы расчёсывались ДО сушки?",
        "options": ["😡 Очень трудно", "😕 Скорее трудно", "😐 Обычно", "🙂 Легко", "🤩 Очень легко"],
    },
    {
        "key": "during_drying",
        "text": "Во время укладки феном волосы стали:",
        "options": [
            "Более гладкими",
            "Более послушными",
            "Более объёмными",
            "Без изменений",
            "Более жёсткими",
        ],
    },
    {
        "key": "comb_after_drying",
        "text": "Насколько легко волосы расчёсывались ПОСЛЕ сушки?",
        "options": ["😡 Очень трудно", "😕 Скорее трудно", "😐 Обычно", "🙂 Легко", "🤩 Очень легко"],
    },
    {
        "key": "main_effect_after_drying",
        "text": "Какой эффект после сушки заметен больше всего?",
        "options": [
            "Волосы стали более гладкими",
            "Волосы стали более блестящими",
            "Стало меньше пушения",
            "Волосы выглядят более здоровыми",
            "Не заметил(а) изменений",
        ],
    },
    {
        "key": "weight_dirty_effect",
        "text": "Было ли ощущение утяжеления или эффекта грязных волос?",
        "options": ["Нет", "Совсем немного", "Заметно", "Сильно"],
    },
    {
        "key": "fragrance",
        "text": "Как ощущался аромат?",
        "options": [
            "Не почувствовал(а)",
            "Только при нанесении",
            "Во время сушки",
            "Остался после укладки",
            "Слишком сильный аромат",
        ],
    },
{
    "key": "fragrance_rating",
    "text": "Насколько вам понравился аромат средства?",
    "options": [
        "😡 Совсем не понравился",
        "😕 Скорее не понравился",
        "😐 Нейтрально",
        "🙂 Понравился",
        "🤩 Очень понравился",
    ],
},
{
        "key": "used_volume_product",
        "text": "Использовали ли вы после термозащиты средство для объёма волос?",
        "options": ["Да", "Нет"],
    },
    {
        "key": "used_upup",
        "text": "Использовали ли вы после термозащиты спрей-пудру для объёма волос Fleecing Up&Up?",
        "options": ["Да", "Нет", "Использовал(а) другое средство для объёма"],
        "condition": lambda answers: answers.get("used_volume_product") == "Да",
    },
    {
        "key": "upup_volume_result",
        "text": "Как повёл себя объём волос после использования Fleecing Up&Up?",
        "options": [
            "🤩 Объём стал лучше обычного",
            "🙂 Такой же как обычно",
            "😕 Объём стал хуже обычного",
            "😐 Сложно оценить",
        ],
        "condition": lambda answers: answers.get("used_upup") == "Да",
    },
    {
        "key": "other_volume_result",
        "text": "Как повёл себя объём волос после использования средства для объёма?",
        "options": [
            "🤩 Объём стал лучше обычного",
            "🙂 Такой же как обычно",
            "😕 Объём стал хуже обычного",
            "😐 Сложно оценить",
        ],
        "condition": lambda answers: answers.get("used_upup") == "Использовал(а) другое средство для объёма",
    },
    {
        "key": "overall_result",
        "text": "Насколько вам понравился результат?",
        "options": ["😡 Не понравился", "😕 Скорее не понравился", "😐 Нормально", "🙂 Понравился", "🤩 Очень понравился"],
    },
    {
        "key": "would_buy",
        "text": "Купили бы вы такой продукт после тестирования?",
        "options": ["Да", "Скорее да", "Скорее нет", "Нет"],
    },
    {
        "key": "comment",
        "text": "Ваш комментарий или замечания:",
        "options": None,
    },
]


def make_keyboard(options):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    for option in options:
        markup.add(option)
    return markup


def get_next_question_index(chat_id):
    data = user_data[chat_id]
    answers = data["answers"]

    while data["step"] < len(QUESTIONS):
        question = QUESTIONS[data["step"]]
        condition = question.get("condition")

        if condition is None or condition(answers):
            return data["step"]

        data["step"] += 1

    return None


def ask_question(chat_id):
    next_index = get_next_question_index(chat_id)

    if next_index is None:
        save_result(chat_id)
        bot.send_message(
            chat_id,
            "Спасибо! Ваш отзыв сохранён ✅",
            reply_markup=types.ReplyKeyboardRemove(),
        )
        user_data.pop(chat_id, None)
        return

    question = QUESTIONS[next_index]

    if question["options"]:
        bot.send_message(
            chat_id,
            question["text"],
            reply_markup=make_keyboard(question["options"]),
        )
    else:
        bot.send_message(
            chat_id,
            question["text"],
            reply_markup=types.ReplyKeyboardRemove(),
        )


def save_result(chat_id):
    data = user_data[chat_id]
    answers = data["answers"]
    user = data["user"]

    fields = [
        "date",
        "telegram_id",
        "telegram_username",
    ] + [q["key"] for q in QUESTIONS]

    row = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "telegram_id": chat_id,
        "telegram_username": user.username or "",
    }

    for q in QUESTIONS:
        row[q["key"]] = answers.get(q["key"], "")

    file_exists = os.path.exists(DATA_FILE)

    with open(DATA_FILE, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        if not file_exists:
            writer.writeheader()
        writer.writerow(row)


@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id

    user_data[chat_id] = {
        "step": 0,
        "answers": {},
        "user": message.from_user,
    }

    bot.send_message(chat_id, INTRO_TEXT)
    ask_question(chat_id)


@bot.message_handler(func=lambda message: True)
def handle_answer(message):
    chat_id = message.chat.id

    if chat_id not in user_data:
        bot.send_message(chat_id, "Нажмите /start, чтобы начать тестирование.")
        return

    data = user_data[chat_id]
    question_index = get_next_question_index(chat_id)

    if question_index is None:
        save_result(chat_id)
        bot.send_message(chat_id, "Спасибо! Ваш отзыв сохранён ✅")
        user_data.pop(chat_id, None)
        return

    question = QUESTIONS[question_index]
    data["answers"][question["key"]] = message.text
    data["step"] = question_index + 1

    ask_question(chat_id)


print("Fleecing Test Lab Bot запущен")

while True:
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print("Ошибка подключения, перезапуск через 10 секунд:", e)
        import time
        time.sleep(10)
