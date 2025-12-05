"""
Утилиты для работы с Telegram Bot API
Включает механизм retry для обработки временных ошибок и rate limiting
"""
import time
from typing import Callable, Any, Optional, Dict, List
from collections import defaultdict, deque
from functools import wraps
from loader import logger, ADMIN_ID, bot


def retry_telegram_api(
    func: Callable[..., Any],
    max_attempts: int = 3,
    base_delay: float = 1.0,
    *args: Any,
    **kwargs: Any
) -> Any:
    """
    Выполняет функцию с автоматическими повторами при временных ошибках Telegram API.
    
    Args:
        func: Функция для выполнения
        max_attempts: Максимальное количество попыток (по умолчанию 3)
        base_delay: Базовая задержка в секундах для экспоненциальной задержки (1, 2, 4 сек)
        *args, **kwargs: Аргументы для передачи в функцию
    
    Returns:
        Результат выполнения функции
    
    Raises:
        Последнее исключение после исчерпания всех попыток
    """
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if attempt > 1:
                func_name = getattr(func, '__name__', str(func))
                logger.info(f"Telegram API call succeeded on attempt {attempt}: {func_name}")
            return result
            
        except Exception as e:
            last_exception = e
            error_str = str(e)
            
            # Проверка на rate limiting (429 ошибка)
            is_rate_limit = (
                "429" in error_str or
                "Too Many Requests" in error_str or
                "retry_after" in error_str.lower()
            )
            
            # Проверка на временные ошибки (сетевые, таймауты)
            is_temporary_error = (
                isinstance(e, (ConnectionError, TimeoutError)) or
                "timeout" in error_str.lower() or
                "connection" in error_str.lower() or
                "network" in error_str.lower()
            )
            
            # Если это не временная ошибка и не rate limit - не повторяем
            if not (is_rate_limit or is_temporary_error):
                logger.warning(f"Telegram API call failed with non-retryable error: {error_str}")
                raise
            
            # Если это последняя попытка - логируем и выбрасываем исключение
            if attempt == max_attempts:
                func_name = getattr(func, '__name__', str(func))
                logger.error(
                    f"Telegram API call failed after {max_attempts} attempts: {func_name}. "
                    f"Error: {error_str}"
                )
                raise
            
            # Вычисляем задержку
            if is_rate_limit:
                # Для rate limiting пытаемся извлечь retry_after
                # Telegram API обычно возвращает retry_after в секундах
                try:
                    # Если в сообщении об ошибке есть число - используем его как задержку
                    import re
                    retry_match = re.search(r'retry[_\s]?after[:\s]+(\d+)', error_str, re.IGNORECASE)
                    if retry_match:
                        delay = float(retry_match.group(1))
                        func_name = getattr(func, '__name__', str(func))
                        logger.warning(
                            f"Rate limit hit (attempt {attempt}/{max_attempts}): {func_name}. "
                            f"Waiting {delay} seconds as requested by API."
                        )
                    else:
                        # Если не нашли retry_after, используем экспоненциальную задержку
                        delay = base_delay * (2 ** (attempt - 1))
                        func_name = getattr(func, '__name__', str(func))
                        logger.warning(
                            f"Rate limit hit (attempt {attempt}/{max_attempts}): {func_name}. "
                            f"Waiting {delay} seconds (exponential backoff)."
                        )
                except Exception:
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Rate limit hit (attempt {attempt}/{max_attempts}): {func.__name__}. "
                        f"Waiting {delay} seconds (exponential backoff)."
                    )
            else:
                # Экспоненциальная задержка для временных ошибок
                delay = base_delay * (2 ** (attempt - 1))
                func_name = getattr(func, '__name__', str(func))
                logger.warning(
                    f"Telegram API temporary error (attempt {attempt}/{max_attempts}): {func_name}. "
                    f"Error: {error_str}. Retrying in {delay} seconds..."
                )
            
            time.sleep(delay)
    
    # Этот код не должен достигнуться, но на всякий случай
    if last_exception:
        raise last_exception


# Rate limiting: хранение истории запросов и блокировок
_rate_limit_history: Dict[int, deque] = defaultdict(lambda: deque())
_user_blocks: Dict[int, float] = {}  # {user_id: unblock_timestamp}


