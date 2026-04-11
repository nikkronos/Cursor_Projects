"""
Loader module for Копия иксуюемся.
Creates bot instance and logger to avoid circular imports.
"""
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from config import load_config

# Load configuration
config = load_config()
BOT_TOKEN = config.get('BOT_TOKEN')
ADMIN_ID = int(config.get('ADMIN_ID')) if config.get('ADMIN_ID') else None
SOURCE_CHANNEL_ID = config.get('SOURCE_CHANNEL_ID')
TARGET_CHANNEL_ID = config.get('TARGET_CHANNEL_ID')

# Pyrogram Userbot configuration
API_ID = int(config.get('API_ID')) if config.get('API_ID') else None
API_HASH = config.get('API_HASH')
PHONE_NUMBER = config.get('PHONE_NUMBER')

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

# Setup userbot logger (separate file for userbot operations)
userbot_logger = logging.getLogger('userbot')
userbot_logger.setLevel(logging.INFO)
userbot_handler = logging.FileHandler('logs/userbot.log', encoding='utf-8')
userbot_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
userbot_logger.addHandler(userbot_handler)
userbot_logger.propagate = False  # Don't propagate to root logger

# Create bot instance (aiogram)
if BOT_TOKEN:
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher()
    logger.info("Bot instance created successfully.")
else:
    logger.warning("Bot token not found. Using mock bot for testing. Handlers will be registered but won't work.")
    bot = None
    dp = None

# Validate configuration
if not BOT_TOKEN:
    logger.warning("BOT_TOKEN not found in env_vars.txt")
if not API_ID or not API_HASH:
    logger.warning("API_ID or API_HASH not found in env_vars.txt - userbot will not work")
if not SOURCE_CHANNEL_ID or not TARGET_CHANNEL_ID:
    logger.warning("SOURCE_CHANNEL_ID or TARGET_CHANNEL_ID not found in env_vars.txt")
