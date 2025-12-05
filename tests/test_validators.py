"""
Тесты для модуля валидации входных данных
"""
import pytest
from validators import (
    validate_user_id, 
    validate_days, 
    validate_text, 
    validate_positive_integer,
    ValidationError
)


class TestValidateUserID:
    """Тесты для validate_user_id"""
    
    def test_valid_user_id_string(self):
        """Тест: корректный ID как строка"""
        result = validate_user_id("123456789")
        assert result == 123456789
    
    def test_valid_user_id_int(self):
        """Тест: корректный ID как число"""
        result = validate_user_id(123456789)
        assert result == 123456789
    
    def test_negative_user_id(self):
        """Тест: отрицательный ID отклоняется"""
        with pytest.raises(ValidationError, match="положительным"):
            validate_user_id(-123)
    
    def test_zero_user_id(self):
        """Тест: ноль отклоняется"""
        with pytest.raises(ValidationError, match="положительным"):
            validate_user_id(0)
    
    def test_non_numeric_user_id(self):
        """Тест: нечисловое значение отклоняется"""
        with pytest.raises(ValidationError, match="числом"):
            validate_user_id("abc")
        with pytest.raises(ValidationError, match="числом"):
            validate_user_id("123abc")
    
    def test_empty_user_id(self):
        """Тест: пустое значение отклоняется"""
        with pytest.raises(ValidationError, match="пустым"):
            validate_user_id("")
        with pytest.raises(ValidationError, match="пустым"):
            validate_user_id("   ")
    
    def test_too_large_user_id(self):
        """Тест: слишком большой ID отклоняется"""
        too_large = 9223372036854775808  # Больше MAX_USER_ID
        with pytest.raises(ValidationError, match="слишком большой"):
            validate_user_id(too_large)
    
    def test_valid_telegram_user_id(self):
        """Тест: валидный Telegram user ID"""
        # Типичный Telegram user ID
        result = validate_user_id("987654321")
        assert result == 987654321


class TestValidateDays:
    """Тесты для validate_days"""
    
    def test_valid_days_string(self):
        """Тест: корректное количество дней как строка"""
        result = validate_days("30")
        assert result == 30
    
    def test_valid_days_int(self):
        """Тест: корректное количество дней как число"""
        result = validate_days(30)
        assert result == 30
    
    def test_valid_negative_days(self):
        """Тест: отрицательное количество дней в пределах диапазона"""
        result = validate_days("-30")
        assert result == -30
    
    def test_days_below_minimum(self):
        """Тест: значение ниже минимума отклоняется"""
        with pytest.raises(ValidationError, match="меньше"):
            validate_days("-400")
    
    def test_days_above_maximum(self):
        """Тест: значение выше максимума отклоняется"""
        with pytest.raises(ValidationError, match="больше"):
            validate_days("400")
    
    def test_non_numeric_days(self):
        """Тест: нечисловое значение отклоняется"""
        with pytest.raises(ValidationError, match="числом"):
            validate_days("abc")
    
    def test_empty_days(self):
        """Тест: пустое значение отклоняется"""
        with pytest.raises(ValidationError, match="пустым"):
            validate_days("")
    
    def test_custom_range(self):
        """Тест: пользовательский диапазон"""
        result = validate_days("10", min_days=-10, max_days=10)
        assert result == 10
        
        with pytest.raises(ValidationError):
            validate_days("20", min_days=-10, max_days=10)


class TestValidateText:
    """Тесты для validate_text"""
    
    def test_valid_text(self):
        """Тест: корректный текст"""
        result = validate_text("Hello, world!")
        assert result == "Hello, world!"
    
    def test_text_with_extra_spaces(self):
        """Тест: текст с лишними пробелами санитизируется"""
        result = validate_text("  Hello    world  ")
        assert result == "Hello world"
    
    def test_text_too_long(self):
        """Тест: слишком длинный текст отклоняется"""
        long_text = "a" * 5000
        with pytest.raises(ValidationError, match="слишком длинный"):
            validate_text(long_text, max_length=4000)
    
    def test_empty_text(self):
        """Тест: пустой текст отклоняется"""
        with pytest.raises(ValidationError, match="пустым"):
            validate_text("")
        with pytest.raises(ValidationError, match="пустым"):
            validate_text("   ")
    
    def test_none_text(self):
        """Тест: None отклоняется"""
        with pytest.raises(ValidationError, match="пустым"):
            validate_text(None)
    
    def test_text_with_newlines(self):
        """Тест: текст с переносами строк обрабатывается"""
        text = "Line 1\nLine 2\nLine 3"
        result = validate_text(text)
        # Переносы строк сохраняются, но лишние пробелы удаляются
        assert "Line 1" in result
    
    def test_custom_field_name(self):
        """Тест: пользовательское имя поля в сообщениях об ошибках"""
        with pytest.raises(ValidationError, match="сообщение"):
            validate_text("", field_name="сообщение")


class TestValidatePositiveInteger:
    """Тесты для validate_positive_integer"""
    
    def test_valid_positive_integer(self):
        """Тест: корректное положительное число"""
        result = validate_positive_integer("42")
        assert result == 42
    
    def test_zero_rejected(self):
        """Тест: ноль отклоняется (по умолчанию минимум 1)"""
        with pytest.raises(ValidationError, match="не меньше"):
            validate_positive_integer("0")
    
    def test_negative_rejected(self):
        """Тест: отрицательное число отклоняется"""
        with pytest.raises(ValidationError, match="не меньше"):
            validate_positive_integer("-10")
    
    def test_custom_min_value(self):
        """Тест: пользовательское минимальное значение"""
        result = validate_positive_integer("5", min_value=5)
        assert result == 5
        
        with pytest.raises(ValidationError):
            validate_positive_integer("3", min_value=5)
    
    def test_custom_max_value(self):
        """Тест: пользовательское максимальное значение"""
        result = validate_positive_integer("10", max_value=20)
        assert result == 10
        
        with pytest.raises(ValidationError, match="не больше"):
            validate_positive_integer("25", max_value=20)
    
    def test_non_numeric_rejected(self):
        """Тест: нечисловое значение отклоняется"""
        with pytest.raises(ValidationError, match="числом"):
            validate_positive_integer("abc")











