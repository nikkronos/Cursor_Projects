"""
Модуль валидации входных данных от пользователей
"""
from typing import Union, Optional
from loader import logger


class ValidationError(Exception):
    """Исключение для ошибок валидации"""
    pass


def validate_user_id(user_id_input: Union[str, int]) -> int:
    """
    Валидация ID пользователя Telegram.
    
    Args:
        user_id_input: Входное значение (str или int)
    
    Returns:
        int: Валидированный ID пользователя
    
    Raises:
        ValidationError: Если ID некорректен
    """
    try:
        # Преобразуем в строку, затем в int для обработки и строк, и чисел
        user_id_str = str(user_id_input).strip()
        
        # Проверяем, что строка не пустая
        if not user_id_str:
            raise ValidationError("ID пользователя не может быть пустым")
        
        # Проверяем, что это число
        try:
            user_id = int(user_id_str)
        except ValueError:
            raise ValidationError(f"ID пользователя должен быть числом, получено: {user_id_str}")
        
        # Telegram user IDs обычно положительные числа от 1 до 2^63-1
        # Проверяем разумные границы
        if user_id <= 0:
            raise ValidationError(f"ID пользователя должен быть положительным числом, получено: {user_id}")
        
        # Максимальное значение для Telegram ID (2^63 - 1 = 9223372036854775807)
        MAX_USER_ID = 9223372036854775807
        if user_id > MAX_USER_ID:
            raise ValidationError(f"ID пользователя слишком большой: {user_id}")
        
        return user_id
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating user_id '{user_id_input}': {e}")
        raise ValidationError(f"Ошибка при валидации ID пользователя: {e}")


def validate_days(days_input: Union[str, int], min_days: int = -365, max_days: int = 365) -> int:
    """
    Валидация количества дней для подписки.
    
    Args:
        days_input: Входное значение (str или int)
        min_days: Минимальное количество дней (по умолчанию -365)
        max_days: Максимальное количество дней (по умолчанию 365)
    
    Returns:
        int: Валидированное количество дней
    
    Raises:
        ValidationError: Если значение некорректно
    """
    try:
        days_str = str(days_input).strip()
        
        if not days_str:
            raise ValidationError("Количество дней не может быть пустым")
        
        try:
            days = int(days_str)
        except ValueError:
            raise ValidationError(f"Количество дней должно быть числом, получено: {days_str}")
        
        if days < min_days:
            raise ValidationError(
                f"Количество дней не может быть меньше {min_days}, получено: {days}"
            )
        
        if days > max_days:
            raise ValidationError(
                f"Количество дней не может быть больше {max_days}, получено: {days}"
            )
        
        return days
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating days '{days_input}': {e}")
        raise ValidationError(f"Ошибка при валидации количества дней: {e}")


def validate_text(text_input: Optional[str], max_length: int = 4000, field_name: str = "текст") -> str:
    """
    Валидация текстового поля.
    
    Args:
        text_input: Входной текст
        max_length: Максимальная длина текста (по умолчанию 4000 - лимит Telegram)
        field_name: Название поля для сообщений об ошибках
    
    Returns:
        str: Валидированный и санитизированный текст
    
    Raises:
        ValidationError: Если текст некорректен
    """
    try:
        if text_input is None:
            raise ValidationError(f"{field_name} не может быть пустым")
        
        text = str(text_input).strip()
        
        if not text:
            raise ValidationError(f"{field_name} не может быть пустым")
        
        if len(text) > max_length:
            raise ValidationError(
                f"{field_name} слишком длинный (максимум {max_length} символов, "
                f"получено {len(text)})"
            )
        
        # Удаляем лишние пробелы (но сохраняем один пробел между словами)
        text = ' '.join(text.split())
        
        return text
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating text: {e}")
        raise ValidationError(f"Ошибка при валидации {field_name}: {e}")


def validate_positive_integer(value_input: Union[str, int], field_name: str = "число", min_value: int = 1, max_value: Optional[int] = None) -> int:
    """
    Валидация положительного целого числа.
    
    Args:
        value_input: Входное значение
        field_name: Название поля для сообщений
        min_value: Минимальное значение (по умолчанию 1)
        max_value: Максимальное значение (None = без ограничения)
    
    Returns:
        int: Валидированное число
    
    Raises:
        ValidationError: Если значение некорректно
    """
    try:
        value_str = str(value_input).strip()
        
        if not value_str:
            raise ValidationError(f"{field_name} не может быть пустым")
        
        try:
            value = int(value_str)
        except ValueError:
            raise ValidationError(f"{field_name} должно быть числом, получено: {value_str}")
        
        if value < min_value:
            raise ValidationError(f"{field_name} должно быть не меньше {min_value}, получено: {value}")
        
        if max_value is not None and value > max_value:
            raise ValidationError(f"{field_name} должно быть не больше {max_value}, получено: {value}")
        
        return value
        
    except ValidationError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating {field_name} '{value_input}': {e}")
        raise ValidationError(f"Ошибка при валидации {field_name}: {e}")

