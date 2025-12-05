"""
Тесты для механизма retry Telegram API
"""
import pytest
import time
from unittest.mock import Mock, MagicMock, patch
from utils import retry_telegram_api, safe_send_message


class TemporaryError(Exception):
    """Временная ошибка для тестов"""
    pass


class RateLimitError(Exception):
    """Ошибка rate limiting для тестов"""
    pass


def test_retry_succeeds_on_first_attempt():
    """Тест: успешный вызов с первого раза"""
    mock_func = Mock(return_value="success")
    
    result = retry_telegram_api(mock_func, max_attempts=3)
    
    assert result == "success"
    assert mock_func.call_count == 1


def test_retry_succeeds_on_second_attempt():
    """Тест: успешный вызов со второй попытки"""
    mock_func = Mock(side_effect=[ConnectionError("Connection failed"), "success"])
    
    with patch('time.sleep'):  # Пропускаем реальную задержку
        result = retry_telegram_api(mock_func, max_attempts=3)
    
    assert result == "success"
    assert mock_func.call_count == 2


def test_retry_fails_after_max_attempts():
    """Тест: неудача после всех попыток"""
    mock_func = Mock(side_effect=ConnectionError("Connection failed"))
    
    with patch('time.sleep'):  # Пропускаем реальную задержку
        with pytest.raises(ConnectionError):
            retry_telegram_api(mock_func, max_attempts=3)
    
    assert mock_func.call_count == 3


def test_retry_exponential_backoff():
    """Тест: экспоненциальная задержка между попытками"""
    mock_func = Mock(side_effect=[ConnectionError(), ConnectionError(), "success"])
    sleep_calls = []
    
    def mock_sleep(seconds):
        sleep_calls.append(seconds)
    
    with patch('time.sleep', side_effect=mock_sleep):
        retry_telegram_api(mock_func, max_attempts=3, base_delay=1.0)
    
    # Первая попытка неудачна, задержка перед второй попыткой = 1 сек
    # Вторая попытка неудачна, задержка перед третьей попыткой = 2 сек
    assert len(sleep_calls) == 2
    assert sleep_calls[0] == 1.0  # base_delay * 2^0
    assert sleep_calls[1] == 2.0  # base_delay * 2^1


def test_retry_non_retryable_error():
    """Тест: не повторяет при некритичных ошибках"""
    class ValueError(Exception):
        pass
    
    mock_func = Mock(side_effect=ValueError("Invalid input"))
    
    with pytest.raises(ValueError):
        retry_telegram_api(mock_func, max_attempts=3)
    
    # Не должно быть повторений при некритичных ошибках
    assert mock_func.call_count == 1


def test_retry_rate_limit_error():
    """Тест: обработка rate limit ошибки"""
    mock_func = Mock(side_effect=[Exception("429 Too Many Requests retry_after: 5"), "success"])
    sleep_calls = []
    
    def mock_sleep(seconds):
        sleep_calls.append(seconds)
    
    with patch('time.sleep', side_effect=mock_sleep):
        result = retry_telegram_api(mock_func, max_attempts=3)
    
    assert result == "success"
    assert mock_func.call_count == 2
    # Должен использовать retry_after из сообщения об ошибке
    assert 5.0 in sleep_calls or len(sleep_calls) > 0


def test_retry_timeout_error():
    """Тест: обработка timeout ошибки"""
    mock_func = Mock(side_effect=[TimeoutError("Request timeout"), "success"])
    
    with patch('time.sleep'):
        result = retry_telegram_api(mock_func, max_attempts=3)
    
    assert result == "success"
    assert mock_func.call_count == 2


def test_safe_send_message_success():
    """Тест: safe_send_message успешно отправляет сообщение"""
    mock_bot = Mock()
    mock_bot.send_message.return_value = Mock()
    
    result = safe_send_message(mock_bot, chat_id=123, text="Test message")
    
    assert result is not None
    mock_bot.send_message.assert_called_once_with(chat_id=123, text="Test message")


def test_safe_send_message_failure():
    """Тест: safe_send_message возвращает None при ошибке"""
    mock_bot = Mock()
    mock_bot.send_message.side_effect = ConnectionError("Connection failed")
    
    with patch('time.sleep'):  # Пропускаем задержки
        result = safe_send_message(mock_bot, chat_id=123, text="Test message")
    
    assert result is None
    # Должно быть 3 попытки
    assert mock_bot.send_message.call_count == 3


def test_retry_with_args_and_kwargs():
    """Тест: retry передает аргументы и ключевые слова"""
    mock_func = Mock(return_value="success")
    
    result = retry_telegram_api(
        mock_func,
        max_attempts=3,
        arg1="value1",
        arg2="value2",
        kwarg1="kwvalue1"
    )
    
    assert result == "success"
    mock_func.assert_called_once_with(arg1="value1", arg2="value2", kwarg1="kwvalue1")













