"""
Admin handlers for TradeTherapyBot.
Contains admin-only commands and functions.
"""
from telebot import types
from datetime import datetime
from loader import bot, logger, ADMIN_ID, GROUP_CHAT_ID
from database import get_db_connection, format_db_date
from utils import retry_telegram_api


@bot.message_handler(commands=['migrate_user'])
def handle_migrate_user(message: types.Message) -> None:
    """Команда для выдачи подписки существующим участникам группы"""
    if message.from_user.id != ADMIN_ID:
        return
    
    # Парсим user_id из аргументов команды
    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.send_message(ADMIN_ID, "Использование: /migrate_user <user_id>")
        return
    
    try:
        user_id = int(command_parts[1])
    except ValueError:
        bot.send_message(ADMIN_ID, f"Ошибка: '{command_parts[1]}' не является валидным ID пользователя.")
        return
    
    # Получаем информацию о пользователе из Telegram API
    first_name = None
    username = None
    
    try:
        # Пробуем получить через get_chat
        try:
            chat = bot.get_chat(user_id)
            first_name = chat.first_name
            username = chat.username
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
                except Exception as e2:
                    logger.warning(f"Could not get user info via get_chat_member({GROUP_CHAT_ID}, {user_id}): {e2}")
    except Exception as e:
        logger.error(f"Error getting user info for {user_id}: {e}")
    
    # Используем значения по умолчанию, если не удалось получить
    if not first_name:
        first_name = "Unknown"
    if not username:
        username = None
    
    # Добавляем/обновляем пользователя в БД с подпиской до конца месяца
    try:
        now = datetime.now()
        if now.month == 12:
            next_month = now.replace(year=now.year+1, month=1, day=1, hour=23, minute=59, second=59)
        else:
            next_month = now.replace(month=now.month+1, day=1, hour=23, minute=59, second=59)
        
        end_date = next_month
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
        
        # Отправляем подтверждение админу
        username_str = f"@{username}" if username else "нет username"
        response = (
            f"Пользователь успешно добавлен/обновлен:\n\n"
            f"ID: {user_id}\n"
            f"Имя: {first_name}\n"
            f"Username: {username_str}\n"
            f"Начало: {now.strftime('%d.%m.%Y %H:%M')}\n"
            f"Конец: {end_date.strftime('%d.%m.%Y %H:%M')}\n"
            f"Оплата: paid"
        )
        bot.send_message(ADMIN_ID, response)
        
    except Exception as e:
        error_msg = f"Ошибка при миграции пользователя {user_id}: {e}"
        logger.error(error_msg)
        bot.send_message(ADMIN_ID, error_msg)
