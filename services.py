from datetime import datetime, timedelta
from typing import Any
from apscheduler.schedulers.background import BackgroundScheduler
from loader import bot, logger, ADMIN_ID, GROUP_CHAT_ID, GROUP_INVITE_LINK
from database import get_db_connection, parse_db_date, format_db_date, get_all_users_for_check, get_user_status, get_active_users
from utils import safe_send_message, retry_telegram_api

def remove_user_from_group(user_id: int, chat_id: int) -> bool:
    if user_id == ADMIN_ID:
        logger.info(f"Попытка удалить администратора {user_id} из группы отклонена.")
        return True 

    try:
        # Используем retry для критичных операций удаления пользователя
        def kick_user():
            bot.kick_chat_member(chat_id, user_id)
        
        def unban_user():
            bot.unban_chat_member(chat_id, user_id)
        
        retry_telegram_api(kick_user, max_attempts=3)
        retry_telegram_api(unban_user, max_attempts=3)
        logger.info(f"Пользователь {user_id} удален из группы {chat_id} и разблокирован.")
        return True
    except Exception as e:
        error_message = str(e)
        if "chat owner" in error_message or "administrators" in error_message:
            logger.warning(f"Невозможно удалить пользователя {user_id} (владелец/админ): {error_message}")
            return True 
        
        logger.error(f"Ошибка при удалении/разблокировке пользователя {user_id} из группы {chat_id}: {e}")
        return False

def add_subscription_days_logic(user_id: int, days_to_add: int, chat_id: int, minutes_to_add: int = 0) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT subscription_end_date FROM users WHERE telegram_id = ?", (user_id,))
            result = cursor.fetchone()
            
            new_end_date = None
            now = datetime.now()

            if result and result['subscription_end_date']:
                current_end_date = parse_db_date(result['subscription_end_date'])
                if current_end_date < now:
                     base_date = now
                else:
                     base_date = current_end_date
                
                new_end_date = base_date + timedelta(days=days_to_add, minutes=minutes_to_add)
            else: 
                new_end_date = now + timedelta(days=days_to_add, minutes=minutes_to_add)

            new_end_date_str = format_db_date(new_end_date)
            now_str = format_db_date(now)

            if result: 
                cursor.execute("UPDATE users SET subscription_end_date = ?, subscription_status = ?, last_notification_level = NULL WHERE telegram_id = ?", (new_end_date_str, 'active', user_id))
            else: 
                cursor.execute("INSERT INTO users (telegram_id, subscription_start_date, subscription_end_date, subscription_status, last_notification_level) VALUES (?, ?, ?, ?, NULL)",
                               (user_id, now_str, new_end_date_str, 'active'))
            conn.commit()
        
        if minutes_to_add > 0 and days_to_add == 0:
             safe_send_message(bot, chat_id, f"Пользователю {user_id} добавлена подписка на {minutes_to_add} минут. Дата окончания: {new_end_date.strftime('%H:%M:%S %d.%m.%Y')}")
        else:
             safe_send_message(bot, chat_id, f"К подписке пользователя {user_id} добавлено {days_to_add} дней. Новая дата окончания: {new_end_date.strftime('%d.%m.%Y')}")

        try:
            if minutes_to_add > 0 and days_to_add == 0:
                safe_send_message(bot, user_id, f"Вам добавлено {minutes_to_add} минут подписки (тест). Действует до: {new_end_date.strftime('%H:%M:%S %d.%m.%Y')}")
            else:
                safe_send_message(bot, user_id, f"Ваша подписка активирована/продлена на {days_to_add} дней. Действует до: {new_end_date.strftime('%d.%m.%Y')}")
            
            try:
                def get_member():
                    return bot.get_chat_member(GROUP_CHAT_ID, user_id)
                member = retry_telegram_api(get_member, max_attempts=2)
                if member.status in ['creator', 'administrator', 'member']:
                    pass 
                else:
                     safe_send_message(bot, user_id, f"Теперь вы можете вступить в группу (если еще не там) по ссылке: {GROUP_INVITE_LINK}")
            except Exception:
                safe_send_message(bot, user_id, f"Теперь вы можете вступить в группу (если еще не там) по ссылке: {GROUP_INVITE_LINK}")

        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")

    except Exception as e:
        safe_send_message(bot, chat_id, f"Ошибка при добавлении дней к подписке: {e}")
        logger.error(f"Error adding subscription days: {e}")

def remove_subscription_days_logic(user_id: int, days_to_remove: int, chat_id: int) -> None:
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT subscription_end_date FROM users WHERE telegram_id = ?", (user_id,))
            result = cursor.fetchone()
            
            if result and result['subscription_end_date']:
                current_end_date = parse_db_date(result['subscription_end_date'])
                new_end_date = current_end_date - timedelta(days=days_to_remove)
                new_end_date_str = format_db_date(new_end_date)
                
                cursor.execute("UPDATE users SET subscription_end_date = ?, last_notification_level = NULL WHERE telegram_id = ?", (new_end_date_str, user_id))
                conn.commit()
                
                safe_send_message(bot, chat_id, f"Из подписки пользователя {user_id} вычтено {days_to_remove} дней. Новая дата окончания: {new_end_date.strftime('%H:%M:%S %d.%m.%Y')}")
                
                try:
                    safe_send_message(bot, user_id, f"Срок вашей подписки уменьшен на {days_to_remove} дней. Новая дата окончания: {new_end_date.strftime('%d.%m.%Y')}")
                except Exception as e:
                     logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")

            else:
                safe_send_message(bot, chat_id, f"Пользователь {user_id} не найден или у него нет даты окончания подписки.")
    except Exception as e:
        safe_send_message(bot, chat_id, f"Ошибка при вычитании дней из подписки: {e}")
        logger.error(f"Error removing subscription days: {e}")

