import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import google.generativeai as genai
import os
from dotenv import load_dotenv
import requests

# Загружаем токены
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not BOT_TOKEN or not GEMINI_API_KEY:
    raise ValueError("❌ Ошибка: Проверь .env файл!")

# Подключаем API
bot = telebot.TeleBot(BOT_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)

# Главное меню
def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📈 Советы по инвестициям", "📊 Рыночные тренды")
    markup.add("❓ Случайный совет", "📉 Рыночные котировки")
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Я AI-консультант по инвестициям. Выбери действие:", reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text in ["📈 Советы по инвестициям", "📊 Рыночные тренды", "❓ Случайный совет", "📉 Рыночные котировки"])
def button_response(message):
    if message.text == "📉 Рыночные котировки":
        bot.send_message(message.chat.id, get_market_data(), reply_markup=main_menu())
        return

    query = {
        "📈 Советы по инвестициям": "Дай советы по инвестициям",
        "📊 Рыночные тренды": "Какие тренды на финансовых рынках сейчас?",
        "❓ Случайный совет": "Дай случайный совет по инвестициям"
    }[message.text]

    try:
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(query, generation_config={"max_output_tokens": 100})
        bot.send_message(message.chat.id, response.text, reply_markup=main_menu())
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка AI: {str(e)}", reply_markup=main_menu())

# Функция получения рыночных данных
def get_market_data():
    try:
        # Новый API для курса USD/KZT
        forex_url = "https://api.exchangerate-api.com/v4/latest/USD"
        forex_data = requests.get(forex_url).json()
        usd_kzt = round(forex_data["rates"]["KZT"], 2)

        # API CoinGecko (Bitcoin)
        btc_price = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd").json()["bitcoin"]["usd"]

        # API OilPrice (Brent) — требуется отдельный API, пока отключено
        brent_price = "Данные временно недоступны"

        return f"📊 Актуальные данные:\n\n💰 Доллар (USD/KZT): {usd_kzt}₸\n🛢 Нефть Brent: {brent_price} $\n₿ Bitcoin: {btc_price} $"

    except Exception as e:
        return f"Ошибка при получении данных: {str(e)}"

# Запуск бота
bot.polling()
