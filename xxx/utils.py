"""
Utility functions for Копия иксуюемся.
Contains retry mechanisms and safe message sending.
"""
import time
import logging
from typing import Callable, Any, Optional
from loader import logger

def retry_telegram_api(func: Callable, max_attempts: int = 3, base_delay: float = 1.0, **kwargs) -> Any:
    """
    Retry mechanism for Telegram API calls with exponential backoff.
    
    Args:
        func: Function to call
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        **kwargs: Arguments to pass to the function
    
    Returns:
        Result of the function call
    
    Raises:
        Exception: If all retry attempts fail
    """
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return func(**kwargs)
        except (ConnectionError, TimeoutError) as e:
            last_exception = e
            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Retry attempt {attempt + 1}/{max_attempts} after {delay}s: {e}")
                time.sleep(delay)
            else:
                logger.error(f"All {max_attempts} retry attempts failed: {e}")
                raise
        except Exception as e:
            error_str = str(e)
            # Check for rate limit error (429)
            if "429" in error_str or "Too Many Requests" in error_str:
                # Try to extract retry_after from error message
                retry_after = base_delay
                if "retry_after:" in error_str:
                    try:
                        retry_after = float(error_str.split("retry_after:")[1].split()[0])
                    except (ValueError, IndexError):
                        pass
                
                if attempt < max_attempts - 1:
                    logger.warning(f"Rate limit hit, waiting {retry_after}s before retry {attempt + 1}/{max_attempts}")
                    time.sleep(retry_after)
                    last_exception = e
                    continue
                else:
                    logger.error(f"Rate limit error after {max_attempts} attempts: {e}")
                    raise
            else:
                # Non-retryable error, raise immediately
                raise
    
    if last_exception:
        raise last_exception


async def safe_send_message(bot_instance: Any, chat_id: int, text: str, **kwargs) -> Optional[Any]:
    """
    Safely send a message with retry mechanism (async version for aiogram).
    
    Args:
        bot_instance: Bot instance (aiogram Bot)
        chat_id: Chat ID to send message to
        text: Message text
        **kwargs: Additional arguments for send_message
    
    Returns:
        Message object if successful, None if failed
    """
    async def send_func(**send_kwargs):
        return await bot_instance.send_message(chat_id, text, **send_kwargs)
    
    try:
        # For async functions, we need to call them differently
        return await send_func(**kwargs)
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id}: {e}")
        # Try retry mechanism
        try:
            return await retry_telegram_api_async(send_func, max_attempts=3, **kwargs)
        except Exception as retry_error:
            logger.error(f"Failed to send message to {chat_id} after retries: {retry_error}")
            return None


async def retry_telegram_api_async(func: Callable, max_attempts: int = 3, base_delay: float = 1.0, **kwargs) -> Any:
    """
    Retry mechanism for async Telegram API calls with exponential backoff.
    
    Args:
        func: Async function to call
        max_attempts: Maximum number of retry attempts
        base_delay: Base delay in seconds for exponential backoff
        **kwargs: Arguments to pass to the function
    
    Returns:
        Result of the function call
    
    Raises:
        Exception: If all retry attempts fail
    """
    import asyncio
    last_exception = None
    
    for attempt in range(max_attempts):
        try:
            return await func(**kwargs)
        except (ConnectionError, TimeoutError) as e:
            last_exception = e
            if attempt < max_attempts - 1:
                delay = base_delay * (2 ** attempt)
                logger.warning(f"Retry attempt {attempt + 1}/{max_attempts} after {delay}s: {e}")
                await asyncio.sleep(delay)
            else:
                logger.error(f"All {max_attempts} retry attempts failed: {e}")
                raise
        except Exception as e:
            error_str = str(e)
            # Check for rate limit error (429)
            if "429" in error_str or "Too Many Requests" in error_str:
                retry_after = base_delay
                if "retry_after:" in error_str:
                    try:
                        retry_after = float(error_str.split("retry_after:")[1].split()[0])
                    except (ValueError, IndexError):
                        pass
                
                if attempt < max_attempts - 1:
                    logger.warning(f"Rate limit hit, waiting {retry_after}s before retry {attempt + 1}/{max_attempts}")
                    await asyncio.sleep(retry_after)
                    last_exception = e
                    continue
                else:
                    logger.error(f"Rate limit error after {max_attempts} attempts: {e}")
                    raise
            else:
                # Non-retryable error, raise immediately
                raise
    
    if last_exception:
        raise last_exception
