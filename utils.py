"""
Утилиты для работы с Telegram Bot API
Включает механизм retry для обработки временных ошибок и rate limiting
"""
import time
from typing import Callable, Any, Type
from loader import logger


def retry_telegram_api(
    func: Callable,
    max_attempts: int = 3,
    base_delay: float = 1.0,
    *args,
    **kwargs
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


def safe_send_message(bot, chat_id, text, **kwargs):
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

