from typing import Optional, Any
import telebot
import logging
import os
from config import load_config

# Загрузка конфига (безопасная, для тестирования)
try:
    config = load_config()
    BOT_TOKEN = config.get('BOT_TOKEN')
    admin_id_str = config.get('ADMIN_ID')
    ADMIN_ID = int(admin_id_str) if admin_id_str else None
    group_chat_id_str = config.get('GROUP_CHAT_ID')
    GROUP_CHAT_ID = int(group_chat_id_str) if group_chat_id_str else None
except (TypeError, ValueError, KeyError) as e:
    # Для тестирования, если конфиг не загружен
    BOT_TOKEN = None
    ADMIN_ID = None
    GROUP_CHAT_ID = None
    logger.debug(f"Config loading failed (this is OK for testing): {e}")

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

# MockBot для тестирования (когда нет токена)
class MockBot:
    """Mock объект бота для тестирования без токена"""
    def __init__(self) -> None:
        self.message_handlers = []
        self.callback_query_handlers = []
        self.chat_join_request_handlers = []
        self.chat_member_handlers = []
    
    def message_handler(self, *args: Any, **kwargs: Any) -> Any:
        """Mock декоратор для message_handler"""
        def decorator(func: Any) -> Any:
            self.message_handlers.append(func)
            return func
        return decorator
    
    def callback_query_handler(self, *args: Any, **kwargs: Any) -> Any:
        """Mock декоратор для callback_query_handler"""
        def decorator(func: Any) -> Any:
            self.callback_query_handlers.append(func)
            return func
        return decorator
    
    def chat_join_request_handler(self, *args: Any, **kwargs: Any) -> Any:
        """Mock декоратор для chat_join_request_handler"""
        def decorator(func: Any) -> Any:
            self.chat_join_request_handlers.append(func)
            return func
        return decorator
    
    def chat_member_handler(self, *args: Any, **kwargs: Any) -> Any:
        """Mock декоратор для chat_member_handler"""
        def decorator(func: Any) -> Any:
            self.chat_member_handlers.append(func)
            return func
        return decorator
    
    def stop_polling(self) -> None:
        """Mock метод для stop_polling"""
        pass
    
    def polling(self, *args: Any, **kwargs: Any) -> None:
        """Mock метод для polling (для тестирования)"""
        logger.warning("Mock bot polling called. Bot is not initialized (no token).")
        # В тестовом режиме просто ждем бесконечно (можно прервать Ctrl+C)
        import time
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Polling stopped by user")

# Инициализация бота (только если токен доступен)
try:
    if BOT_TOKEN:
        bot = telebot.TeleBot(BOT_TOKEN)
    else:
        # Для тестирования создаем mock объект, чтобы декораторы работали
        bot = MockBot()
        logger.warning("Bot token not found. Using mock bot for testing. Handlers will be registered but won't work.")
except Exception as e:
    # Для тестирования, если бот не может быть инициализирован
    bot = MockBot()
    logger.warning(f"Bot initialization failed: {e}. Using mock bot for testing.")

