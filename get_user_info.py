"""
Скрипт для получения информации о пользователе
Проверяет базу данных и Telegram API
Использование: python get_user_info.py <telegram_id>
"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from database import get_db_connection, get_user_status
from loader import bot

def get_user_info(telegram_id: int):
    """Получить информацию о пользователе из базы данных и Telegram API"""
    print(f"\n🔍 Поиск информации о пользователе {telegram_id}...\n")
    
    # Проверяем базу данных
    try:
        user_data = get_user_status(telegram_id)
        if user_data:
            print("✅ Пользователь найден в базе данных:")
            print(f"  ID: {user_data['telegram_id']}")
            print(f"  Имя: {user_data['first_name']}")
            print(f"  Username: @{user_data['username']}" if user_data['username'] else "  Username: нет")
            print(f"  Статус подписки: {user_data['subscription_status']}")
            print(f"  Начало подписки: {user_data['subscription_start_date'] or 'N/A'}")
            print(f"  Конец подписки: {user_data['subscription_end_date'] or 'N/A'}")
            print(f"  Статус оплаты: {user_data['payment_status']}")
        else:
            print("❌ Пользователь не найден в базе данных")
            print("   (возможно, он еще не использовал /start)")
    except Exception as e:
        print(f"⚠️ Ошибка при проверке базы данных: {e}")
    
    # Пытаемся получить информацию через Telegram API
    print("\n📡 Попытка получить информацию через Telegram API...")
    try:
        chat_member = bot.get_chat_member(telegram_id, telegram_id)
        if chat_member:
            user = chat_member.user
            print(f"✅ Информация из Telegram API:")
            print(f"  ID: {user.id}")
            print(f"  Имя: {user.first_name}")
            if user.last_name:
                print(f"  Фамилия: {user.last_name}")
            if user.username:
                print(f"  Username: @{user.username}")
            print(f"  Язык: {user.language_code or 'N/A'}")
    except Exception as e:
        error_str = str(e)
        if "user not found" in error_str.lower() or "chat not found" in error_str.lower():
            print("❌ Пользователь не найден в Telegram")
            print("   (возможно, он заблокировал бота или удалил аккаунт)")
        elif "forbidden" in error_str.lower():
            print("⚠️ Нет доступа к информации о пользователе")
            print("   (пользователь заблокировал бота)")
        else:
            print(f"⚠️ Ошибка при запросе к Telegram API: {e}")
    
    print("\n" + "="*50)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python get_user_info.py <telegram_id>")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
        get_user_info(user_id)
    except ValueError:
        print("Ошибка: telegram_id должен быть числом")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n\nПрервано пользователем")
        sys.exit(0)


