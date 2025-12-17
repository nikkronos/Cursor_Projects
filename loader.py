"""
Loader module for TradeTherapyBot.
Creates bot instance and logger to avoid circular imports.
"""
import logging
import os
from telebot import TeleBot
from config import load_config

# Load configuration
config = load_config()
BOT_TOKEN = config.get('BOT_TOKEN')
ADMIN_ID = int(config.get('ADMIN_ID')) if config.get('ADMIN_ID') else None
GROUP_CHAT_ID = int(config.get('GROUP_CHAT_ID')) if config.get('GROUP_CHAT_ID') else None
GROUP_INVITE_LINK = config.get('GROUP_INVITE_LINK', '')

# Ensure logs directory exists
os.makedirs('logs', exist_ok=True)

# Setup logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Setup receipt errors logger (separate file for ignored receipt attempts)
receipt_logger = logging.getLogger('receipt_errors')
receipt_logger.setLevel(logging.INFO)
receipt_handler = logging.FileHandler('logs/receipt_errors.log', encoding='utf-8')
receipt_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
receipt_logger.addHandler(receipt_handler)
receipt_logger.propagate = False  # Don't propagate to root logger

# Create bot instance
if BOT_TOKEN:
    bot = TeleBot(BOT_TOKEN)
    logger.info("Bot instance created successfully.")
else:
    logger.warning("Bot token not found. Using mock bot for testing. Handlers will be registered but won't work.")
    # Create a mock bot object to avoid import errors
    bot = None
