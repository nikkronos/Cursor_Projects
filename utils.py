"""
Утилиты для работы с Telegram Bot API.
Содержит механизмы retry, rate limiting и безопасной отправки сообщений.
"""
import time
import re
from typing import Callable, Any, Optional, Dict, List
from functools import wraps
from loader import logger, ADMIN_ID


# ==================== Retry механизм ====================

def retry_telegram_api(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    *args: Any,
    **kwargs: Any
) -> Any:
    """
    Выполняет функцию с автоматическими повторами при временных ошибках.
    
    Args:
        func: Функция для выполнения
        max_attempts: Максимальное количество попыток (по умолчанию 3)
        base_delay: Базовая задержка для экспоненциальной задержки (по умолчанию 1.0 сек)
        *args: Позиционные аргументы для функции
        **kwargs: Именованные аргументы для функции
    
    Returns:
        Результат выполнения функции
    
    Raises:
        Исключение после исчерпания всех попыток
    """
    last_exception = None
    
    for attempt in range(1, max_attempts + 1):
        try:
            result = func(*args, **kwargs)
            if attempt > 1:
                logger.info(f"Retry успешен на попытке {attempt} для функции {func.__name__}")
            return result
        except Exception as e:
            last_exception = e
            error_message = str(e)
            
            # Проверка на rate limiting (429 ошибка)
            if "429" in error_message or "Too Many Requests" in error_message:
                retry_after = extract_retry_after(error_message)
                if retry_after:
                    logger.warning(f"Rate limit detected. Waiting {retry_after} seconds before retry.")
                    time.sleep(retry_after)
                    continue
            
            # Проверка на временные ошибки (ConnectionError, TimeoutError, и т.д.)
            if is_retryable_error(e):
                if attempt < max_attempts:
                    delay = base_delay * (2 ** (attempt - 1))
                    logger.warning(
                        f"Временная ошибка при вызове {func.__name__} (попытка {attempt}/{max_attempts}): {e}. "
                        f"Повтор через {delay} сек."
                    )
                    time.sleep(delay)
                else:
                    logger.error(f"Все попытки исчерпаны для {func.__name__}: {e}")
            else:
                # Некритичная ошибка - не повторяем
                logger.error(f"Некритичная ошибка в {func.__name__}: {e}")
                raise e
    
    # Если дошли сюда - все попытки исчерпаны
    logger.error(f"Все {max_attempts} попыток исчерпаны для {func.__name__}")
    raise last_exception


def is_retryable_error(error: Exception) -> bool:
    """
    Проверяет, является ли ошибка временной и требует ли она повторной попытки.
    
    Args:
        error: Исключение для проверки
    
    Returns:
        True если ошибка временная и требует retry, False иначе
    """
    retryable_errors = (
        ConnectionError,
        TimeoutError,
        OSError,
    )
    
    if isinstance(error, retryable_errors):
        return True
    
    error_message = str(error).lower()
    retryable_keywords = [
        "connection",
        "timeout",
        "network",
        "temporary",
        "unavailable",
        "service",
        "retry",
    ]
    
    return any(keyword in error_message for keyword in retryable_keywords)


def extract_retry_after(error_message: str) -> Optional[float]:
    """
    Извлекает значение retry_after из сообщения об ошибке rate limiting.
    
    Args:
        error_message: Сообщение об ошибке
    
    Returns:
        Количество секунд для ожидания или None
    """
    # Ищем паттерны типа "retry_after: 5" или "retry after 5"
    patterns = [
        r"retry[_\s]after[:\s]+(\d+)",
        r"429.*?(\d+)",
    ]
    
    for pattern in patterns:
        match = re.search(pattern, error_message, re.IGNORECASE)
        if match:
            try:
                return float(match.group(1))
            except ValueError:
                pass
    
    return None


# ==================== Safe send message ====================

def safe_send_message(
    bot: Any,
    chat_id: int,
    text: str,
    parse_mode: Optional[str] = None,
    **kwargs: Any
) -> Optional[Any]:
    """
    Безопасная отправка сообщения с автоматическими повторами при ошибках.
    
    Args:
        bot: Экземпляр бота
        chat_id: ID чата для отправки
        text: Текст сообщения
        parse_mode: Режим парсинга (Markdown, HTML и т.д.)
        **kwargs: Дополнительные параметры для send_message
    
    Returns:
        Результат отправки сообщения или None при ошибке
    """
    def send_func():
        return bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode, **kwargs)
    
    try:
        return retry_telegram_api(send_func, max_attempts=3)
    except Exception as e:
        logger.error(f"Не удалось отправить сообщение в чат {chat_id}: {e}")
        return None


def safe_send_photo(
    bot: Any,
    chat_id: int,
    photo: str,
    caption: Optional[str] = None,
    **kwargs: Any
) -> Optional[Any]:
    """
    Безопасная отправка фото с автоматическими повторами при ошибках.
    
    Args:
        bot: Экземпляр бота
        chat_id: ID чата для отправки
        photo: file_id или URL фото
        caption: Подпись к фото
        **kwargs: Дополнительные параметры для send_photo
    
    Returns:
        Результат отправки фото или None при ошибке
    """
    def send_func():
        return bot.send_photo(chat_id=chat_id, photo=photo, caption=caption, **kwargs)
    
    try:
        return retry_telegram_api(send_func, max_attempts=3)
    except Exception as e:
        logger.error(f"Не удалось отправить фото в чат {chat_id}: {e}")
        return None


