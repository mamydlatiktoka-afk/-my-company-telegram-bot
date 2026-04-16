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

# Загрузка ключей с альтернативными именами
TELEGRAM_BOT_TOKEN = (
    os.environ.get('TELEGRAM_BOT_TOKEN') or 
    os.environ.get('TELEGRAM_TOKEN') or 
    os.environ.get('BOT_TOKEN')
)

OPENAI_API_KEY = (
    os.environ.get('OPENAI_API_KEY') or 
    os.environ.get('OPENAI_KEY') or 
    os.environ.get('AI_KEY')
)

# Детальная проверка ключей
logger.info("=== ПРОВЕРКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ===")
logger.info(f"TELEGRAM_BOT_TOKEN: {'***' if TELEGRAM_BOT_TOKEN else 'НЕТ'}")
logger.info(f"OPENAI_API_KEY: {'***' if OPENAI_API_KEY else 'НЕТ'}")

# Выведем все переменные окружения для диагностики (без значений)
all_vars = dict(os.environ)
logger.info("=== ВСЕ ПЕРЕМЕННЫЕ ОКРУЖЕНИЯ (имена) ===")
for var_name in sorted(all_vars.keys()):
    if any(keyword in var_name.upper() for keyword in ['TEL', 'OPEN', 'API', 'KEY', 'BOT']):
        logger.info(f"Найдена переменная: {var_name}")

if not TELEGRAM_BOT_TOKEN:
    logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Не найден TELEGRAM_BOT_TOKEN!")
    logger.error("Проверьте настройки Variables в Railway")
    exit(1)

if not OPENAI_API_KEY:
    logger.error("❌ КРИТИЧЕСКАЯ ОШИБКА: Не найден OPENAI_API_KEY!")
    logger.error("Проверьте настройки Variables в Railway")
    exit(1)

logger.info("✅ Все ключи успешно загружены")

# Инициализация клиента OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# База знаний
knowledge_base = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработка команды /start"""
    try:
        await update.message.reply_text('✅ Бот работает! Отправьте текст для обучения, затем задавайте вопросы.')
        logger.info("Команда /start выполнена успешно")
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
            await update.message.reply_text("📝 База пуста. Отправьте информацию для обучения.")
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
        logger.info("Ответ отправлен успешно")

    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await update.message.reply_text("⚠️ Ошибка обработки запроса")

def main():
    """Запуск бота"""
    try:
        logger.info("=== ЗАПУСК БОТА ===")
        
        app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        app.add_handler(CommandHandler("start", start))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        
        logger.info("✅ Бот запущен и готов к работе")
        app.run_polling()
        
    except Exception as e:
        logger.error(f"❌ Фатальная ошибка при запуске бота: {e}")

if __name__ == '__main__':
    main()
