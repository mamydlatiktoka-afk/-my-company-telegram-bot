import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from openai import OpenAI

# Настраиваем логирование
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Безопасная загрузка ключей из переменных окружения
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# ПРОВЕРКА КЛЮЧЕЙ ПРИ ЗАПУСКЕ
if not TELEGRAM_BOT_TOKEN:
    logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Не найден TELEGRAM_BOT_TOKEN!")
    exit(1)

if not OPENAI_API_KEY:
    logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Не найден OPENAI_API_KEY!")
    exit(1)

logger.info("✅ Ключи успешно загружены.")

# Инициализируем клиент OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Простая база знаний в памяти
knowledge_base = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start"""
    await update.message.reply_text(
        'Привет! Я ваш ИИ-помощник. Отправьте мне текст или файл, чтобы я его запомнил. Затем задавайте вопросы!'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает все текстовые сообщения"""
    try:
        # Проверяем, есть ли текст в сообщении
        if not update.message or not update.message.text:
            await update.message.reply_text("Я понимаю только текстовые сообщения.")
            return

        user_text = update.message.text
        user_name = update.message.from_user.first_name or "Аноним"

        logger.info(f"Получено сообщение от {user_name}: {user_text}")

        # Если сообщение длинное - добавляем в базу знаний
        if len(user_text) > 150:
            knowledge_base.append(user_text)
            await update.message.reply_text("✅ Информация добавлена в базу знаний!")
            return

        # Если база знаний пуста
        if not knowledge_base:
            await update.message.reply_text("База знаний пуста. Отправьте мне информацию для обучения.")
            return

        # Это вопрос - обрабатываем
        context_text = "\n".join(knowledge_base[-3:])  # Берем 3 послед
