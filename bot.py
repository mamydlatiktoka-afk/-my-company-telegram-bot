import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from openai import OpenAI

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Загрузка ключей
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY')

# Проверка ключей
if not BOT_TOKEN or not DEEPSEEK_KEY:
    logger.error("❌ ОШИБКА: Не найдены ключи!")
    exit(1)

# Клиент DeepSeek
client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com/v1")

# База знаний
knowledge = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Я ваш AI-помощник! Отправьте мне информацию для запоминания, затем задавайте вопросы.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        text = update.message.text
        user = update.message.from_user.first_name

        # Если сообщение длинное - запоминаем
        if len(text) > 100:
            knowledge.append(text)
            await update.message.reply_text("✅ Запомнил!")
            return

        # Если база пуста
        if not knowledge:
            await update.message.reply_text("📝 Сначала отправьте информацию для обучения.")
            return

        # Собираем контекст
        context_text = "\n".join(knowledge[-3:])
        
        prompt = f"""Отвечай на основе информации:

{context_text}

Вопрос: {text}

Ответ:"""

        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500
        )
        
        answer = response.choices[0].message.content
        await update.message.reply_text(answer)

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        await update.message.reply_text("⚠️ Ошибка, попробуйте позже")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("Бот запущен!")
    app.run_polling()

if __name__ == '__main__':
    main()
