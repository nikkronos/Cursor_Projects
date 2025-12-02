from loader import bot, logger
from database import init_db
from services import start_scheduler
import handlers # Import handlers to register them
import signal
import sys

def signal_handler(sig, frame):
    """Обработчик сигналов для graceful shutdown"""
    logger.info("Получен сигнал завершения. Останавливаю бота...")
    bot.stop_polling()
    sys.exit(0)

if __name__ == '__main__':
    # Регистрируем обработчики сигналов для корректного завершения
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize Database
    init_db()
    
    # Start Scheduler
    start_scheduler()
    
    # Start Polling
    logger.info("Bot started (Main).")
    try:
        bot.polling(none_stop=True, interval=0, timeout=20)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
        sys.exit(1)