def check_subscriptions() -> None:
    """Проверка подписок и отправка уведомлений. Оптимизировано: одно соединение с БД для всех обновлений."""
    try:
        users_to_check = get_all_users_for_check()
        today = datetime.now()
        
        # Открываем одно соединение для всех обновлений БД
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            for user in users_to_check:
                try:
                    user_id, first_name = user['telegram_id'], user['first_name']
                    sub_status = user['subscription_status']
                    last_notif_level = user['last_notification_level']
                    
                    end_date = parse_db_date(user['subscription_end_date'])

                    if sub_status == 'active' and end_date:
                        time_left = end_date - today
                        days_left = time_left.days
                        seconds_left = time_left.total_seconds()
                        hours_left = seconds_left / 3600
                        
                        reminder_text = "\n\nЕсли вы не будете продлевать подписку, то напишите, пожалуйста, о своей причине в форме обратной связи."

                        if end_date < today:
                            safe_send_message(bot, user_id, f"Привет, {first_name}! Твоя подписка истекла {end_date.strftime('%d.%m.%Y')}. Пожалуйста, продли ее.")
                            
                            cursor.execute("UPDATE users SET subscription_status = 'inactive', last_notification_level = 'expired' WHERE telegram_id = ?", (user_id,))
                            
                            if remove_user_from_group(user_id, GROUP_CHAT_ID):
                                cursor.execute("UPDATE users SET last_notification_level = 'kicked' WHERE telegram_id = ?", (user_id,))
                                logger.info(f"Пользователь {user_id} обработан как удаленный из группы (истечение подписки).")

                        elif 1 < days_left <= 3 and last_notif_level != '3days':
                            safe_send_message(bot, user_id, f"Привет, {first_name}! Твоя подписка истекает через 3 дня ({end_date.strftime('%d.%m.%Y')}). Пожалуйста, не забудь продлить.{reminder_text}")
                            cursor.execute("UPDATE users SET last_notification_level = '3days' WHERE telegram_id = ?", (user_id,))
                        
                        elif 0 < days_left <= 1 and last_notif_level != '1day':
                            safe_send_message(bot, user_id, f"Привет, {first_name}! Твоя подписка истекает завтра ({end_date.strftime('%d.%m.%Y')}).{reminder_text}")
                            cursor.execute("UPDATE users SET last_notification_level = '1day' WHERE telegram_id = ?", (user_id,))
                        
                        elif 0 < hours_left <= 1 and last_notif_level != '1hour':
                            safe_send_message(bot, user_id, f"Привет, {first_name}! Твоя подписка истекает менее чем через час!{reminder_text}")
                            cursor.execute("UPDATE users SET last_notification_level = '1hour' WHERE telegram_id = ?", (user_id,))

                    elif sub_status == 'inactive' and last_notif_level != 'kicked':
                        if remove_user_from_group(user_id, GROUP_CHAT_ID):
                            cursor.execute("UPDATE users SET last_notification_level = 'kicked' WHERE telegram_id = ?", (user_id,))
                            logger.info(f"Пользователь {user_id} удален из группы (подписка неактивна).")
                
                except Exception as user_error:
                    # Ошибка при обработке одного пользователя не должна останавливать обработку остальных
                    logger.error(f"Error processing user {user.get('telegram_id', 'unknown')} in check_subscriptions: {user_error}")
                    continue
            
            # Коммитим все изменения одним разом в конце
            conn.commit()
            
    except Exception as e:
        # Разделяем обработку ошибок по типам для более детального логирования
        error_type = type(e).__name__
        error_message = str(e)
        
        if "database" in error_message.lower() or "sqlite" in error_message.lower():
            logger.critical(f"Database error in check_subscriptions: {error_type} - {error_message}")
        elif "telegram" in error_message.lower() or "api" in error_message.lower():
            logger.error(f"Telegram API error in check_subscriptions: {error_type} - {error_message}")
        else:
            logger.error(f"Error in check_subscriptions: {error_type} - {error_message}")

def notify_tariff_available() -> None:
    """Отправляет уведомление всем активным пользователям о том, что тарифы доступны"""
    try:
        active_users = get_active_users()
        message_text = "Теперь можно продлить доступ"
        
        for user in active_users:
            user_id = user['telegram_id']
            try:
                safe_send_message(bot, user_id, message_text)
                logger.info(f"Tariff availability notification sent to user {user_id}")
            except Exception as e:
                logger.error(f"Failed to send tariff notification to user {user_id}: {e}")
        
        logger.info(f"Tariff availability notifications sent to {len(active_users)} active users")
    except Exception as e:
        logger.error(f"Error sending tariff availability notifications: {e}")

def start_scheduler() -> None:
    scheduler = BackgroundScheduler()
    scheduler.add_job(check_subscriptions, 'interval', minutes=30)
    
    # Задача на отправку уведомления о доступности тарифов: 25.12.2025 в 12:00 МСК (09:00 UTC)
    from datetime import timezone
    notification_time = datetime(2025, 12, 25, 9, 0, 0, tzinfo=timezone.utc)
    scheduler.add_job(notify_tariff_available, 'date', run_date=notification_time, id='tariff_notification')
    
    scheduler.start()

