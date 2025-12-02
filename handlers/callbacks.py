"""
Callback query handlers for TradeTherapyBot.
Handles all inline button callbacks.
"""
from telebot import types
from datetime import datetime
from loader import bot, logger, ADMIN_ID, GROUP_INVITE_LINK
from database import get_db_connection, format_db_date, update_tariff_answers_status
from services import add_subscription_days_logic
from utils import rate_limit


@bot.callback_query_handler(func=lambda call: call.data == 'start_bot')
@rate_limit(max_requests=15, time_window=10.0, block_duration=30.0)
def callback_start_bot(call: types.CallbackQuery) -> None:
    """Обработчик callback кнопки 'Запустить бота'"""
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    
    # Импортируем handle_start внутри функции, чтобы избежать циклических зависимостей
    from handlers.user import handle_start
    
    # Вызываем handle_start логику, чтобы сработала миграция
    msg = types.Message(call.message.message_id, call.message.from_user, call.message.date, call.message.chat, 'text', {}, '/start')
    handle_start(msg)


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_pay_'))
def callback_confirm_payment(call: types.CallbackQuery) -> None:
    """Обработчик подтверждения оплаты администратором"""
    if call.from_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(call.data.split('_')[2])
        
        now = datetime.now()
        if now.month == 12:
            next_month = now.replace(year=now.year+1, month=1, day=1)
        else:
            next_month = now.replace(month=now.month+1, day=1)
        
        new_end_date = next_month
        new_end_date_str = format_db_date(new_end_date)
        
        with get_db_connection() as conn:
            conn.execute("UPDATE users SET subscription_end_date = ?, subscription_status = 'active', payment_status = 'paid', last_notification_level = NULL WHERE telegram_id = ?", (new_end_date_str, user_id))
            conn.commit()
        
        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text="Подписка подтверждена.", reply_markup=None)
        except Exception as e:
            logger.error(f"Failed to edit admin message: {e}")
            bot.send_message(ADMIN_ID, f"Подписка подтверждена.")

        markup_user = types.InlineKeyboardMarkup()
        btn_join = types.InlineKeyboardButton("Вступить в Сообщество", url=GROUP_INVITE_LINK)
        markup_user.add(btn_join)
        
        bot.send_message(user_id, "Подписка активирована.", reply_markup=markup_user)
        
    except Exception as e:
        logger.error(f"Error confirming payment: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при подтверждении: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_pay_'))
def callback_reject_payment(call: types.CallbackQuery) -> None:
    """Обработчик отклонения оплаты администратором"""
    if call.from_user.id != ADMIN_ID:
        return
        
    try:
        user_id = int(call.data.split('_')[2])
        
        with get_db_connection() as conn:
            conn.execute("UPDATE users SET payment_status = 'rejected' WHERE telegram_id = ?", (user_id,))
            conn.commit()
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Оплата пользователя {user_id} отклонена.", reply_markup=None)
        
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn_feedback = types.KeyboardButton("Обратная связь")
        markup.add(btn_feedback)
        
        bot.send_message(user_id, "Администратор отклонил ваше действие. Напишите ваш вопрос, используя кнопку ниже.", reply_markup=markup)

    except Exception as e:
        logger.error(f"Error rejecting payment: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при отклонении: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_tariff_'))
def callback_confirm_tariff(call: types.CallbackQuery) -> None:
    """Обработчик подтверждения ответов на вопросы тарифа"""
    if call.from_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(call.data.split('_')[2])
        
        # Обновляем статус ответов
        update_tariff_answers_status(user_id, 'approved')
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Ответы пользователя {user_id} подтверждены.", reply_markup=None)
        
        # Отправляем пользователю сообщение с реквизитами
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(home_btn)
        
        payment_text = (
            "Ваши ответы были приняты и подтверждены.\n\n"
            "Для оплаты подписки переведите любую сумму на\n\n"
            "Номер телефона: +79213032918 (Т-Банк)\n\n"
            "Или через СБП по этому номеру телефона.\n\n"
            "После оплаты, пожалуйста, отправьте скриншот чека в этот чат для активации подписки."
        )
        
        bot.send_message(user_id, payment_text, reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Error confirming tariff answers: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при подтверждении: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_tariff_'))
def callback_reject_tariff(call: types.CallbackQuery) -> None:
    """Обработчик отклонения ответов на вопросы тарифа"""
    if call.from_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(call.data.split('_')[2])
        
        # Обновляем статус ответов
        update_tariff_answers_status(user_id, 'rejected')
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Ответы пользователя {user_id} отклонены.", reply_markup=None)
        
        # Отправляем пользователю сообщение об отклонении
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(home_btn)
        
        reject_text = (
            "Лидер сообщества отклонил ваш ответ, если хотите узнать подробности, то задайте вопрос в личные сообщения: @nikronos"
        )
        
        bot.send_message(user_id, reject_text, reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Error rejecting tariff answers: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при отклонении: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_reason_trading_'))
def callback_confirm_reason_trading(call: types.CallbackQuery) -> None:
    """Обработчик подтверждения причины 'Я не торгую'"""
    if call.from_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(call.data.split('_')[3])
        
        # Продлеваем подписку на 30 дней
        add_subscription_days_logic(user_id, 30, ADMIN_ID)
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Ответ пользователя {user_id} подтвержден. Подписка продлена на 30 дней.", reply_markup=None)
        
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(home_btn)
        bot.send_message(user_id, "Ваш ответ был принят. Подписка продлена на 30 дней.", reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Error confirming reason trading: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при подтверждении: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_reason_trading_'))
def callback_reject_reason_trading(call: types.CallbackQuery) -> None:
    """Обработчик отклонения причины 'Я не торгую'"""
    if call.from_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(call.data.split('_')[3])
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Ответ пользователя {user_id} отклонен.", reply_markup=None)
        
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(home_btn)
        bot.send_message(user_id, "Лидер сообщества отклонил ваш ответ, если хотите узнать подробности, то задайте вопрос в личные сообщения: @nikronos", reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Error rejecting reason trading: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при отклонении: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_reason_other_'))
def callback_confirm_reason_other(call: types.CallbackQuery) -> None:
    """Обработчик подтверждения другой причины отказа от оплаты"""
    if call.from_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(call.data.split('_')[3])
        
        # Продлеваем подписку на 30 дней
        add_subscription_days_logic(user_id, 30, ADMIN_ID)
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Ответ пользователя {user_id} подтвержден. Подписка продлена на 30 дней.", reply_markup=None)
        
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(home_btn)
        bot.send_message(user_id, "Ваш ответ был принят. Подписка продлена на 30 дней.", reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Error confirming reason other: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при подтверждении: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith('reject_reason_other_'))
def callback_reject_reason_other(call: types.CallbackQuery) -> None:
    """Обработчик отклонения другой причины отказа от оплаты"""
    if call.from_user.id != ADMIN_ID:
        return
    
    try:
        user_id = int(call.data.split('_')[3])
        
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f"Ответ пользователя {user_id} отклонен.", reply_markup=None)
        
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(home_btn)
        bot.send_message(user_id, "Лидер сообщества отклонил ваш ответ, если хотите узнать подробности, то задайте вопрос в личные сообщения: @nikronos", reply_markup=markup)
        
    except Exception as e:
        logger.error(f"Error rejecting reason other: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при отклонении: {e}")
