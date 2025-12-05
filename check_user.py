"""
Скрипт для проверки информации о пользователе в базе данных
Использование: python check_user.py <telegram_id>
"""
import sys
from database import get_db_connection

def check_user(telegram_id: int):
    """Проверить информацию о пользователе"""
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT telegram_id, first_name, username, subscription_status,
                       subscription_start_date, subscription_end_date, payment_status
                FROM users
                WHERE telegram_id = ?
            """, (telegram_id,))
            user = cursor.fetchone()
            
            if user:
                print(f"\n✅ Пользователь найден в базе данных:")
                print(f"ID: {user['telegram_id']}")
                print(f"Имя: {user['first_name']}")
                print(f"Username: @{user['username']}" if user['username'] else "Username: нет")
                print(f"Статус подписки: {user['subscription_status']}")
                print(f"Начало подписки: {user['subscription_start_date'] or 'N/A'}")
                print(f"Конец подписки: {user['subscription_end_date'] or 'N/A'}")
                print(f"Статус оплаты: {user['payment_status']}")
            else:
                print(f"\n❌ Пользователь {telegram_id} не найден в базе данных.")
                print("Это может быть новый пользователь, который еще не использовал /start")
    except Exception as e:
        print(f"Ошибка при проверке пользователя: {e}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Использование: python check_user.py <telegram_id>")
        sys.exit(1)
    
    try:
        user_id = int(sys.argv[1])
        check_user(user_id)
    except ValueError:
        print("Ошибка: telegram_id должен быть числом")
        sys.exit(1)


