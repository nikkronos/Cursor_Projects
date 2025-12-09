"""
Admin handlers for TradeTherapyBot.
Contains admin-only commands and functions.
"""
from telebot import types
from datetime import datetime
from loader import bot, logger, ADMIN_ID, GROUP_CHAT_ID
from database import get_db_connection, format_db_date
from utils import retry_telegram_api
from handlers.helpers import send_admin_menu, send_users_filter_menu
from database import get_users_by_status, get_all_users_for_check
from services import add_subscription_days_logic, remove_subscription_days_logic, remove_user_from_group
from validators import validate_user_id, validate_days


@bot.message_handler(commands=['admin'])
def handle_admin_command(message: types.Message) -> None:
    """Обработчик команды /admin"""
    if message.from_user.id != ADMIN_ID:
        return
    send_admin_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "⚙️ Админ")
def handle_admin_button(message: types.Message) -> None:
    """Обработчик кнопки '⚙️ Админ'"""
    if message.from_user.id != ADMIN_ID:
        return
    send_admin_menu(message.chat.id)


@bot.message_handler(commands=['migrate_user', 'update_user'])
def handle_migrate_user(message: types.Message) -> None:
    """Команда для выдачи подписки существующим участникам группы или обновления данных пользователя"""
    if message.from_user.id != ADMIN_ID:
        return
    
    # Парсим user_id из аргументов команды
    command_parts = message.text.split()
    if len(command_parts) < 2:
        bot.send_message(ADMIN_ID, "Использование: /migrate_user <user_id> или /update_user <user_id>")
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
    
    # Проверяем, существует ли пользователь в БД
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT subscription_end_date FROM users WHERE telegram_id = ?", (user_id,))
        existing_user = cursor.fetchone()
    
    # Если команда /update_user и пользователь существует - только обновляем данные
    if command_parts[0] == '/update_user' and existing_user:
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
            
            username_str = f"@{username}" if username else "нет username"
            response = (
                f"Данные пользователя обновлены:\n\n"
                f"ID: {user_id}\n"
                f"Имя: {first_name}\n"
                f"Username: {username_str}"
            )
            bot.send_message(ADMIN_ID, response)
            return
        except Exception as e:
            error_msg = f"Ошибка при обновлении данных пользователя {user_id}: {e}"
            logger.error(error_msg)
            bot.send_message(ADMIN_ID, error_msg)
            return
    
    # Для /migrate_user - добавляем/обновляем пользователя в БД с подпиской до конца месяца
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


@bot.message_handler(func=lambda message: message.text == "🕒 Изменить дни")
def handle_manage_days_menu(message: types.Message) -> None:
    """Обработчик кнопки '🕒 Изменить дни'"""
    if message.from_user.id != ADMIN_ID:
        return
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_add = types.KeyboardButton("➕ Добавить дни")
    btn_remove = types.KeyboardButton("➖ Вычесть дни")
    btn_delete = types.KeyboardButton("🗑 Удалить участника")
    btn_back = types.KeyboardButton("🔙 Назад в админку")
    markup.add(btn_add, btn_remove, btn_delete, btn_back)
    bot.send_message(ADMIN_ID, "Выберите действие:", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "👥 Все участники")
def handle_all_users_button(message: types.Message) -> None:
    """Обработчик кнопки '👥 Все участники'"""
    if message.from_user.id != ADMIN_ID:
        return
    send_users_filter_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "✅ Текущие участники")
def handle_active_users_button(message: types.Message) -> None:
    """Обработчик кнопки '✅ Текущие участники'"""
    if message.from_user.id != ADMIN_ID:
        return
    get_users_by_status(message, 'active')


@bot.message_handler(func=lambda message: message.text == "❌ Бывшие участники")
def handle_inactive_users_button(message: types.Message) -> None:
    """Обработчик кнопки '❌ Бывшие участники'"""
    if message.from_user.id != ADMIN_ID:
        return
    get_users_by_status(message, 'inactive')


