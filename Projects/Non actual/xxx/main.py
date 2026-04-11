"""
Main entry point for Копия иксуюемся.
Initializes database, starts userbot and management bot.
"""
import asyncio
import signal
import sys
from typing import Any, Optional
from loader import bot, dp, logger, userbot_logger
from database import init_db
from config import load_config
from userbot import start_userbot, stop_userbot, run_userbot

# Import handlers to register them
from handlers.user import router as user_router

# Global variable to store userbot task
userbot_task: Optional[asyncio.Task] = None

def signal_handler(sig: Any, frame: Any) -> None:
    """Обработчик сигналов для graceful shutdown"""
    logger.info("Получен сигнал завершения. Останавливаю бота...")
    # Stop userbot gracefully
    if userbot_task and not userbot_task.done():
        userbot_task.cancel()
    # Stop dispatcher
    if dp:
        asyncio.create_task(dp.stop_polling())
    sys.exit(0)

async def main() -> None:
    """Main async function to start the bot."""
    # Register signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Initialize Database
    logger.info("Initializing database...")
    init_db()
    
    # Load configuration
    config = load_config()
    
    # Validate configuration
    if not config.get('BOT_TOKEN'):
        logger.error("BOT_TOKEN not found in env_vars.txt. Bot cannot start.")
        sys.exit(1)
    
    # Start userbot if configured
    global userbot_task
    if config.get('API_ID') and config.get('API_HASH') and config.get('PHONE_NUMBER'):
        logger.info("Starting userbot...")
        try:
            # Set copy handler callback before starting userbot
            try:
                from copy_handler import copy_message
                from userbot import set_copy_handler
                set_copy_handler(copy_message)
                logger.info("Copy handler set for userbot.")
            except Exception as e:
                logger.warning(f"Could not set copy handler: {e}")
                logger.warning("Messages will be logged but not copied.")
            
            # Start userbot in background task
            userbot_task = asyncio.create_task(run_userbot())
            logger.info("Userbot task created.")
            # Give userbot time to start
            await asyncio.sleep(2)
        except Exception as e:
            logger.error(f"Error starting userbot: {e}")
            logger.warning("Continuing without userbot...")
    else:
        logger.warning("API_ID, API_HASH or PHONE_NUMBER not found. Userbot will not start.")
    
    # Register handlers
    if dp:
        dp.include_router(user_router)
        logger.info("Handlers registered.")
    
    # Start bot polling
    logger.info("Starting management bot...")
    try:
        # Start polling (aiogram 3.x syntax)
        # This will run until stopped
        await dp.start_polling(bot, skip_updates=True)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        # Stop userbot if running
        if userbot_task and not userbot_task.done():
            userbot_task.cancel()
            try:
                await userbot_task
            except asyncio.CancelledError:
                pass
        sys.exit(1)
    finally:
        # Stop userbot gracefully
        if userbot_task and not userbot_task.done():
            logger.info("Stopping userbot...")
            userbot_task.cancel()
            try:
                await userbot_task
            except asyncio.CancelledError:
                pass
        # Stop userbot client
        from userbot import stop_userbot
        await stop_userbot()

if __name__ == '__main__':
    try:
        logger.info("Bot started (Main).")
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
