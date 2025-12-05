"""
Loader module for TradeTherapyBot.
Creates bot instance and logger to avoid circular imports.
"""
import logging
import os
from telebot import TeleBot
from config import load_config

# Create logs directory if it doesn't exist
os.makedirs('logs', exist_ok=True)

# Load configuration
config = load_config()

# Bot token
BOT_TOKEN = config.get('BOT_TOKEN')
if not BOT_TOKEN:
    raise ValueError("BOT_TOKEN not found in env_vars.txt")

# Admin ID
ADMIN_ID = int(config.get('ADMIN_ID', 0)) if config.get('ADMIN_ID') else None
if not ADMIN_ID:
    raise ValueError("ADMIN_ID not found in env_vars.txt")

# Group chat ID
GROUP_CHAT_ID = int(config.get('GROUP_CHAT_ID', 0)) if config.get('GROUP_CHAT_ID') else None
if not GROUP_CHAT_ID:
    raise ValueError("GROUP_CHAT_ID not found in env_vars.txt")

# Group invite link
GROUP_INVITE_LINK = 'https://t.me/+jpWPa5zAj61lMWI6'

# Initialize bot
bot = TeleBot(BOT_TOKEN)

# Configure logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('loader')
