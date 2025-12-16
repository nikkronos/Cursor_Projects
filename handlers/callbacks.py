"""
Callback query handlers for TradeTherapyBot.
Handles inline keyboard button callbacks (confirm/reject payments, tariffs, etc.)
"""
from telebot import types
from datetime import datetime
from loader import bot, logger, ADMIN_ID
from database import get_db_connection, format_db_date, get_user_status
from services import add_subscription_days_logic
from utils import safe_send_message


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_pay_'))
def handle_confirm_payment(call: types.CallbackQuery) -> None:
    """Обработчик подтверждения оплаты"""
    # Проверяем, что это админ
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может подтверждать оплаты.", show_alert=True)
        return
    
    try:
        # Извлекаем user_id из callback_data
        user_id = int(call.data.split('_')[-1])
        
        # Получаем информацию о пользователе
        user_data = get_user_status(user_id)
        if not user_data:
            bot.answer_callback_query(call.id, "Пользователь не найден в базе данных.", show_alert=True)
            return
        
        # Вычисляем дату до 1-го числа следующего месяца
        now = datetime.now()
        if now.month == 12:
            next_month = now.replace(year=now.year + 1, month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
        else:
            next_month = now.replace(month=now.month + 1, day=1, hour=0, minute=0, second=0, microsecond=0)
        
        next_month_str = format_db_date(next_month)
        now_str = format_db_date(now)
        
        # Обновляем подписку в БД
        with get_db_connection() as conn:
            cursor = conn.cursor()
            # Обновляем статус подписки и дату окончания
            cursor.execute("""
                UPDATE users 
                SET subscription_status = 'active', 
                    subscription_end_date = ?,
                    subscription_start_date = COALESCE(subscription_start_date, ?),
                    payment_status = 'paid',
                    last_notification_level = NULL
                WHERE telegram_id = ?
            """, (next_month_str, now_str, user_id))
            conn.commit()
        
        logger.info(f"Оплата подтверждена для пользователя {user_id}. Подписка продлена до {next_month.strftime('%d.%m.%Y')}")
        
        # Отправляем уведомление пользователю
        first_name = user_data.get('first_name', 'Пользователь')
        try:
            safe_send_message(bot, user_id, 
                f"✅ Ваша оплата подтверждена, {first_name}!\n\n"
                f"Подписка продлена до {next_month.strftime('%d.%m.%Y')}.\n\n"
                f"Спасибо за поддержку сообщества!")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        
        # Обновляем сообщение админу
        bot.answer_callback_query(call.id, "✅ Оплата подтверждена")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        bot.send_message(ADMIN_ID, f"✅ Оплата пользователя {user_id} ({first_name}) подтверждена. Подписка продлена до {next_month.strftime('%d.%m.%Y')}")
        
    except ValueError:
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных.", show_alert=True)
        logger.error(f"Ошибка при парсинге user_id из callback_data: {call.data}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка при подтверждении оплаты: {e}", show_alert=True)
        logger.error(f"Ошибка при подтверждении оплаты: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_pay_'))
def handle_reject_payment(call: types.CallbackQuery) -> None:
    """Обработчик отклонения оплаты"""
    # Проверяем, что это админ
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может отклонять оплаты.", show_alert=True)
        return
    
    try:
        # Извлекаем user_id из callback_data
        user_id = int(call.data.split('_')[-1])
        
        # Получаем информацию о пользователе
        user_data = get_user_status(user_id)
        if not user_data:
            bot.answer_callback_query(call.id, "Пользователь не найден в базе данных.", show_alert=True)
            return
        
        # Обновляем статус оплаты в БД
        with get_db_connection() as conn:
            conn.execute("UPDATE users SET payment_status = 'rejected' WHERE telegram_id = ?", (user_id,))
            conn.commit()
        
        logger.info(f"Оплата отклонена для пользователя {user_id}")
        
        # Отправляем уведомление пользователю
        first_name = user_data.get('first_name', 'Пользователь')
        try:
            safe_send_message(bot, user_id, 
                f"❌ Ваша оплата была отклонена, {first_name}.\n\n"
                f"Если у вас есть вопросы, свяжитесь с администратором через форму обратной связи.")
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        
        # Обновляем сообщение админу
        bot.answer_callback_query(call.id, "❌ Оплата отклонена")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        bot.send_message(ADMIN_ID, f"❌ Оплата пользователя {user_id} ({first_name}) отклонена.")
        
    except ValueError:
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных.", show_alert=True)
        logger.error(f"Ошибка при парсинге user_id из callback_data: {call.data}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка при отклонении оплаты: {e}", show_alert=True)
        logger.error(f"Ошибка при отклонении оплаты: {e}")
