"""
Ручное тестирование модулей без pytest
Можно запустить: python test_manual.py
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Тест 1: Проверка импортов всех модулей"""
    print("=" * 60)
    print("ТЕСТ 1: Проверка импортов модулей")
    print("=" * 60)
    
    modules = ['validators', 'utils', 'database', 'services', 'config', 'loader']
    failed = []
    
    for module_name in modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name} - успешно импортирован")
        except Exception as e:
            print(f"✗ {module_name} - ОШИБКА: {e}")
            failed.append(module_name)
    
    if failed:
        print(f"\n❌ Не удалось импортировать: {', '.join(failed)}")
        return False
    else:
        print("\n✅ Все модули успешно импортированы!")
        return True


def test_validators():
    """Тест 2: Проверка функций валидации"""
    print("\n" + "=" * 60)
    print("ТЕСТ 2: Проверка функций валидации")
    print("=" * 60)
    
    try:
        from validators import validate_user_id, validate_days, validate_text, ValidationError
        
        # Тест validate_user_id
        print("\n--- Тест validate_user_id ---")
        assert validate_user_id("123456789") == 123456789, "Должен принимать корректный ID"
        assert validate_user_id(987654321) == 987654321, "Должен принимать число"
        print("✓ Корректные ID принимаются")
        
        try:
            validate_user_id(-1)
            print("✗ Отрицательный ID не должен приниматься")
            return False
        except ValidationError:
            print("✓ Отрицательные ID отклоняются")
        
        try:
            validate_user_id("abc")
            print("✗ Нечисловой ID не должен приниматься")
            return False
        except ValidationError:
            print("✓ Нечисловые значения отклоняются")
        
        # Тест validate_days
        print("\n--- Тест validate_days ---")
        assert validate_days("30") == 30, "Должен принимать корректное количество дней"
        assert validate_days(-30) == -30, "Должен принимать отрицательные дни в диапазоне"
        print("✓ Корректные значения дней принимаются")
        
        try:
            validate_days("500")  # Больше 365
            print("✗ Значения вне диапазона не должны приниматься")
            return False
        except ValidationError:
            print("✓ Значения вне диапазона отклоняются")
        
        # Тест validate_text
        print("\n--- Тест validate_text ---")
        result = validate_text("  Hello   World  ")
        assert result == "Hello World", "Должен удалять лишние пробелы"
        print("✓ Текст санитизируется (удаление лишних пробелов)")
        
        try:
            validate_text("a" * 5000, max_length=4000)
            print("✗ Слишком длинный текст не должен приниматься")
            return False
        except ValidationError:
            print("✓ Слишком длинный текст отклоняется")
        
        print("\n✅ Все функции валидации работают корректно!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании валидаторов: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_utils():
    """Тест 3: Проверка утилит"""
    print("\n" + "=" * 60)
    print("ТЕСТ 3: Проверка утилит (retry механизм)")
    print("=" * 60)
    
    try:
        from utils import retry_telegram_api
        import time
        
        # Тест успешного вызова
        print("\n--- Тест успешного вызова ---")
        def success_func():
            return "success"
        
        result = retry_telegram_api(success_func, max_attempts=3)
        assert result == "success", "Должен возвращать результат успешного вызова"
        print("✓ Успешный вызов работает корректно")
        
        # Тест retry при временной ошибке
        print("\n--- Тест retry при ошибке ---")
        call_count = [0]
        
        def failing_then_success():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ConnectionError("Temporary error")
            return "success"
        
        # Мокаем time.sleep чтобы не ждать
        original_sleep = time.sleep
        time.sleep = lambda x: None
        
        try:
            result = retry_telegram_api(failing_then_success, max_attempts=3)
            assert result == "success", "Должен успешно выполнить после retry"
            assert call_count[0] == 2, f"Должно быть 2 попытки, было {call_count[0]}"
            print("✓ Retry механизм работает (повтор при ошибке)")
        finally:
            time.sleep = original_sleep
        
        print("\n✅ Все утилиты работают корректно!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при тестировании утилит: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_database_structure():
    """Тест 4: Проверка структуры базы данных"""
    print("\n" + "=" * 60)
    print("ТЕСТ 4: Проверка структуры БД")
    print("=" * 60)
    
    try:
        from database import DB_FILE, get_db_connection, init_db, migrate_add_indexes
        
        print(f"\n--- Проверка файла БД: {DB_FILE} ---")
        # Проверяем, что функция get_db_connection существует
        assert callable(get_db_connection), "get_db_connection должна быть функцией"
        print("✓ Функция get_db_connection существует")
        
        assert callable(init_db), "init_db должна быть функцией"
        print("✓ Функция init_db существует")
        
        assert callable(migrate_add_indexes), "migrate_add_indexes должна быть функцией"
        print("✓ Функция migrate_add_indexes существует")
        
        print("\n✅ Структура БД корректна!")
        return True
        
    except Exception as e:
        print(f"\n❌ Ошибка при проверке БД: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Запуск всех тестов"""
    print("\n" + "=" * 60)
    print("РУЧНОЕ ТЕСТИРОВАНИЕ МОДУЛЕЙ")
    print("=" * 60)
    
    results = []
    
    # Запускаем тесты
    results.append(("Импорты", test_imports()))
    results.append(("Валидаторы", test_validators()))
    results.append(("Утилиты", test_utils()))
    results.append(("База данных", test_database_structure()))
    
    # Итоговый отчет
    print("\n" + "=" * 60)
    print("ИТОГОВЫЙ ОТЧЕТ")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✅ ПРОЙДЕН" if result else "❌ ПРОВАЛЕН"
        print(f"{test_name}: {status}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    print(f"\nВсего тестов: {total}")
    print(f"Пройдено: {passed}")
    print(f"Провалено: {total - passed}")
    
    if passed == total:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
        return 0
    else:
        print("\n⚠️  НЕКОТОРЫЕ ТЕСТЫ ПРОВАЛЕНЫ!")
        return 1


if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

