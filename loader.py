import telebot
import logging
import os
from config import load_config

# Загрузка конфига (безопасная, для тестирования)
try:
    config = load_config()
    BOT_TOKEN = config.get('BOT_TOKEN')
    ADMIN_ID = int(config['ADMIN_ID']) if config.get('ADMIN_ID') else None
    GROUP_CHAT_ID = int(config['GROUP_CHAT_ID']) if config.get('GROUP_CHAT_ID') else None
except (TypeError, ValueError, KeyError):
    # Для тестирования, если конфиг не загружен
    BOT_TOKEN = None
    ADMIN_ID = None
    GROUP_CHAT_ID = None

GROUP_INVITE_LINK = 'https://t.me/+IBT7qa_VMBk5Mjgy'

# Настройка логирования
os.makedirs('logs', exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Инициализация бота (только если токен доступен)
try:
    bot = telebot.TeleBot(BOT_TOKEN) if BOT_TOKEN else None
except Exception:
    # Для тестирования, если бот не может быть инициализирован
    bot = None