@bot.message_handler(func=lambda message: message.text == "💰 Неподтверждённые оплаты")
def handle_pending_payments_button(message: types.Message) -> None:
    """Обработчик кнопки '💰 Неподтверждённые оплаты'"""
    if message.from_user.id != ADMIN_ID:
        return
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.telegram_id, u.first_name, u.username, r.file_id, r.file_type, r.created_at
                FROM receipts r
                JOIN users u ON r.user_id = u.telegram_id
                WHERE u.payment_status = 'pending_review'
                ORDER BY r.created_at DESC
                LIMIT 20
            """)
            receipts = cursor.fetchall()
        
        if receipts:
            for receipt in receipts:
                user_id = receipt['telegram_id']
                first_name = receipt['first_name'] or 'Unknown'
                username = receipt['username'] or 'нет username'
                file_id = receipt['file_id']
                file_type = receipt['file_type']
                
                markup = types.InlineKeyboardMarkup()
                btn_confirm = types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_pay_{user_id}")
                btn_reject = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_pay_{user_id}")
                markup.add(btn_confirm, btn_reject)
                
                if file_type == 'photo':
                    bot.send_photo(ADMIN_ID, file_id, 
                                 caption=f"Чек от {first_name} (@{username if username != 'нет username' else 'N/A'})",
                                 reply_markup=markup)
                else:
                    bot.send_document(ADMIN_ID, file_id,
                                    caption=f"Чек от {first_name} (@{username if username != 'нет username' else 'N/A'})",
                                    reply_markup=markup)
        else:
            bot.send_message(ADMIN_ID, "Нет неподтверждённых оплат.")
    except Exception as e:
        logger.error(f"Error getting pending payments: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при получении неподтверждённых оплат: {e}")


@bot.message_handler(func=lambda message: message.text == "🧾 Чеки и оплаты")
def handle_receipts_menu_button(message: types.Message) -> None:
    """Обработчик кнопки '🧾 Чеки и оплаты'"""
    if message.from_user.id != ADMIN_ID:
        return
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count FROM receipts
            """)
            total = cursor.fetchone()['count']
        
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn_show = types.KeyboardButton("👁 Показать чеки")
        btn_delete_old = types.KeyboardButton("🗑 Удалить старые чеки (30+ дней)")
        btn_delete_all = types.KeyboardButton("🗑 Удалить все чеки")
        btn_back = types.KeyboardButton("⬅️ Главное меню")
        markup.add(btn_show, btn_delete_old, btn_delete_all, btn_back)
        
        bot.send_message(ADMIN_ID, f"Всего чеков в базе: {total}", reply_markup=markup)
    except Exception as e:
        logger.error(f"Error in receipts menu: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка: {e}")


@bot.message_handler(func=lambda message: message.text == "👁 Показать чеки")
def handle_show_receipts_button(message: types.Message) -> None:
    """Обработчик кнопки '👁 Показать чеки'"""
    if message.from_user.id != ADMIN_ID:
        return
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT u.telegram_id, u.first_name, u.username, r.file_id, r.file_type, r.created_at
                FROM receipts r
                JOIN users u ON r.user_id = u.telegram_id
                ORDER BY r.created_at DESC
                LIMIT 10
            """)
            receipts = cursor.fetchall()
        
        if receipts:
            for receipt in receipts:
                user_id = receipt['telegram_id']
                first_name = receipt['first_name'] or 'Unknown'
                username = receipt['username'] or 'нет username'
                file_id = receipt['file_id']
                file_type = receipt['file_type']
                created_at = receipt['created_at']
                
                if file_type == 'photo':
                    bot.send_photo(ADMIN_ID, file_id, 
                                 caption=f"Чек от {first_name} (@{username if username != 'нет username' else 'N/A'})\nДата: {created_at}")
                else:
                    bot.send_document(ADMIN_ID, file_id,
                                    caption=f"Чек от {first_name} (@{username if username != 'нет username' else 'N/A'})\nДата: {created_at}")
        else:
            bot.send_message(ADMIN_ID, "Нет чеков в базе.")
    except Exception as e:
        logger.error(f"Error showing receipts: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка при показе чеков: {e}")


@bot.message_handler(func=lambda message: message.text == "🗑 Удалить старые чеки (30+ дней)")
def handle_delete_old_receipts_button(message: types.Message) -> None:
    """Обработчик кнопки '🗑 Удалить старые чеки (30+ дней)'"""
    if message.from_user.id != ADMIN_ID:
        return
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Удаляем чеки старше 30 дней
            cursor.execute("""
                DELETE FROM receipts 
                WHERE datetime(created_at) < datetime('now', '-30 days')
            """)
            deleted = cursor.rowcount
            conn.commit()
            
            logger.info(f"Deleted {deleted} old receipts (30+ days)")
        
        bot.send_message(ADMIN_ID, f"Удалено старых чеков (30+ дней): {deleted}")
        send_admin_menu(ADMIN_ID)
    except Exception as e:
        logger.error(f"Error deleting old receipts: {e}", exc_info=True)
        bot.send_message(ADMIN_ID, f"Ошибка при удалении чеков: {e}")


@bot.message_handler(func=lambda message: message.text == "🗑 Удалить все чеки")
def handle_delete_all_receipts_button(message: types.Message) -> None:
    """Обработчик кнопки '🗑 Удалить все чеки'"""
    if message.from_user.id != ADMIN_ID:
        return
    
    # Запрашиваем подтверждение
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_confirm = types.KeyboardButton("✅ Да, удалить все")
    btn_cancel = types.KeyboardButton("❌ Отмена")
    markup.add(btn_confirm, btn_cancel)
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) as count FROM receipts")
            total = cursor.fetchone()['count']
        
        bot.send_message(ADMIN_ID, f"⚠️ Внимание! Вы собираетесь удалить ВСЕ чеки ({total} шт.).\n\nПодтвердите действие:", reply_markup=markup)
        bot.register_next_step_handler(message, process_delete_all_receipts_confirmation)
    except Exception as e:
        logger.error(f"Error in delete all receipts: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка: {e}")


def process_delete_all_receipts_confirmation(message: types.Message) -> None:
    """Обработка подтверждения удаления всех чеков"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "✅ Да, удалить все":
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM receipts")
                deleted = cursor.rowcount
                conn.commit()
            
            logger.info(f"Deleted all receipts: {deleted}")
            bot.send_message(ADMIN_ID, f"✅ Удалено всех чеков: {deleted}")
            send_admin_menu(ADMIN_ID)
        except Exception as e:
            logger.error(f"Error deleting all receipts: {e}", exc_info=True)
            bot.send_message(ADMIN_ID, f"Ошибка при удалении чеков: {e}")
            send_admin_menu(ADMIN_ID)
    elif message.text == "❌ Отмена":
        bot.send_message(ADMIN_ID, "❌ Удаление отменено.")
        send_admin_menu(ADMIN_ID)
    else:
        bot.send_message(ADMIN_ID, "Используйте кнопки для подтверждения или отмены.")
        send_admin_menu(ADMIN_ID)


