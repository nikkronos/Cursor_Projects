"""
Callback query handlers for TradeTherapyBot.
Handles inline keyboard button callbacks (confirm/reject payments, tariffs, etc.)
"""
from telebot import types
from datetime import datetime
import calendar
from loader import bot, logger, ADMIN_ID
from database import get_db_connection, format_db_date, get_user_status
from utils import safe_send_message


def calculate_subscription_end_date() -> datetime:
    """Вычисляет дату окончания подписки: последний день следующего месяца до 23:00"""
    now = datetime.now()
    if now.month == 12:
        # Если декабрь, следующий месяц - январь следующего года
        next_month_num = 1
        next_year = now.year + 1
    else:
        next_month_num = now.month + 1
        next_year = now.year
    
    # Получаем последний день следующего месяца
    last_day = calendar.monthrange(next_year, next_month_num)[1]
    
    # Устанавливаем дату на последний день следующего месяца в 23:00
    return datetime(next_year, next_month_num, last_day, 23, 0, 0, 0)


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
        
        # Вычисляем дату до последнего дня следующего месяца до 23:00
        end_date = calculate_subscription_end_date()
        end_date_str = format_db_date(end_date)
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
            """, (end_date_str, now_str, user_id))
            conn.commit()
        
        logger.info(f"Оплата подтверждена для пользователя {user_id}. Подписка продлена до {end_date.strftime('%d.%m.%Y %H:%M')}")
        
        # Отправляем уведомление пользователю со стандартной кнопкой
        first_name = user_data['first_name'] if user_data['first_name'] else 'Пользователь'
        try:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            back_button = types.KeyboardButton("Вернутся в главное меню🏡")
            markup.add(back_button)
            
            bot.send_message(user_id, 
                f"✅ Ваша оплата подтверждена, {first_name}!\n\n"
                f"Подписка продлена до {end_date.strftime('%d.%m.%Y %H:%M')}.\n\n"
                f"Спасибо за поддержку сообщества!",
                reply_markup=markup)
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        
        # Обновляем сообщение админу
        bot.answer_callback_query(call.id, "✅ Оплата подтверждена")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        bot.send_message(ADMIN_ID, f"✅ Оплата пользователя {user_id} ({first_name}) подтверждена. Подписка продлена до {end_date.strftime('%d.%m.%Y %H:%M')}")
        
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
        
        # Отправляем уведомление пользователю с кнопкой "Обратная связь"
        first_name = user_data['first_name'] if user_data['first_name'] else 'Пользователь'
        try:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            feedback_btn = types.KeyboardButton("Обратная связь")
            markup.add(feedback_btn)
            
            bot.send_message(user_id, 
                f"❌ Ваша оплата была отклонена, {first_name}.\n\n"
                f"Если у вас есть вопросы, свяжитесь с администратором через форму обратной связи.",
                reply_markup=markup)
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


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_reason_trading_'))
def handle_confirm_reason_trading(call: types.CallbackQuery) -> None:
    """Обработчик подтверждения причины 'Я не торгую' - продлевает до последнего дня следующего месяца до 23:00"""
    # Проверяем, что это админ
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может подтверждать.", show_alert=True)
        return
    
    try:
        # Извлекаем user_id из callback_data
        user_id = int(call.data.split('_')[-1])
        
        # Получаем информацию о пользователе
        user_data = get_user_status(user_id)
        if not user_data:
            bot.answer_callback_query(call.id, "Пользователь не найден в базе данных.", show_alert=True)
            return
        
        # Вычисляем дату до последнего дня следующего месяца до 23:00
        end_date = calculate_subscription_end_date()
        end_date_str = format_db_date(end_date)
        now_str = format_db_date(datetime.now())
        
        # Обновляем подписку в БД
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET subscription_status = 'active', 
                    subscription_end_date = ?,
                    subscription_start_date = COALESCE(subscription_start_date, ?),
                    payment_status = 'paid',
                    last_notification_level = NULL
                WHERE telegram_id = ?
            """, (end_date_str, now_str, user_id))
            conn.commit()
        
        first_name = user_data['first_name'] if user_data['first_name'] else 'Пользователь'
        logger.info(f"Причина 'Я не торгую' подтверждена для пользователя {user_id}. Подписка продлена до {end_date.strftime('%d.%m.%Y %H:%M')}")
        
        # Отправляем уведомление пользователю со стандартной кнопкой
        try:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            back_button = types.KeyboardButton("Вернутся в главное меню🏡")
            markup.add(back_button)
            
            bot.send_message(user_id, 
                f"✅ Ваша причина принята, {first_name}!\n\n"
                f"Подписка продлена до {end_date.strftime('%d.%m.%Y %H:%M')}.",
                reply_markup=markup)
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        
        # Обновляем сообщение админу
        bot.answer_callback_query(call.id, "✅ Причина подтверждена")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        bot.send_message(ADMIN_ID, f"✅ Причина 'Я не торгую' пользователя {user_id} ({first_name}) подтверждена. Подписка продлена до {end_date.strftime('%d.%m.%Y %H:%M')}.")
        
    except ValueError:
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных.", show_alert=True)
        logger.error(f"Ошибка при парсинге user_id из callback_data: {call.data}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка при подтверждении: {e}", show_alert=True)
        logger.error(f"Ошибка при подтверждении причины 'Я не торгую': {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_reason_trading_'))
def handle_reject_reason_trading(call: types.CallbackQuery) -> None:
    """Обработчик отклонения причины 'Я не торгую'"""
    # Проверяем, что это админ
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может отклонять.", show_alert=True)
        return
    
    try:
        # Извлекаем user_id из callback_data
        user_id = int(call.data.split('_')[-1])
        
        # Получаем информацию о пользователе
        user_data = get_user_status(user_id)
        if not user_data:
            bot.answer_callback_query(call.id, "Пользователь не найден в базе данных.", show_alert=True)
            return
        
        logger.info(f"Причина 'Я не торгую' отклонена для пользователя {user_id}")
        
        # Отправляем уведомление пользователю с кнопкой "Обратная связь"
        first_name = user_data['first_name'] if user_data['first_name'] else 'Пользователь'
        try:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            feedback_btn = types.KeyboardButton("Обратная связь")
            markup.add(feedback_btn)
            
            bot.send_message(user_id, 
                f"❌ Ваша причина была отклонена, {first_name}.\n\n"
                f"Если у вас есть вопросы, свяжитесь с администратором через форму обратной связи.",
                reply_markup=markup)
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        
        # Обновляем сообщение админу
        bot.answer_callback_query(call.id, "❌ Причина отклонена")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        bot.send_message(ADMIN_ID, f"❌ Причина 'Я не торгую' пользователя {user_id} ({first_name}) отклонена.")
        
    except ValueError:
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных.", show_alert=True)
        logger.error(f"Ошибка при парсинге user_id из callback_data: {call.data}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка при отклонении: {e}", show_alert=True)
        logger.error(f"Ошибка при отклонении причины 'Я не торгую': {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_reason_other_'))
def handle_confirm_reason_other(call: types.CallbackQuery) -> None:
    """Обработчик подтверждения причины 'Не буду платить по другой причине' - продлевает до последнего дня следующего месяца до 23:00"""
    # Проверяем, что это админ
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может подтверждать.", show_alert=True)
        return
    
    try:
        # Извлекаем user_id из callback_data
        user_id = int(call.data.split('_')[-1])
        
        # Получаем информацию о пользователе
        user_data = get_user_status(user_id)
        if not user_data:
            bot.answer_callback_query(call.id, "Пользователь не найден в базе данных.", show_alert=True)
            return
        
        # Вычисляем дату до последнего дня следующего месяца до 23:00
        end_date = calculate_subscription_end_date()
        end_date_str = format_db_date(end_date)
        now_str = format_db_date(datetime.now())
        
        # Обновляем подписку в БД
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE users 
                SET subscription_status = 'active', 
                    subscription_end_date = ?,
                    subscription_start_date = COALESCE(subscription_start_date, ?),
                    payment_status = 'paid',
                    last_notification_level = NULL
                WHERE telegram_id = ?
            """, (end_date_str, now_str, user_id))
            conn.commit()
        
        first_name = user_data['first_name'] if user_data['first_name'] else 'Пользователь'
        logger.info(f"Причина 'Другая причина' подтверждена для пользователя {user_id}. Подписка продлена до {end_date.strftime('%d.%m.%Y %H:%M')}")
        
        # Отправляем уведомление пользователю со стандартной кнопкой
        try:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            back_button = types.KeyboardButton("Вернутся в главное меню🏡")
            markup.add(back_button)
            
            bot.send_message(user_id, 
                f"✅ Ваша причина принята, {first_name}!\n\n"
                f"Подписка продлена до {end_date.strftime('%d.%m.%Y %H:%M')}.",
                reply_markup=markup)
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        
        # Обновляем сообщение админу
        bot.answer_callback_query(call.id, "✅ Причина подтверждена")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        bot.send_message(ADMIN_ID, f"✅ Причина 'Другая причина' пользователя {user_id} ({first_name}) подтверждена. Подписка продлена до {end_date.strftime('%d.%m.%Y %H:%M')}.")
        
    except ValueError:
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных.", show_alert=True)
        logger.error(f"Ошибка при парсинге user_id из callback_data: {call.data}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка при подтверждении: {e}", show_alert=True)
        logger.error(f"Ошибка при подтверждении причины 'Другая причина': {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_reason_other_'))
def handle_reject_reason_other(call: types.CallbackQuery) -> None:
    """Обработчик отклонения причины 'Не буду платить по другой причине'"""
    # Проверяем, что это админ
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может отклонять.", show_alert=True)
        return
    
    try:
        # Извлекаем user_id из callback_data
        user_id = int(call.data.split('_')[-1])
        
        # Получаем информацию о пользователе
        user_data = get_user_status(user_id)
        if not user_data:
            bot.answer_callback_query(call.id, "Пользователь не найден в базе данных.", show_alert=True)
            return
        
        logger.info(f"Причина 'Другая причина' отклонена для пользователя {user_id}")
        
        # Отправляем уведомление пользователю с кнопкой "Обратная связь"
        first_name = user_data['first_name'] if user_data['first_name'] else 'Пользователь'
        try:
            markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
            feedback_btn = types.KeyboardButton("Обратная связь")
            markup.add(feedback_btn)
            
            bot.send_message(user_id, 
                f"❌ Ваша причина была отклонена, {first_name}.\n\n"
                f"Если у вас есть вопросы, свяжитесь с администратором через форму обратной связи.",
                reply_markup=markup)
        except Exception as e:
            logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
        
        # Обновляем сообщение админу
        bot.answer_callback_query(call.id, "❌ Причина отклонена")
        bot.edit_message_reply_markup(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=None
        )
        bot.send_message(ADMIN_ID, f"❌ Причина 'Другая причина' пользователя {user_id} ({first_name}) отклонена.")
        
    except ValueError:
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных.", show_alert=True)
        logger.error(f"Ошибка при парсинге user_id из callback_data: {call.data}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"Ошибка при отклонении: {e}", show_alert=True)
        logger.error(f"Ошибка при отклонении причины 'Другая причина': {e}")
