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

# Загрузка ключей
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Проверка ключей
if not TELEGRAM_BOT_TOKEN:
    logger.error("❌ ОШИБКА: Не найден TELEGRAM_BOT_TOKEN!")
    exit(1)

if not OPENAI_API_KEY:
    logger.error("❌ ОШИБКА: Не найден OPENAI_API_KEY!")
    exit(1)

logger.info("✅ Ключи загружены")

# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# База знаний
knowledge_base = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    try:
        await update.message.reply_text('Привет! Я ваш ИИ-помощник. Отправьте мне текст для обучения, затем задавайте вопросы!')
    except Exception as e:
        logger.error(f"Ошибка в start: {e}")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка текстовых сообщений"""
    try:
        if not update.message or not update.message.text:
            return

        user_text = update.message.text
        user_name = update.message.from_user.first_name or "Аноним"

        logger.info(f"Сообщение от {user_name}: {user_text}")

        # Если сообщение длинное - добавляем в базу
        if len(user_text) > 100:
            knowledge_base.append(user_text)
            await update.message.reply_text("✅ Информация добавлена в базу!")
            return

        # Если база пуста
        if not knowledge_base:
            await update.message.reply_text("База пуста. Отправьте информацию для обучения.")
            return

        # Обработка вопроса
        context_text = "\n".join(knowledge_base[-3:])

        prompt = f"""Отвечай на основе информации:

{context_text}

Вопрос: {user_text}

Ответ:"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки")

def main():
    """Запуск бота"""
    try:
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("Бот запущен")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"Ошибка запуска: {e}")

if __name__ == '__main__':
    main()
