from typing import Any
from loader import bot, logger
from database import init_db, migrate_add_indexes
from services import start_scheduler
import handlers # Import handlers to register them
import signal
import sys

def signal_handler(sig: Any, frame: Any) -> None:
    """Обработчик сигналов для graceful shutdown"""
    logger.info("Получен сигнал завершения. Останавливаю бота...")
    if bot and hasattr(bot, 'stop_polling'):
        bot.stop_polling()
    sys.exit(0)

if __name__ == '__main__':
    # Регистрируем обработчики сигналов для корректного завершения
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize Database
    init_db()
    
    # Migrate existing database (add indexes if needed)
    migrate_add_indexes()
    
    # Start Scheduler
    start_scheduler()
    
    # Start Polling
    logger.info("Bot started (Main).")
    try:
        if bot and hasattr(bot, 'polling'):
            bot.polling(none_stop=True, interval=0, timeout=20)
        else:
            logger.error("Bot is not initialized. Please check BOT_TOKEN in env_vars.txt")
            sys.exit(1)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)

