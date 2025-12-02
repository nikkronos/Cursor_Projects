from loader import bot, logger
from database import init_db
from services import start_scheduler
import handlers # Import handlers to register them

if __name__ == '__main__':
    # Initialize Database
    init_db()
    
    # Start Scheduler
    start_scheduler()
    
    # Start Polling
    logger.info("Bot started (Main).")
    bot.polling(none_stop=True)

