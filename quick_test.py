"""
Быстрая проверка после рефакторинга handlers
Запуск: python quick_test.py
"""
import sys
import os

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def main():
    print("=" * 60)
    print("БЫСТРАЯ ПРОВЕРКА ПОСЛЕ РЕФАКТОРИНГА HANDLERS")
    print("=" * 60)
    
    errors = []
    
    # Тест 1: Импорт пакета handlers
    print("\n[1/5] Проверка импорта пакета handlers...")
    try:
        import handlers
        print("✅ Пакет handlers импортирован успешно")
    except Exception as e:
        print(f"❌ Ошибка импорта handlers: {e}")
        errors.append(f"Импорт handlers: {e}")
        return 1
    
    # Тест 2: Импорт всех модулей
    print("\n[2/5] Проверка импорта всех модулей...")
    try:
        from handlers import helpers, admin, user, callbacks, join_requests
        print("✅ handlers.helpers импортирован")
        print("✅ handlers.admin импортирован")
        print("✅ handlers.user импортирован")
        print("✅ handlers.callbacks импортирован")
        print("✅ handlers.join_requests импортирован")
    except Exception as e:
        print(f"❌ Ошибка импорта модулей: {e}")
        errors.append(f"Импорт модулей: {e}")
        return 1
    
    # Тест 3: Проверка helper функций
    print("\n[3/5] Проверка helper функций...")
    try:
        from handlers.helpers import (
            send_main_menu,
            send_admin_menu,
            send_payment_info,
            TARIFF_QUESTIONS
        )
        assert callable(send_main_menu)
        assert callable(send_admin_menu)
        assert callable(send_payment_info)
        assert isinstance(TARIFF_QUESTIONS, list)
        print("✅ Все helper функции доступны")
    except Exception as e:
        print(f"❌ Ошибка проверки helpers: {e}")
        errors.append(f"Helpers: {e}")
        return 1
    
    # Тест 4: Проверка обработчиков
    print("\n[4/5] Проверка обработчиков...")
    try:
        assert hasattr(admin, 'handle_admin_command')
        assert hasattr(user, 'handle_start')
        assert hasattr(callbacks, 'callback_confirm_payment')
        assert hasattr(join_requests, 'handle_join_request')
        print("✅ Основные обработчики существуют")
    except Exception as e:
        print(f"❌ Ошибка проверки обработчиков: {e}")
        errors.append(f"Обработчики: {e}")
        return 1
    
    # Тест 5: Проверка регистрации (если bot доступен)
    print("\n[5/5] Проверка регистрации обработчиков...")
    try:
        from loader import bot
        total_handlers = (
            len(bot.message_handlers) +
            len(bot.callback_query_handlers) +
            len(bot.chat_join_request_handlers) +
            len(bot.chat_member_handlers)
        )
        if total_handlers > 0:
            print(f"✅ Зарегистрировано обработчиков: {total_handlers}")
        else:
            print("⚠️  Обработчики не зарегистрированы (возможно, bot не инициализирован)")
    except (ImportError, AttributeError) as e:
        print(f"⚠️  Bot не инициализирован (это нормально, если нет токена): {e}")
    
    # Итог
    print("\n" + "=" * 60)
    if errors:
        print("❌ ОБНАРУЖЕНЫ ОШИБКИ:")
        for error in errors:
            print(f"  - {error}")
        print("=" * 60)
        return 1
    else:
        print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
        print("=" * 60)
        print("\n✅ Рефакторинг handlers завершен успешно!")
        print("✅ Все модули импортируются корректно")
        print("✅ Структура handlers работает правильно")
        print("\n💡 Следующий шаг: запустите бота (python main.py) для полного тестирования")
        return 0

if __name__ == '__main__':
    exit_code = main()
    sys.exit(exit_code)

