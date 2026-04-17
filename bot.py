import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes, CommandHandler
from openai import OpenAI

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ДИАГНОСТИКА: Выведем все переменные окружения
logger.info("=== ДИАГНОСТИКА ПЕРЕМЕННЫХ ОКРУЖЕНИЯ ===")
all_vars = os.environ
for var_name, var_value in all_vars.items():
    if any(keyword in var_name.upper() for keyword in ['BOT', 'TOKEN', 'DEEPSEEK', 'KEY', 'API']):
        logger.info(f"Найдена переменная: {var_name} = {'***' if var_value else 'ПУСТО'}")

# Загрузка ключей
BOT_TOKEN = os.environ.get('BOT_TOKEN')
DEEPSEEK_KEY = os.environ.get('DEEPSEEK_KEY')

logger.info(f"BOT_TOKEN: {'***' if BOT_TOKEN else 'НЕТ'}")
logger.info(f"DEEPSEEK_KEY: {'***' if DEEPSEEK_KEY else 'НЕТ'}")

# Проверка ключей
if not BOT_TOKEN or not DEEPSEEK_KEY:
    logger.error("❌ ОШИБКА: Не найдены ключи!")
    # Выведем все доступные переменные для отладки
    logger.info("=== ВСЕ ДОСТУПНЫЕ ПЕРЕМЕННЫЕ ===")
    for var_name in sorted(all_vars.keys()):
        logger.info(f"Переменная: {var_name}")
    exit(1)

# Клиент DeepSeek
client = OpenAI(api_key=DEEPSEEK_KEY, base_url="https://api.deepseek.com/v1")
logger.info("✅ Ключи загружены успешно!")

# ... остальной код без изменений ...