# ==================== Rate Limiting ====================

# Хранилище истории запросов: {user_id: [timestamp1, timestamp2, ...]}
_rate_limit_history: Dict[int, List[float]] = {}

# Хранилище блокировок: {user_id: unblock_timestamp}
_rate_limit_blocks: Dict[int, float] = {}


def check_rate_limit(
    user_id: int,
    max_requests: int,
    time_window: float
) -> bool:
    """
    Проверяет, не превышен ли лимит запросов для пользователя.
    
    Args:
        user_id: ID пользователя
        max_requests: Максимальное количество запросов
        time_window: Окно времени в секундах
    
    Returns:
        True если лимит не превышен, False если превышен
    """
    # Администратор не ограничивается
    if user_id == ADMIN_ID:
        return True
    
    current_time = time.time()
    
    # Проверка блокировки
    if user_id in _rate_limit_blocks:
        unblock_time = _rate_limit_blocks[user_id]
        if current_time < unblock_time:
            return False
        else:
            # Блокировка истекла - удаляем
            del _rate_limit_blocks[user_id]
    
    # Инициализация истории для пользователя
    if user_id not in _rate_limit_history:
        _rate_limit_history[user_id] = []
    
    # Очистка старых запросов (старше time_window)
    cutoff_time = current_time - time_window
    _rate_limit_history[user_id] = [
        timestamp for timestamp in _rate_limit_history[user_id]
        if timestamp > cutoff_time
    ]
    
    # Проверка лимита
    request_count = len(_rate_limit_history[user_id])
    if request_count >= max_requests:
        logger.warning(f"Rate limit exceeded by user {user_id}. {request_count} requests in {time_window}s (limit: {max_requests})")
        return False
    
    # Добавляем текущий запрос
    _rate_limit_history[user_id].append(current_time)
    return True


def rate_limit(
    max_requests: int = 20,
    time_window: float = 30.0,
    block_duration: float = 30.0
):
    """
    Декоратор для применения rate limiting к обработчикам.
    
    Args:
        max_requests: Максимальное количество запросов
        time_window: Окно времени в секундах
        block_duration: Длительность блокировки в секундах при превышении лимита
    
    Returns:
        Декорированная функция
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Получаем user_id из сообщения
            message = None
            if args and hasattr(args[0], 'from_user'):
                message = args[0]
            elif args and hasattr(args[0], 'message') and hasattr(args[0].message, 'from_user'):
                message = args[0].message
            
            if not message:
                # Если не можем определить пользователя - пропускаем
                return func(*args, **kwargs)
            
            user_id = message.from_user.id
            
            # Проверка rate limit
            if not check_rate_limit(user_id, max_requests, time_window):
                # Превышен лимит - блокируем пользователя
                current_time = time.time()
                unblock_time = current_time + block_duration
                _rate_limit_blocks[user_id] = unblock_time
                
                logger.warning(
                    f"Rate limit exceeded by user {user_id} ({message.from_user.first_name}, "
                    f"@{message.from_user.username}). {max_requests} requests in {time_window}s "
                    f"(limit: {max_requests}). Blocked for {block_duration} seconds."
                )
                
                # Отправляем предупреждение пользователю
                try:
                    from loader import bot
                    safe_send_message(
                        bot,
                        user_id,
                        f"⚠️ Вы превысили лимит запросов ({max_requests} запросов за {time_window} секунд). "
                        f"Пожалуйста, подождите {int(block_duration)} секунд."
                    )
                except Exception as e:
                    logger.error(f"Не удалось отправить предупреждение о rate limit пользователю {user_id}: {e}")
                
                # Уведомляем администратора
                try:
                    from loader import bot
                    safe_send_message(
                        bot,
                        ADMIN_ID,
                        f"⚠️ Rate limit exceeded by user {user_id} ({message.from_user.first_name}, "
                        f"@{message.from_user.username}). {max_requests} requests in {time_window}s "
                        f"(limit: {max_requests}). Blocked for {block_duration} seconds."
                    )
                except Exception as e:
                    logger.error(f"Не удалось отправить уведомление администратору о rate limit: {e}")
                
                # Не выполняем обработчик
                return None
            
            # Лимит не превышен - выполняем обработчик
            return func(*args, **kwargs)
        
        return wrapper
    return decorator


# ==================== Markdown escaping ====================

def escape_markdown(text: str) -> str:
    """
    Экранирует специальные символы Markdown в тексте.
    
    Args:
        text: Текст для экранирования
    
    Returns:
        Текст с экранированными символами Markdown
    """
    if not text:
        return text
    
    # Символы, которые нужно экранировать в Markdown
    escape_chars = ['*', '_', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    result = text
    for char in escape_chars:
        result = result.replace(char, f'\\{char}')
    
    return result
