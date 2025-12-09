"""
Utility functions for TradeTherapyBot.
Contains retry mechanisms, rate limiting, and safe message sending.
"""
import time
import logging
from typing import Callable, Any, Optional, Dict, List, Tuple
from functools import wraps
from collections import defaultdict, deque
from loader import ADMIN_ID, bot, logger

# Rate limiting storage
_rate_limit_history: Dict[int, deque] = defaultdict(lambda: deque())
_user_blocks: Dict[int, float] = {}  # {user_id: block_until_timestamp}


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


def safe_send_message(bot_instance: Any, chat_id: int, text: str, **kwargs) -> Optional[Any]:
    """
    Safely send a message with retry mechanism.
    
    Args:
        bot_instance: Bot instance
        chat_id: Chat ID to send message to
        text: Message text
        **kwargs: Additional arguments for send_message
    
    Returns:
        Message object if successful, None if failed
    """
    def send_func(**send_kwargs):
        return bot_instance.send_message(chat_id, text, **send_kwargs)
    
    try:
        return retry_telegram_api(send_func, max_attempts=3, **kwargs)
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id} after retries: {e}")
        return None


def rate_limit(max_requests: int = 10, time_window: float = 15.0, block_duration: float = 30.0):
    """
    Decorator for rate limiting message handlers.
    
    Args:
        max_requests: Maximum number of requests allowed
        time_window: Time window in seconds
        block_duration: Duration to block user in seconds after exceeding limit
    
    Returns:
        Decorated function
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(message: Any, *args, **kwargs) -> Any:
            # Skip rate limiting for admin
            if hasattr(message, 'from_user') and message.from_user.id == ADMIN_ID:
                return func(message, *args, **kwargs)
            
            # Skip rate limiting for non-private chats (groups, channels)
            if hasattr(message, 'chat') and hasattr(message.chat, 'type'):
                if message.chat.type != 'private':
                    return func(message, *args, **kwargs)
            
            user_id = message.from_user.id if hasattr(message, 'from_user') else None
            if not user_id:
                return func(message, *args, **kwargs)
            
            current_time = time.time()
            
            # Check if user is blocked
            if user_id in _user_blocks:
                if current_time < _user_blocks[user_id]:
                    # User is still blocked, ignore request
                    return
                else:
                    # Block expired, remove it
                    del _user_blocks[user_id]
            
            # Clean old entries and check rate limit
            if user_id in _rate_limit_history:
                # Remove entries older than time_window
                while _rate_limit_history[user_id] and current_time - _rate_limit_history[user_id][0] > time_window:
                    _rate_limit_history[user_id].popleft()
                
                # Check if limit exceeded
                if len(_rate_limit_history[user_id]) >= max_requests:
                    # Block user
                    block_until = current_time + block_duration
                    _user_blocks[user_id] = block_until
                    
                    # Log and notify admin
                    user_name = getattr(message.from_user, 'first_name', 'Unknown')
                    username = getattr(message.from_user, 'username', None)
                    username_str = f"@{username}" if username else "нет username"
                    
                    warning_msg = (
                        f"Rate limit exceeded by user {user_id} ({user_name}, {username_str}). "
                        f"{len(_rate_limit_history[user_id])} requests in {time_window:.1f}s (limit: {max_requests}). "
                        f"Blocked for {block_duration:.1f} seconds."
                    )
                    logger.warning(warning_msg)
                    
                    # Send notification to admin
                    try:
                        bot.send_message(ADMIN_ID, warning_msg)
                    except Exception as e:
                        logger.error(f"Failed to send rate limit notification to admin: {e}")
                    
                    # Send warning to user
                    try:
                        bot.send_message(
                            user_id,
                            f"Вы превысили лимит запросов. Пожалуйста, подождите {block_duration:.0f} секунд."
                        )
                    except Exception as e:
                        logger.error(f"Failed to send rate limit warning to user {user_id}: {e}")
                    
                    return
            
            # Add current request to history
            if user_id not in _rate_limit_history:
                _rate_limit_history[user_id] = deque()
            _rate_limit_history[user_id].append(current_time)
            
            # Call the original function
            return func(message, *args, **kwargs)
        
        return wrapper
    return decorator


def escape_markdown(text: str) -> str:
    """
    Escape special Markdown characters in text.
    
    Args:
        text: Text to escape
    
    Returns:
        Escaped text safe for Markdown
    """
    if not text:
        return text
    
    # Escape special Markdown characters: _ * [ ] ( ) ~ ` > # + - = | { } . !
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    for char in escape_chars:
        text = text.replace(char, f'\\{char}')
    
    return text
