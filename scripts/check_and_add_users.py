"""
Скрипт для проверки и добавления пользователей из скриншотов.
Проверяет наличие пользователей в БД и выводит список отсутствующих.
"""
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import get_db_connection

# ID пользователей из скриншотов
USER_IDS_FROM_SCREENSHOTS = [
    266036332,
    694180315,
    820136776,
    871902505,
    5123301955,
    841626442,
    704970831,
    5621382577,
    1130977365,
    386977572,
    1001781237,
    351989935,
    356381069,
    406315652,
    536493326,
    87495646,
    1909876357,
    434949440,
    5154058087,
    5079005371,
    378693761,
    5029953750,
    750101239,
    677671588,
    687124427,
    785720443,
    240059157,
    135509949,
    486384359,
    713741360,
    1598767139,
    7882817110,
    135366416,
    5923810582,
]

def check_users():
    """Проверяет наличие пользователей в БД"""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        existing_users = []
        missing_users = []
        
        for user_id in USER_IDS_FROM_SCREENSHOTS:
            cursor.execute("SELECT telegram_id, first_name, username, subscription_status FROM users WHERE telegram_id = ?", (user_id,))
            user = cursor.fetchone()
            
            if user:
                existing_users.append({
                    'id': user_id,
                    'name': user['first_name'] or 'Unknown',
                    'username': user['username'] or 'нет username',
                    'status': user['subscription_status']
                })
            else:
                missing_users.append(user_id)
    
    print(f"Всего пользователей в скриншотах: {len(USER_IDS_FROM_SCREENSHOTS)}")
    print(f"Найдено в БД: {len(existing_users)}")
    print(f"Отсутствует в БД: {len(missing_users)}")
    print("\n" + "="*50)
    
    if existing_users:
        print("\nПользователи, найденные в БД:")
        for user in existing_users:
            username_str = f"@{user['username']}" if user['username'] != 'нет username' else "нет username"
            print(f"  ID: {user['id']}, Имя: {user['name']}, Username: {username_str}, Статус: {user['status']}")
    
    if missing_users:
        print("\nПользователи, отсутствующие в БД (ID для добавления):")
        print("  " + ", ".join(map(str, missing_users)))
        print("\nДля добавления используйте команду:")
        for user_id in missing_users:
            print(f"  /migrate_user {user_id}")
    else:
        print("\nВсе пользователи из скриншотов найдены в БД!")
    
    return missing_users

if __name__ == '__main__':
    try:
        missing = check_users()
        sys.exit(0 if not missing else 1)
    except Exception as e:
        print(f"Ошибка: {e}")
        sys.exit(1)

