import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from openai import OpenAI

# Настраиваем логирование
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Ваши ключи! Они подставятся из переменных окружения Railway.
TELEGRAM_BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')

# Инициализируем клиент OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Простая база знаний в памяти (для начала)
knowledge_base = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start"""
    await update.message.reply_text(
        'Привет! Я ваш ИИ-помощник. Отправьте мне текст или файл, чтобы я его запомнил. Затем задавайте вопросы! Если я не знаю ответа, я сообщу вашему руководителю.'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает все текстовые сообщения"""
    user_text = update.message.text
    user_name = update.message.from_user.first_name

    # Логируем вопрос
    logger.info(f"Вопрос от {user_name}: {user_text}")

    # Если сообщение длинное, считаем это "знанием" для базы
    if len(user_text) > 150:
        knowledge_base.append(user_text)
        await update.message.reply_text("✅ Информация добавлена в базу знаний!")
        return

    # Это вопрос. Готовим контекст из базы знаний.
    context_text = "\n".join(knowledge_base) if knowledge_base else "База знаний пока пуста."

    # Создаем умный запрос к ИИ
    prompt = f"""Ты — ассистент для внутренних сотрудников компании. Отвечай ТОЛЬКО на основе предоставленной информации.
Если ответа в информации нет, или вопрос сложный/юридический, или пользователь недоволен, НЕ придумывай ответ, а напиши строго вот это: <<ESCALATE>>.

Информация из базы знаний компании:
{context_text}

Вопрос сотрудника: {user_text}

Ответ:"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Экономная и быстрая модель
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        answer = response.choices[0].message.content.strip()

        # Проверяем, не требует ли вопрос эскалации
        if "<<ESCALATE>>" in answer:
            # Здесь должна быть логика отправки сообщения вам в личку.
            # Пока просто сообщим пользователю.
            await update.message.reply_text("🤔 Ваш вопрос сложный. Я передал его специалисту, ожидайте ответа.")
            # В идеале здесь код, который пишет вам: "Вопрос от [user_name]: [user_text]"
            logger.warning(f"ТРЕБУЕТСЯ ЭСКАЛАЦИЯ от {user_name}: {user_text}")
        else:
            await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("⚠️ Произошла техническая ошибка. Попробуйте позже.")

def main():
    """Запуск бота"""
    if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
        logger.error("Не заданы TELEGRAM_BOT_TOKEN или OPENAI_API_KEY!")
        return

    # Создаем приложение и передаем ему токен
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Запускаем бота
    application.run_polling(allowed_updates=Update.ALL_TYPES)
    logger.info("Бот запущен!")

if __name__ == '__main__':
    main()