def check_rate_limit(user_id: int, max_requests: int, time_window: float) -> bool:
    """
    Проверяет, не превышен ли лимит запросов для пользователя.
    
    Args:
        user_id: ID пользователя
        max_requests: Максимальное количество запросов
        time_window: Окно времени в секундах
    
    Returns:
        True если лимит не превышен, False если превышен
    """
    from loader import ADMIN_ID
    
    # Администратор не ограничивается
    if user_id == ADMIN_ID:
        return True
    
    # Проверка блокировки
    current_time = time.time()
    if user_id in _user_blocks:
        if current_time < _user_blocks[user_id]:
            # Пользователь все еще заблокирован
            return False
        else:
            # Блокировка истекла, удаляем
            del _user_blocks[user_id]
    
    # Получаем историю запросов пользователя
    request_times = _rate_limit_history[user_id]
    
    # Удаляем старые записи (старше time_window)
    cutoff_time = current_time - time_window
    while request_times and request_times[0] < cutoff_time:
        request_times.popleft()
    
    # Проверяем лимит
    if len(request_times) >= max_requests:
        return False
    
    # Добавляем текущий запрос
    request_times.append(current_time)
    return True


def block_user(user_id: int, duration: float) -> None:
    """
    Блокирует пользователя на указанное время.
    
    Args:
        user_id: ID пользователя
        duration: Длительность блокировки в секундах
    """
    from loader import ADMIN_ID
    
    # Администратор не блокируется
    if user_id == ADMIN_ID:
        return
    
    unblock_time = time.time() + duration
    _user_blocks[user_id] = unblock_time
    logger.warning(f"User {user_id} blocked for {duration} seconds due to rate limit violations")


