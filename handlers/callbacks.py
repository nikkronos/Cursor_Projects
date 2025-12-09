"""
Callback query handlers for TradeTherapyBot.
Handles inline button callbacks for payment confirmations, tariff approvals, etc.
"""
from telebot import types
from datetime import datetime
from loader import bot, logger, ADMIN_ID
from database import get_db_connection, format_db_date
from services import get_next_month_end
from utils import safe_send_message


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_pay_'))
def callback_confirm_payment(call: types.CallbackQuery) -> None:
    """Обработчик подтверждения оплаты администратором"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "У вас нет прав для этого действия.")
        return
    
    try:
        # Извлекаем user_id из callback_data (формат: "confirm_pay_{user_id}")
        user_id = int(call.data.split('_')[-1])
        
        # Получаем текущую дату окончания подписки пользователя
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT subscription_end_date, first_name, username 
                FROM users 
                WHERE telegram_id = ?
            """, (user_id,))
            user = cursor.fetchone()
            
            if not user:
                bot.answer_callback_query(call.id, "Пользователь не найден в базе данных.")
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                return
            
            # Рассчитываем новую дату окончания - до конца следующего месяца
            now = datetime.now()
            new_end_date = get_next_month_end(now)
            new_end_date_str = format_db_date(new_end_date)
            
            # Обновляем подписку пользователя
            cursor.execute("""
                UPDATE users 
                SET subscription_status = 'active',
                    subscription_end_date = ?,
                    payment_status = 'paid',
                    last_notification_level = NULL
                WHERE telegram_id = ?
            """, (new_end_date_str, user_id))
            conn.commit()
        
        logger.info(f"Payment confirmed for user {user_id}. Subscription extended until {new_end_date}")
        
        # Отправляем подтверждение администратору
        first_name = user['first_name'] or 'Unknown'
        username_str = f"@{user['username']}" if user['username'] else "нет username"
        bot.answer_callback_query(call.id, "Оплата подтверждена!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(ADMIN_ID, 
                        f"✅ Оплата подтверждена для пользователя:\n\n"
                        f"ID: {user_id}\n"
                        f"Имя: {first_name}\n"
                        f"Username: {username_str}\n"
                        f"Подписка продлена до: {new_end_date.strftime('%d.%m.%Y %H:%M')}")
        
        # Отправляем уведомление пользователю
        try:
            safe_send_message(bot, user_id, 
                            f"✅ Ваша оплата подтверждена!\n\n"
                            f"Подписка продлена до: {new_end_date.strftime('%d.%m.%Y %H:%M')}\n\n"
                            f"Спасибо за оплату!")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
    except ValueError:
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных.")
        logger.error(f"Invalid callback data format: {call.data}")
    except Exception as e:
        error_msg = f"Ошибка при подтверждении оплаты: {e}"
        logger.error(error_msg, exc_info=True)
        bot.answer_callback_query(call.id, "Произошла ошибка при подтверждении оплаты.")
        safe_send_message(bot, ADMIN_ID, error_msg)


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_pay_'))
def callback_reject_payment(call: types.CallbackQuery) -> None:
    """Обработчик отклонения оплаты администратором"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "У вас нет прав для этого действия.")
        return
    
    try:
        # Извлекаем user_id из callback_data (формат: "reject_pay_{user_id}")
        user_id = int(call.data.split('_')[-1])
        
        # Получаем информацию о пользователе
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT first_name, username 
                FROM users 
                WHERE telegram_id = ?
            """, (user_id,))
            user = cursor.fetchone()
            
            if not user:
                bot.answer_callback_query(call.id, "Пользователь не найден в базе данных.")
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
                return
            
            # Обновляем статус оплаты на 'pending'
            cursor.execute("""
                UPDATE users 
                SET payment_status = 'pending'
                WHERE telegram_id = ?
            """, (user_id,))
            
            # Удаляем чек из таблицы receipts
            cursor.execute("""
                DELETE FROM receipts 
                WHERE user_id = ?
            """, (user_id,))
            
            conn.commit()
        
        logger.info(f"Payment rejected for user {user_id}")
        
        # Отправляем подтверждение администратору
        first_name = user['first_name'] or 'Unknown'
        username_str = f"@{user['username']}" if user['username'] else "нет username"
        bot.answer_callback_query(call.id, "Оплата отклонена!")
        bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=None)
        bot.send_message(ADMIN_ID, 
                        f"❌ Оплата отклонена для пользователя:\n\n"
                        f"ID: {user_id}\n"
                        f"Имя: {first_name}\n"
                        f"Username: {username_str}")
        
        # Отправляем уведомление пользователю
        try:
            safe_send_message(bot, user_id, 
                            f"❌ Ваша оплата была отклонена.\n\n"
                            f"Пожалуйста, проверьте чек и отправьте его снова, или свяжитесь с администратором.")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
    except ValueError:
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных.")
        logger.error(f"Invalid callback data format: {call.data}")
    except Exception as e:
        error_msg = f"Ошибка при отклонении оплаты: {e}"
        logger.error(error_msg, exc_info=True)
        bot.answer_callback_query(call.id, "Произошла ошибка при отклонении оплаты.")
        safe_send_message(bot, ADMIN_ID, error_msg)
