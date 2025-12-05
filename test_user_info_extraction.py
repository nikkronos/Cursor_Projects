"""
Простой тест для проверки логики извлечения информации о пользователе
Можно запустить локально без зависимостей от бота
"""

# Симуляция объектов Telegram
class MockUser:
    def __init__(self, user_id, first_name=None, username=None):
        self.id = user_id
        self.first_name = first_name
        self.username = username

class MockMessage:
    def __init__(self, user_id, first_name=None, username=None):
        self.from_user = MockUser(user_id, first_name, username) if user_id else None

def extract_user_info(args):
    """Симуляция логики извлечения информации о пользователе из utils.py"""
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
    except Exception:
        pass  # Если не удалось получить информацию, продолжаем без неё
    
    return user_info

def test_cases():
    """Тестовые случаи"""
    print("="*60)
    print("Тестирование извлечения информации о пользователе")
    print("="*60)
    
    # Тест 1: Сообщение с именем и username
    print("\nТест 1: Сообщение с именем и username")
    message1 = MockMessage(871902505, "Иван", "ivan_user")
    user_info1 = extract_user_info([message1])
    expected1 = " (Иван, @ivan_user)"
    print(f"  Вход: user_id=871902505, first_name='Иван', username='ivan_user'")
    print(f"  Ожидается: {expected1}")
    print(f"  Получено: {user_info1}")
    assert user_info1 == expected1, f"Ожидалось {expected1}, получено {user_info1}"
    print("  ✅ Тест пройден")
    
    # Тест 2: Сообщение только с именем
    print("\nТест 2: Сообщение только с именем")
    message2 = MockMessage(871902505, "Иван", None)
    user_info2 = extract_user_info([message2])
    expected2 = " (Иван)"
    print(f"  Вход: user_id=871902505, first_name='Иван', username=None")
    print(f"  Ожидается: {expected2}")
    print(f"  Получено: {user_info2}")
    assert user_info2 == expected2, f"Ожидалось {expected2}, получено {user_info2}"
    print("  ✅ Тест пройден")
    
    # Тест 3: Сообщение без имени и username
    print("\nТест 3: Сообщение без имени и username")
    message3 = MockMessage(871902505, None, None)
    user_info3 = extract_user_info([message3])
    expected3 = " (Unknown)"
    print(f"  Вход: user_id=871902505, first_name=None, username=None")
    print(f"  Ожидается: {expected3}")
    print(f"  Получено: {user_info3}")
    assert user_info3 == expected3, f"Ожидалось {expected3}, получено {user_info3}"
    print("  ✅ Тест пройден")
    
    # Тест 4: Сообщение только с username
    print("\nТест 4: Сообщение только с username")
    message4 = MockMessage(871902505, None, "ivan_user")
    user_info4 = extract_user_info([message4])
    expected4 = " (Unknown, @ivan_user)"
    print(f"  Вход: user_id=871902505, first_name=None, username='ivan_user'")
    print(f"  Ожидается: {expected4}")
    print(f"  Получено: {user_info4}")
    assert user_info4 == expected4, f"Ожидалось {expected4}, получено {user_info4}"
    print("  ✅ Тест пройден")
    
    # Тест 5: Пустой args
    print("\nТест 5: Пустой args")
    user_info5 = extract_user_info([])
    expected5 = ""
    print(f"  Вход: args=[]")
    print(f"  Ожидается: '{expected5}'")
    print(f"  Получено: '{user_info5}'")
    assert user_info5 == expected5, f"Ожидалось '{expected5}', получено '{user_info5}'"
    print("  ✅ Тест пройден")
    
    # Тест 6: Сообщение без from_user
    print("\nТест 6: Сообщение без from_user")
    class MockMessageNoUser:
        pass
    message6 = MockMessageNoUser()
    user_info6 = extract_user_info([message6])
    expected6 = ""
    print(f"  Вход: message без from_user")
    print(f"  Ожидается: '{expected6}'")
    print(f"  Получено: '{user_info6}'")
    assert user_info6 == expected6, f"Ожидалось '{expected6}', получено '{user_info6}'"
    print("  ✅ Тест пройден")
    
    print("\n" + "="*60)
    print("✅ Все тесты пройдены успешно!")
    print("="*60)
    return True

if __name__ == "__main__":
    try:
        test_cases()
    except AssertionError as e:
        print(f"\n❌ Ошибка в тесте: {e}")
        exit(1)
    except Exception as e:
        print(f"\n❌ Неожиданная ошибка: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

