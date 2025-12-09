"""
Скрипт для массового обновления данных пользователей с именем "Unknown".
Пытается получить реальные данные через Telegram API и обновить их в БД.
"""
import sys
import os

# Добавляем корневую директорию проекта в путь
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Меняем рабочую директорию на корень проекта, чтобы config.py мог найти env_vars.txt
os.chdir(project_root)

from database import get_db_connection
from loader import bot, logger, GROUP_CHAT_ID
from utils import retry_telegram_api


def get_user_info(user_id: int) -> tuple[str, str | None]:
    """
    Получает информацию о пользователе из Telegram API.
    Возвращает (first_name, username) или (None, None) если не удалось получить.
    """
    first_name = None
    username = None
    
    if not bot:
        print(f"  ⚠️  Бот не инициализирован")
        return None, None
    
    try:
        # Пробуем получить через get_chat
        try:
            chat = bot.get_chat(user_id)
            first_name = chat.first_name
            username = chat.username
            print(f"  ✅ Получены данные через get_chat: {first_name}, @{username if username else 'N/A'}")
            return first_name, username
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
                    return first_name, username
                except Exception as e2:
                    logger.warning(f"Could not get user info via get_chat_member({GROUP_CHAT_ID}, {user_id}): {e2}")
                    print(f"  ⚠️  Не удалось получить данные через API")
                    return None, None
    except Exception as e:
        logger.error(f"Error getting user info for {user_id}: {e}")
        print(f"  ⚠️  Ошибка при получении данных: {e}")
        return None, None


def update_user_data(user_id: int, first_name: str, username: str | None) -> bool:
    """
    Обновляет данные пользователя в БД.
    Возвращает True если успешно, False если ошибка.
    """
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET first_name = ?, username = ?
                WHERE telegram_id = ?
            """, (first_name, username, user_id))
            conn.commit()
        
        logger.info(f"User {user_id} data updated: {first_name}, @{username if username else 'N/A'}")
        return True
        
    except Exception as e:
        error_msg = f"Ошибка при обновлении данных пользователя {user_id}: {e}"
        logger.error(error_msg)
        print(f"  ❌ {error_msg}")
        return False


def update_unknown_users():
    """Обновляет данные всех пользователей с именем 'Unknown'"""
    print("Скрипт массового обновления данных пользователей")
    print("="*60)
    
    # Получаем всех пользователей с именем "Unknown"
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT telegram_id, first_name, username 
            FROM users 
            WHERE first_name = 'Unknown' OR first_name IS NULL
            ORDER BY telegram_id
        """)
        unknown_users = cursor.fetchall()
    
    if not unknown_users:
        print("\n✅ Пользователей с именем 'Unknown' не найдено!")
        return 0, 0, 0
    
    print(f"\nНайдено пользователей с именем 'Unknown': {len(unknown_users)}")
    print("Начинаем обновление данных...")
    print("="*60)
    
    updated_count = 0
    failed_count = 0
    skipped_count = 0
    
    for i, user in enumerate(unknown_users, 1):
        user_id = user['telegram_id']
        current_name = user['first_name'] or 'Unknown'
        current_username = user['username']
        
        print(f"\n[{i}/{len(unknown_users)}] Обновление пользователя {user_id}:")
        print(f"  Текущие данные: {current_name}, @{current_username if current_username else 'нет username'}")
        
        # Получаем информацию о пользователе
        first_name, username = get_user_info(user_id)
        
        if first_name:
            # Обновляем данные
            if update_user_data(user_id, first_name, username):
                username_str = f"@{username}" if username else "нет username"
                print(f"  ✅ Данные обновлены: {first_name} ({username_str})")
                updated_count += 1
            else:
                failed_count += 1
        else:
            print(f"  ⏭️  Не удалось получить данные, пропускаем")
            skipped_count += 1
    
    print("\n" + "="*60)
    print(f"\nИтоги:")
    print(f"  ✅ Успешно обновлено: {updated_count}")
    print(f"  ⏭️  Пропущено (не удалось получить данные): {skipped_count}")
    print(f"  ❌ Ошибок: {failed_count}")
    print(f"  📊 Всего обработано: {len(unknown_users)}")
    
    return updated_count, skipped_count, failed_count


if __name__ == '__main__':
    try:
        # Проверяем загрузку токена
        from config import load_config
        config = load_config()
        token = config.get('BOT_TOKEN')
        
        print("\nПроверка конфигурации:")
        print(f"  Рабочая директория: {os.getcwd()}")
        print(f"  Файл env_vars.txt существует: {os.path.exists('env_vars.txt')}")
        if token:
            print(f"  Токен загружен: {token[:10]}...{token[-10:]}")
        else:
            print(f"  ❌ Токен НЕ загружен!")
        
        if not bot:
            print("\n⚠️  Внимание: Бот не инициализирован (нет токена).")
            print("   Обновление данных невозможно без токена.")
            sys.exit(1)
        else:
            print(f"  ✅ Бот инициализирован успешно\n")
        
        updated, skipped, failed = update_unknown_users()
        
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
        logger.error(f"Critical error in update_unknown_users script: {e}", exc_info=True)
        sys.exit(1)