@bot.message_handler(func=lambda message: message.text == "➕ Добавить дни")
def handle_add_days_button(message: types.Message) -> None:
    """Обработчик кнопки '➕ Добавить дни'"""
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(ADMIN_ID, "Введите ID пользователя и количество дней через пробел:\nНапример: 123456789 30")
    bot.register_next_step_handler(msg, process_add_days)


def process_add_days(message: types.Message) -> None:
    """Обработка добавления дней"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Назад в админку":
        send_admin_menu(ADMIN_ID)
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(ADMIN_ID, "Неверный формат. Введите: <user_id> <days>")
            return
        
        user_id = validate_user_id(parts[0])
        days = validate_days(parts[1])
        
        add_subscription_days_logic(user_id, days, ADMIN_ID)
    except Exception as e:
        logger.error(f"Error in process_add_days: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка: {e}")


@bot.message_handler(func=lambda message: message.text == "➖ Вычесть дни")
def handle_remove_days_button(message: types.Message) -> None:
    """Обработчик кнопки '➖ Вычесть дни'"""
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(ADMIN_ID, "Введите ID пользователя и количество дней через пробел:\nНапример: 123456789 7")
    bot.register_next_step_handler(msg, process_remove_days)


def process_remove_days(message: types.Message) -> None:
    """Обработка вычитания дней"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Назад в админку":
        send_admin_menu(ADMIN_ID)
        return
    
    try:
        parts = message.text.split()
        if len(parts) != 2:
            bot.send_message(ADMIN_ID, "Неверный формат. Введите: <user_id> <days>")
            return
        
        user_id = validate_user_id(parts[0])
        days = validate_days(parts[1])
        
        remove_subscription_days_logic(user_id, days, ADMIN_ID)
    except Exception as e:
        logger.error(f"Error in process_remove_days: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка: {e}")


@bot.message_handler(func=lambda message: message.text == "🗑 Удалить участника")
def handle_delete_user_button(message: types.Message) -> None:
    """Обработчик кнопки '🗑 Удалить участника'"""
    if message.from_user.id != ADMIN_ID:
        return
    msg = bot.send_message(ADMIN_ID, "Введите ID пользователя для удаления:")
    bot.register_next_step_handler(msg, process_delete_user)


def process_delete_user(message: types.Message) -> None:
    """Обработка удаления пользователя"""
    if message.from_user.id != ADMIN_ID:
        return
    
    if message.text == "🔙 Назад в админку":
        send_admin_menu(ADMIN_ID)
        return
    
    try:
        user_id = validate_user_id(message.text)
        
        # Удаляем из группы
        if GROUP_CHAT_ID:
            remove_user_from_group(user_id, GROUP_CHAT_ID)
        
        # Удаляем из БД
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE telegram_id = ?", (user_id,))
            cursor.execute("DELETE FROM receipts WHERE user_id = ?", (user_id,))
            cursor.execute("DELETE FROM tariff_answers WHERE user_id = ?", (user_id,))
            conn.commit()
        
        bot.send_message(ADMIN_ID, f"Пользователь {user_id} удален из базы данных и группы.")
        send_admin_menu(ADMIN_ID)
    except Exception as e:
        logger.error(f"Error in process_delete_user: {e}")
        bot.send_message(ADMIN_ID, f"Ошибка: {e}")


@bot.message_handler(func=lambda message: message.text == "🔙 Назад в админку")
def handle_back_to_admin_menu(message: types.Message) -> None:
    """Обработчик кнопки '🔙 Назад в админку'"""
    if message.from_user.id != ADMIN_ID:
        return
    send_admin_menu(message.chat.id)
