import telebot
import logging
import os
from config import load_config

# Загрузка конфига
config = load_config()
BOT_TOKEN = config['BOT_TOKEN']
ADMIN_ID = int(config['ADMIN_ID'])
GROUP_CHAT_ID = int(config['GROUP_CHAT_ID'])
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

# Инициализация бота
bot = telebot.TeleBot(BOT_TOKEN)