def rate_limit(max_requests: int = 10, time_window: float = 30.0, block_duration: float = 60.0):
    """
    Декоратор для ограничения частоты запросов от пользователей.
    
    Args:
        max_requests: Максимальное количество запросов за time_window
        time_window: Окно времени в секундах
        block_duration: Длительность блокировки в секундах при превышении лимита
    
    Usage:
        @rate_limit(max_requests=10, time_window=15.0)
        @bot.message_handler(commands=['start'])
        def handle_start(message):
            ...
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            from loader import ADMIN_ID
            
            # Получаем user_id из аргументов (обычно первый аргумент - message или call)
            user_id = None
            if args:
                message_or_call = args[0]
                # Для message: message.from_user.id
                # Для call: call.from_user.id
                if hasattr(message_or_call, 'from_user') and message_or_call.from_user:
                    user_id = message_or_call.from_user.id
                # Если это callback query, может быть call.from_user напрямую
                elif hasattr(message_or_call, 'from_user') and hasattr(message_or_call.from_user, 'id'):
                    user_id = message_or_call.from_user.id
            
            # Если не удалось получить user_id, пропускаем проверку
            if user_id is None:
                logger.warning(f"Could not extract user_id for rate limiting in {func.__name__}")
                return func(*args, **kwargs)
            
            # Администратор не ограничивается
            if user_id == ADMIN_ID:
                return func(*args, **kwargs)
            
            # Проверка блокировки
            current_time = time.time()
            if user_id in _user_blocks:
                if current_time < _user_blocks[user_id]:
                    remaining_time = int(_user_blocks[user_id] - current_time)
                    logger.warning(f"User {user_id} is blocked, {remaining_time} seconds remaining")
                    # Для callback query нужно ответить, иначе будет "loading"
                    if args and hasattr(args[0], 'id') and hasattr(args[0], 'data'):
                        try:
                            bot.answer_callback_query(args[0].id, text=f"Подождите {remaining_time} секунд", show_alert=False)
                        except Exception:
                            pass
                    # Не отправляем сообщение, просто игнорируем запрос
                    return None
                else:
                    # Блокировка истекла
                    del _user_blocks[user_id]
            
            # Проверка rate limit
            if not check_rate_limit(user_id, max_requests, time_window):
                # Превышен лимит - блокируем пользователя
                block_user(user_id, block_duration)
                
                # Получаем информацию о пользователе для логирования
                user_info = ""
                try:
                    # Пытаемся получить имя из message/call
                    if args and hasattr(args[0], 'from_user') and args[0].from_user:
                        first_name = getattr(args[0].from_user, 'first_name', None) or "Unknown"
                        username = getattr(args[0].from_user, 'username', None)
                        user_info = f" ({first_name}"
                        if username:
                            user_info += f", @{username}"
                        user_info += ")"
                    else:
                        # Если нет в message, пытаемся получить из базы данных
                        from database import get_user_status
                        user_data = get_user_status(user_id)
                        if user_data:
                            first_name = user_data.get('first_name', 'Unknown')
                            username = user_data.get('username')
                            user_info = f" ({first_name}"
                            if username:
                                user_info += f", @{username}"
                            user_info += ")"
                        else:
                            # Если нет в БД, пытаемся получить через Telegram API
                            try:
                                chat_member = bot.get_chat_member(user_id, user_id)
                                if chat_member and chat_member.user:
                                    first_name = chat_member.user.first_name or "Unknown"
                                    username = chat_member.user.username
                                    user_info = f" ({first_name}"
                                    if username:
                                        user_info += f", @{username}"
                                    user_info += ")"
                            except Exception as api_error:
                                logger.debug(f"Could not get user info via API for {user_id}: {api_error}")
                except Exception as e:
                    logger.debug(f"Error extracting user info for {user_id}: {e}")
                    # Продолжаем без информации о пользователе
                
                # Логируем для отладки (временно, для диагностики)
                if not user_info:
                    logger.debug(f"User info is empty for {user_id} in {func.__name__}, args[0] type: {type(args[0]) if args else 'no args'}")
                
                # Логируем для отладки
                request_count = len(_rate_limit_history.get(user_id, deque()))
                logger.warning(
                    f"Rate limit exceeded for user {user_id}{user_info} in {func.__name__}: "
                    f"{request_count} requests in {time_window}s (limit: {max_requests})"
                )
                
                # Для callback query нужно ответить, иначе будет "loading"
                if args and hasattr(args[0], 'id') and hasattr(args[0], 'data'):
                    try:
                        bot.answer_callback_query(args[0].id, text="Превышен лимит запросов", show_alert=False)
                    except Exception:
                        pass
                
                # Отправляем предупреждение пользователю
                try:
                    warning_text = (
                        f"⚠️ Вы превысили лимит запросов ({request_count}/{max_requests} за {int(time_window)} сек). "
                        f"Пожалуйста, подождите {int(block_duration)} секунд перед следующим запросом."
                    )
                    safe_send_message(bot, user_id, warning_text)
                except Exception as e:
                    logger.error(f"Failed to send rate limit warning to user {user_id}: {e}")
                
                # Уведомляем администратора
                try:
                    from loader import ADMIN_ID
                    if ADMIN_ID:
                        admin_notification = (
                            f"⚠️ Rate limit exceeded by user {user_id}{user_info}. "
                            f"{request_count} requests in {int(time_window)}s (limit: {max_requests}). "
                            f"Blocked for {int(block_duration)} seconds."
                        )
                        safe_send_message(bot, ADMIN_ID, admin_notification)
                except Exception as e:
                    logger.error(f"Failed to notify admin about rate limit: {e}")
                
                return None
            
            # Лимит не превышен - выполняем обработчик
            request_count = len(_rate_limit_history.get(user_id, deque()))
            logger.debug(f"Rate limit check passed for user {user_id} in {func.__name__}: {request_count}/{max_requests} requests")
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


def safe_send_message(bot: Any, chat_id: int, text: str, **kwargs: Any) -> Optional[Any]:
    """
    Безопасная отправка сообщения с автоматическими повторами.
    
    Args:
        bot: Экземпляр TeleBot
        chat_id: ID чата для отправки
        text: Текст сообщения
        **kwargs: Дополнительные параметры для send_message
    
    Returns:
        Сообщение или None при ошибке
    """
    try:
        return retry_telegram_api(
            bot.send_message,
            max_attempts=3,
            chat_id=chat_id,
            text=text,
            **kwargs
        )
    except Exception as e:
        logger.error(f"Failed to send message to {chat_id} after all retries: {e}")
        # Не выбрасываем исключение дальше - бот должен продолжать работать
        return None

