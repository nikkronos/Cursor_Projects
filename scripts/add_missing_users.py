"""
Скрипт для массового добавления недостающих пользователей в базу данных.
Использует ту же логику, что и команда /migrate_user.
"""
import sys
import os
from datetime import datetime

# Добавляем корневую директорию проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Меняем рабочую директорию на корень проекта, чтобы config.py мог найти env_vars.txt
os.chdir(project_root)

from database import get_db_connection, format_db_date
from services import get_next_month_end
from config import load_config
from loader import bot, logger, GROUP_CHAT_ID
from utils import retry_telegram_api

# ID пользователей из скриншотов, которые отсутствуют в БД
MISSING_USER_IDS = [
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
    5923810582,
]


def get_user_info(user_id: int) -> tuple[str, str | None]:
    """
    Получает информацию о пользователе из Telegram API.
    Возвращает (first_name, username) или ("Unknown", None) если не удалось получить.
    """
    first_name = None
    username = None
    
    if not bot:
        print(f"  ⚠️  Бот не инициализирован, используем значения по умолчанию")
        return "Unknown", None
    
    try:
        # Пробуем получить через get_chat
        try:
            chat = bot.get_chat(user_id)
            first_name = chat.first_name
            username = chat.username
            print(f"  ✅ Получены данные через get_chat: {first_name}, @{username if username else 'N/A'}")
        except Exception as e:
            logger.warning(f"Could not get user info via get_chat({user_id}): {e}")
            # Пробуем через get_chat_member если пользователь в группе
            if GROUP_CHAT_ID:
                try:
                    def get_member():
                        return bot.get_chat_member(GROUP_CHAT_ID, user_id)
                    member = retry_telegram_api(get_member, max_attempts=2)
                    first_name = member.user.first_name
                    username = member.user.username
                    print(f"  ✅ Получены данные через get_chat_member: {first_name}, @{username if username else 'N/A'}")
                except Exception as e2:
                    logger.warning(f"Could not get user info via get_chat_member({GROUP_CHAT_ID}, {user_id}): {e2}")
                    print(f"  ⚠️  Не удалось получить данные через API, используем значения по умолчанию")
    except Exception as e:
        logger.error(f"Error getting user info for {user_id}: {e}")
        print(f"  ⚠️  Ошибка при получении данных: {e}")
    
    # Используем значения по умолчанию, если не удалось получить
    if not first_name:
        first_name = "Unknown"
    if not username:
        username = None
    
    return first_name, username


def add_user(user_id: int, first_name: str, username: str | None) -> bool:
    """
    Добавляет пользователя в БД с подпиской до конца следующего месяца.
    Возвращает True если успешно, False если ошибка.
    """
    try:
        now = datetime.now()
        # Используем функцию get_next_month_end для правильного расчета даты конца следующего месяца
        end_date = get_next_month_end(now)
        now_str = format_db_date(now)
        end_date_str = format_db_date(end_date)
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO users (telegram_id, first_name, username, subscription_status, subscription_start_date, subscription_end_date, payment_status, last_notification_level) 
                VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
                ON CONFLICT (telegram_id) 
                DO UPDATE SET 
                    first_name = ?,
                    username = ?,
                    subscription_status = 'active', 
                    subscription_end_date = ?, 
                    payment_status = 'paid', 
                    last_notification_level = NULL
            """, (user_id, first_name, username, 'active', now_str, end_date_str, 'paid', first_name, username, end_date_str))
            conn.commit()
        
        logger.info(f"User {user_id} ({first_name}) migrated with active sub until {end_date}.")
        return True
        
    except Exception as e:
        error_msg = f"Ошибка при добавлении пользователя {user_id}: {e}"
        logger.error(error_msg)
        print(f"  ❌ {error_msg}")
        return False


def add_missing_users():
    """Добавляет всех недостающих пользователей в БД"""
    print(f"Начинаем добавление {len(MISSING_USER_IDS)} пользователей...")
    print("="*60)
    
    added_count = 0
    failed_count = 0
    skipped_count = 0
    
    for i, user_id in enumerate(MISSING_USER_IDS, 1):
        print(f"\n[{i}/{len(MISSING_USER_IDS)}] Обработка пользователя {user_id}:")
        
        # Проверяем, не добавлен ли уже пользователь
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT telegram_id FROM users WHERE telegram_id = ?", (user_id,))
            if cursor.fetchone():
                print(f"  ⏭️  Пользователь уже существует в БД, пропускаем")
                skipped_count += 1
                continue
        
        # Получаем информацию о пользователе
        first_name, username = get_user_info(user_id)
        
        # Добавляем пользователя
        if add_user(user_id, first_name, username):
            username_str = f"@{username}" if username else "нет username"
            print(f"  ✅ Пользователь добавлен: {first_name} ({username_str})")
            added_count += 1
        else:
            failed_count += 1
    
    print("\n" + "="*60)
    print(f"\nИтоги:")
    print(f"  ✅ Успешно добавлено: {added_count}")
    print(f"  ⏭️  Пропущено (уже есть в БД): {skipped_count}")
    print(f"  ❌ Ошибок: {failed_count}")
    print(f"  📊 Всего обработано: {len(MISSING_USER_IDS)}")
    
    return added_count, skipped_count, failed_count


if __name__ == '__main__':
    try:
        print("Скрипт массового добавления пользователей")
        print("="*60)
        
        # Проверяем загрузку токена
        config = load_config()
        token = config.get('BOT_TOKEN')
        print(f"\nПроверка конфигурации:")
        print(f"  Рабочая директория: {os.getcwd()}")
        print(f"  Путь к env_vars.txt: {os.path.join(os.getcwd(), 'env_vars.txt')}")
        print(f"  Файл env_vars.txt существует: {os.path.exists('env_vars.txt')}")
        if token:
            print(f"  Токен загружен: {token[:10]}...{token[-10:]}")
        else:
            print(f"  ❌ Токен НЕ загружен!")
        
        # Проверяем, что бот инициализирован (опционально)
        if not bot:
            print("\n⚠️  Внимание: Бот не инициализирован (нет токена).")
            print("   Пользователи будут добавлены с именем 'Unknown' и без username.")
            response = input("\nПродолжить? (y/n): ")
            if response.lower() != 'y':
                print("Отменено.")
                sys.exit(0)
        else:
            print(f"  ✅ Бот инициализирован успешно")
        
        added, skipped, failed = add_missing_users()
        
        if failed == 0:
            print("\n✅ Все пользователи успешно обработаны!")
            sys.exit(0)
        else:
            print(f"\n⚠️  Обработано с ошибками. Проверьте логи.")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n\n⚠️  Прервано пользователем.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Критическая ошибка: {e}")
        logger.error(f"Critical error in add_missing_users script: {e}", exc_info=True)
        sys.exit(1)

