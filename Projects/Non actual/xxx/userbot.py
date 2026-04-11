"""
Pyrogram Userbot module for Копия иксуюемся.
Reads messages from source channel and passes them to copy handler.
"""
import asyncio
from typing import Optional, Callable
from pyrogram import Client, idle
from pyrogram.handlers import MessageHandler
from pyrogram.types import Message
from loader import API_ID, API_HASH, PHONE_NUMBER, SOURCE_CHANNEL_ID, userbot_logger

# Global variable to store copy handler callback
copy_handler_callback: Optional[Callable] = None

# Pyrogram client instance
userbot_client: Optional[Client] = None


def set_copy_handler(callback: Callable) -> None:
    """
    Set callback function for handling copied messages.
    
    Args:
        callback: Function to call when message is received
    """
    global copy_handler_callback
    copy_handler_callback = callback
    userbot_logger.info("Copy handler callback set.")


async def handle_new_message(client: Client, message: Message) -> None:
    """
    Handle new message from source channel.
    
    Args:
        client: Pyrogram client instance
        message: Received message
    """
    try:
        # Check if message is from source channel
        if str(message.chat.id) != str(SOURCE_CHANNEL_ID):
            return
        
        # Log received message
        userbot_logger.info(
            f"Received message {message.id} from channel {message.chat.id} "
            f"(type: {message.media if message.media else 'text'})"
        )
        
        # Pass message to copy handler if set
        if copy_handler_callback:
            try:
                await copy_handler_callback(message)
                userbot_logger.info(f"Message {message.id} passed to copy handler successfully.")
            except Exception as e:
                userbot_logger.error(f"Error in copy handler for message {message.id}: {e}")
        else:
            userbot_logger.warning(f"Copy handler not set. Message {message.id} not processed.")
            
    except Exception as e:
        userbot_logger.error(f"Error handling message {message.id}: {e}")


async def start_userbot() -> Optional[Client]:
    """
    Start Pyrogram userbot client.
    
    Returns:
        Client instance if started successfully, None otherwise
    """
    global userbot_client
    
    if not API_ID or not API_HASH:
        userbot_logger.error("API_ID or API_HASH not configured. Userbot cannot start.")
        return None
    
    if not PHONE_NUMBER:
        userbot_logger.error("PHONE_NUMBER not configured. Userbot cannot start.")
        return None
    
    if not SOURCE_CHANNEL_ID:
        userbot_logger.error("SOURCE_CHANNEL_ID not configured. Userbot cannot start.")
        return None
    
    try:
        userbot_logger.info("Initializing Pyrogram userbot client...")
        
        # Create Pyrogram client
        userbot_client = Client(
            name="userbot",
            api_id=API_ID,
            api_hash=API_HASH,
            phone_number=PHONE_NUMBER,
            workdir="."
        )
        
        # Add message handler
        userbot_client.add_handler(
            MessageHandler(handle_new_message)
        )
        
        # Start client
        await userbot_client.start()
        userbot_logger.info("Pyrogram userbot started successfully.")
        
        # Set Pyrogram client in copy_handler immediately (so photo/media download works before dialogs load)
        try:
            from copy_handler import set_pyrogram_client
            set_pyrogram_client(userbot_client)
            userbot_logger.info("Pyrogram client set in copy handler.")
        except Exception as e:
            userbot_logger.warning(f"Could not set Pyrogram client in copy handler: {e}")
        
        # Get info about connected account
        me = await userbot_client.get_me()
        userbot_logger.info(f"Userbot connected as: {me.first_name} (@{me.username})")
        
        # Verify access to source channel
        try:
            source_channel = await userbot_client.get_chat(int(SOURCE_CHANNEL_ID))
            userbot_logger.info(f"Access to source channel verified: {source_channel.title}")
        except Exception as e:
            userbot_logger.warning(f"Could not verify access to source channel {SOURCE_CHANNEL_ID}: {e}")
            userbot_logger.warning("Make sure userbot is a member of the source channel.")
        
        # Pre-load dialogs so Pyrogram session has all peers in cache (avoids "Peer id invalid" on first update)
        try:
            async for _ in userbot_client.get_dialogs():
                pass
            userbot_logger.info("Dialogs pre-loaded (session cache warmed).")
        except Exception as e:
            userbot_logger.warning(f"Could not pre-load dialogs: {e}")
        
        return userbot_client
        
    except Exception as e:
        userbot_logger.error(f"Error starting userbot: {e}")
        return None


async def stop_userbot() -> None:
    """
    Stop Pyrogram userbot client gracefully.
    """
    global userbot_client
    
    if userbot_client:
        try:
            userbot_logger.info("Stopping Pyrogram userbot...")
            await userbot_client.stop()
            userbot_logger.info("Pyrogram userbot stopped successfully.")
        except Exception as e:
            userbot_logger.error(f"Error stopping userbot: {e}")
        finally:
            userbot_client = None


async def run_userbot() -> None:
    """
    Run userbot in async loop.
    This function should be called from main.py.
    """
    try:
        client = await start_userbot()
        if client:
            # Keep running until signal (CTRL+C). client.idle() in a task can return early;
            # pyrogram.idle() blocks until signal and keeps session alive.
            userbot_logger.info("Userbot entering idle (waiting for messages)...")
            await idle()
        else:
            userbot_logger.error("Userbot client not started. Exiting.")
    except KeyboardInterrupt:
        userbot_logger.info("Userbot stopped by user.")
    except Exception as e:
        userbot_logger.error(f"Fatal error in userbot: {e}")
    finally:
        await stop_userbot()
