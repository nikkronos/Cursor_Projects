"""
Callback handlers for TradeTherapyBot.
Contains all callback query handlers for inline buttons.
"""
from telebot import types
from datetime import datetime
from loader import bot, logger, ADMIN_ID, GROUP_CHAT_ID, GROUP_INVITE_LINK
from database import get_db_connection, format_db_date, update_tariff_answers_status, clear_user_tariff_answers
from services import get_next_month_end_date
from utils import safe_send_message, retry_telegram_api


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_pay_') or call.data.startswith('reject_pay_'))
def handle_payment_callback(call: types.CallbackQuery) -> None:
    """Обработчик callback'ов для подтверждения/отклонения оплаты"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может подтверждать оплаты.")
        return
    
    try:
        user_id = int(call.data.split('_')[-1])
        
        if call.data.startswith('confirm_pay_'):
            # Подтверждение оплаты
            now = datetime.now()
            end_date = get_next_month_end_date(now)
            end_date_str = format_db_date(end_date)
            now_str = format_db_date(now)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Проверяем, существует ли пользователь
                cursor.execute("SELECT first_name FROM users WHERE telegram_id = ?", (user_id,))
                user = cursor.fetchone()
                
                if user:
                    cursor.execute("""
                        UPDATE users 
                        SET subscription_status = 'active', 
                            subscription_end_date = ?, 
                            payment_status = 'paid',
                            subscription_start_date = ?,
                            last_notification_level = NULL
                        WHERE telegram_id = ?
                    """, (end_date_str, now_str, user_id))
                else:
                    # Если пользователя нет, создаем его
                    cursor.execute("""
                        INSERT INTO users (telegram_id, subscription_status, subscription_start_date, 
                                         subscription_end_date, payment_status, last_notification_level)
                        VALUES (?, 'active', ?, ?, 'paid', NULL)
                    """, (user_id, now_str, end_date_str))
                
                conn.commit()
            
            # Отправляем уведомление пользователю
            try:
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                back_button = types.KeyboardButton("Вернуться в главное меню🏡")
                markup.add(back_button)
                
                safe_send_message(bot, user_id, 
                    f"✅ Ваша оплата подтверждена! Подписка продлена до {end_date.strftime('%d.%m.%Y')} до 23:00.",
                    reply_markup=markup)
                
                # Проверяем, в группе ли пользователь
                try:
                    def get_member():
                        return bot.get_chat_member(GROUP_CHAT_ID, user_id)
                    member = retry_telegram_api(get_member, max_attempts=2)
                    if member.status not in ['creator', 'administrator', 'member']:
                        safe_send_message(bot, user_id, 
                            f"Теперь вы можете вступить в группу по ссылке: {GROUP_INVITE_LINK}")
                except Exception:
                    safe_send_message(bot, user_id, 
                        f"Теперь вы можете вступить в группу по ссылке: {GROUP_INVITE_LINK}")
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Уведомление админу
            safe_send_message(bot, ADMIN_ID, 
                f"✅ Оплата пользователя {user_id} подтверждена. Подписка до {end_date.strftime('%d.%m.%Y')} 23:00.")
            
            bot.answer_callback_query(call.id, "Оплата подтверждена")
            
        elif call.data.startswith('reject_pay_'):
            # Отклонение оплаты
            with get_db_connection() as conn:
                conn.execute("UPDATE users SET payment_status = 'rejected' WHERE telegram_id = ?", (user_id,))
                conn.commit()
            
            # Уведомление пользователю
            try:
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                feedback_button = types.KeyboardButton("Обратная связь")
                markup.add(feedback_button)
                
                safe_send_message(bot, user_id, 
                    "❌ Ваша оплата была отклонена. Пожалуйста, свяжитесь с администратором для уточнения.",
                    reply_markup=markup)
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Уведомление админу
            safe_send_message(bot, ADMIN_ID, f"❌ Оплата пользователя {user_id} отклонена.")
            
            bot.answer_callback_query(call.id, "Оплата отклонена")
            
    except ValueError:
        logger.error(f"Неверный формат user_id в callback: {call.data}")
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных")
    except Exception as e:
        logger.error(f"Ошибка при обработке callback оплаты: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_tariff_') or call.data.startswith('reject_tariff_'))
def handle_tariff_callback(call: types.CallbackQuery) -> None:
    """Обработчик callback'ов для подтверждения/отклонения ответов на вопросы тарифа"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может подтверждать ответы.")
        return
    
    try:
        user_id = int(call.data.split('_')[-1])
        
        if call.data.startswith('confirm_tariff_'):
            # Подтверждение ответов на вопросы
            now = datetime.now()
            end_date = get_next_month_end_date(now)
            end_date_str = format_db_date(end_date)
            now_str = format_db_date(now)
            
            # Обновляем статус ответов
            update_tariff_answers_status(user_id, 'approved')
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Проверяем, существует ли пользователь
                cursor.execute("SELECT first_name FROM users WHERE telegram_id = ?", (user_id,))
                user = cursor.fetchone()
                
                if user:
                    cursor.execute("""
                        UPDATE users 
                        SET subscription_status = 'active', 
                            subscription_end_date = ?, 
                            subscription_start_date = ?,
                            payment_status = 'paid',
                            last_notification_level = NULL
                        WHERE telegram_id = ?
                    """, (end_date_str, now_str, user_id))
                else:
                    # Если пользователя нет, создаем его
                    cursor.execute("""
                        INSERT INTO users (telegram_id, subscription_status, subscription_start_date, 
                                         subscription_end_date, payment_status, last_notification_level)
                        VALUES (?, 'active', ?, ?, 'paid', NULL)
                    """, (user_id, now_str, end_date_str))
                
                conn.commit()
            
            # Отправляем уведомление пользователю
            try:
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                back_button = types.KeyboardButton("Вернуться в главное меню🏡")
                markup.add(back_button)
                
                safe_send_message(bot, user_id, 
                    f"✅ Ваши ответы подтверждены! Подписка активирована до {end_date.strftime('%d.%m.%Y')} до 23:00.",
                    reply_markup=markup)
                
                # Проверяем, в группе ли пользователь
                try:
                    def get_member():
                        return bot.get_chat_member(GROUP_CHAT_ID, user_id)
                    member = retry_telegram_api(get_member, max_attempts=2)
                    if member.status not in ['creator', 'administrator', 'member']:
                        safe_send_message(bot, user_id, 
                            f"Теперь вы можете вступить в группу по ссылке: {GROUP_INVITE_LINK}")
                except Exception:
                    safe_send_message(bot, user_id, 
                        f"Теперь вы можете вступить в группу по ссылке: {GROUP_INVITE_LINK}")
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Уведомление админу
            safe_send_message(bot, ADMIN_ID, 
                f"✅ Ответы пользователя {user_id} подтверждены. Подписка до {end_date.strftime('%d.%m.%Y')} 23:00.")
            
            bot.answer_callback_query(call.id, "Ответы подтверждены")
            
        elif call.data.startswith('reject_tariff_'):
            # Отклонение ответов
            update_tariff_answers_status(user_id, 'rejected')
            
            # Уведомление пользователю
            try:
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                feedback_button = types.KeyboardButton("Обратная связь")
                markup.add(feedback_button)
                
                safe_send_message(bot, user_id, 
                    "❌ Ваши ответы были отклонены. Пожалуйста, свяжитесь с администратором для уточнения.",
                    reply_markup=markup)
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Уведомление админу
            safe_send_message(bot, ADMIN_ID, f"❌ Ответы пользователя {user_id} отклонены.")
            
            bot.answer_callback_query(call.id, "Ответы отклонены")
            
    except ValueError:
        logger.error(f"Неверный формат user_id в callback: {call.data}")
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных")
    except Exception as e:
        logger.error(f"Ошибка при обработке callback тарифа: {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_reason_trading_') or call.data.startswith('reject_reason_trading_'))
def handle_reason_trading_callback(call: types.CallbackQuery) -> None:
    """Обработчик callback'ов для подтверждения/отклонения причины 'Я не торгую'"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может подтверждать причины.")
        return
    
    try:
        user_id = int(call.data.split('_')[-1])
        
        if call.data.startswith('confirm_reason_trading_'):
            # Подтверждение причины "Я не торгую"
            now = datetime.now()
            end_date = get_next_month_end_date(now)
            end_date_str = format_db_date(end_date)
            now_str = format_db_date(now)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Проверяем, существует ли пользователь
                cursor.execute("SELECT first_name FROM users WHERE telegram_id = ?", (user_id,))
                user = cursor.fetchone()
                
                if user:
                    cursor.execute("""
                        UPDATE users 
                        SET subscription_status = 'active', 
                            subscription_end_date = ?, 
                            subscription_start_date = ?,
                            payment_status = 'paid',
                            last_notification_level = NULL
                        WHERE telegram_id = ?
                    """, (end_date_str, now_str, user_id))
                else:
                    # Если пользователя нет, создаем его
                    cursor.execute("""
                        INSERT INTO users (telegram_id, subscription_status, subscription_start_date, 
                                         subscription_end_date, payment_status, last_notification_level)
                        VALUES (?, 'active', ?, ?, 'paid', NULL)
                    """, (user_id, now_str, end_date_str))
                
                conn.commit()
            
            # Отправляем уведомление пользователю
            try:
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                back_button = types.KeyboardButton("Вернуться в главное меню🏡")
                markup.add(back_button)
                
                safe_send_message(bot, user_id, 
                    f"✅ Ваша причина подтверждена! Подписка активирована до {end_date.strftime('%d.%m.%Y')} до 23:00.",
                    reply_markup=markup)
                
                # Проверяем, в группе ли пользователь
                try:
                    def get_member():
                        return bot.get_chat_member(GROUP_CHAT_ID, user_id)
                    member = retry_telegram_api(get_member, max_attempts=2)
                    if member.status not in ['creator', 'administrator', 'member']:
                        safe_send_message(bot, user_id, 
                            f"Теперь вы можете вступить в группу по ссылке: {GROUP_INVITE_LINK}")
                except Exception:
                    safe_send_message(bot, user_id, 
                        f"Теперь вы можете вступить в группу по ссылке: {GROUP_INVITE_LINK}")
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Уведомление админу
            safe_send_message(bot, ADMIN_ID, 
                f"✅ Причина пользователя {user_id} ('Я не торгую') подтверждена. Подписка до {end_date.strftime('%d.%m.%Y')} 23:00.")
            
            bot.answer_callback_query(call.id, "Причина подтверждена")
            
        elif call.data.startswith('reject_reason_trading_'):
            # Отклонение причины
            # Уведомление пользователю
            try:
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                feedback_button = types.KeyboardButton("Обратная связь")
                markup.add(feedback_button)
                
                safe_send_message(bot, user_id, 
                    "❌ Ваша причина была отклонена. Пожалуйста, свяжитесь с администратором для уточнения.",
                    reply_markup=markup)
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Уведомление админу
            safe_send_message(bot, ADMIN_ID, f"❌ Причина пользователя {user_id} ('Я не торгую') отклонена.")
            
            bot.answer_callback_query(call.id, "Причина отклонена")
            
    except ValueError:
        logger.error(f"Неверный формат user_id в callback: {call.data}")
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных")
    except Exception as e:
        logger.error(f"Ошибка при обработке callback причины 'Я не торгую': {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_reason_other_') or call.data.startswith('reject_reason_other_'))
def handle_reason_other_callback(call: types.CallbackQuery) -> None:
    """Обработчик callback'ов для подтверждения/отклонения причины 'По другой причине'"""
    if call.from_user.id != ADMIN_ID:
        bot.answer_callback_query(call.id, "Только администратор может подтверждать причины.")
        return
    
    try:
        user_id = int(call.data.split('_')[-1])
        
        if call.data.startswith('confirm_reason_other_'):
            # Подтверждение причины "По другой причине"
            now = datetime.now()
            end_date = get_next_month_end_date(now)
            end_date_str = format_db_date(end_date)
            now_str = format_db_date(now)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                # Проверяем, существует ли пользователь
                cursor.execute("SELECT first_name FROM users WHERE telegram_id = ?", (user_id,))
                user = cursor.fetchone()
                
                if user:
                    cursor.execute("""
                        UPDATE users 
                        SET subscription_status = 'active', 
                            subscription_end_date = ?, 
                            subscription_start_date = ?,
                            payment_status = 'paid',
                            last_notification_level = NULL
                        WHERE telegram_id = ?
                    """, (end_date_str, now_str, user_id))
                else:
                    # Если пользователя нет, создаем его
                    cursor.execute("""
                        INSERT INTO users (telegram_id, subscription_status, subscription_start_date, 
                                         subscription_end_date, payment_status, last_notification_level)
                        VALUES (?, 'active', ?, ?, 'paid', NULL)
                    """, (user_id, now_str, end_date_str))
                
                conn.commit()
            
            # Отправляем уведомление пользователю
            try:
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                back_button = types.KeyboardButton("Вернуться в главное меню🏡")
                markup.add(back_button)
                
                safe_send_message(bot, user_id, 
                    f"✅ Ваша причина подтверждена! Подписка активирована до {end_date.strftime('%d.%m.%Y')} до 23:00.",
                    reply_markup=markup)
                
                # Проверяем, в группе ли пользователь
                try:
                    def get_member():
                        return bot.get_chat_member(GROUP_CHAT_ID, user_id)
                    member = retry_telegram_api(get_member, max_attempts=2)
                    if member.status not in ['creator', 'administrator', 'member']:
                        safe_send_message(bot, user_id, 
                            f"Теперь вы можете вступить в группу по ссылке: {GROUP_INVITE_LINK}")
                except Exception:
                    safe_send_message(bot, user_id, 
                        f"Теперь вы можете вступить в группу по ссылке: {GROUP_INVITE_LINK}")
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Уведомление админу
            safe_send_message(bot, ADMIN_ID, 
                f"✅ Причина пользователя {user_id} ('По другой причине') подтверждена. Подписка до {end_date.strftime('%d.%m.%Y')} 23:00.")
            
            bot.answer_callback_query(call.id, "Причина подтверждена")
            
        elif call.data.startswith('reject_reason_other_'):
            # Отклонение причины
            # Уведомление пользователю
            try:
                markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
                feedback_button = types.KeyboardButton("Обратная связь")
                markup.add(feedback_button)
                
                safe_send_message(bot, user_id, 
                    "❌ Ваша причина была отклонена. Пожалуйста, свяжитесь с администратором для уточнения.",
                    reply_markup=markup)
            except Exception as e:
                logger.error(f"Не удалось отправить уведомление пользователю {user_id}: {e}")
            
            # Уведомление админу
            safe_send_message(bot, ADMIN_ID, f"❌ Причина пользователя {user_id} ('По другой причине') отклонена.")
            
            bot.answer_callback_query(call.id, "Причина отклонена")
            
    except ValueError:
        logger.error(f"Неверный формат user_id в callback: {call.data}")
        bot.answer_callback_query(call.id, "Ошибка: неверный формат данных")
    except Exception as e:
        logger.error(f"Ошибка при обработке callback причины 'По другой причине': {e}")
        bot.answer_callback_query(call.id, "Произошла ошибка")
