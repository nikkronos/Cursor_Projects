"""
Admin handlers for TradeTherapyBot.
Contains all admin-only commands and functions.
"""
from telebot import types
from datetime import datetime
from loader import bot, logger, ADMIN_ID, GROUP_CHAT_ID, GROUP_INVITE_LINK
from database import get_db_connection, parse_db_date, format_db_date, get_users_by_status, DB_FILE
from services import remove_user_from_group, add_subscription_days_logic, remove_subscription_days_logic
from validators import validate_user_id, validate_days, ValidationError
from handlers.helpers import send_admin_menu, send_users_filter_menu


@bot.message_handler(commands=['backup'])
def handle_backup_command(message: types.Message) -> None:
    """Команда для получения бэкапа базы данных"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        with open(DB_FILE, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"Backup от {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Backup sent to admin {message.from_user.id}")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при создании бэкапа.")
        logger.error(f"Error sending backup: {e}")


@bot.message_handler(commands=['admin'])
def handle_admin_command(message: types.Message) -> None:
    """Команда /admin для открытия админского меню"""
    logger.info(f"Admin command requested by {message.from_user.id}")
    if message.from_user.id == ADMIN_ID:
        send_admin_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")


@bot.message_handler(commands=['me'])
def handle_me_command(message: types.Message) -> None:
    """Команда /me для получения своего ID"""
    bot.send_message(message.chat.id, f"Ваш ID: {message.from_user.id}")


@bot.message_handler(func=lambda message: message.text == "⚙️ Админ")
def handle_admin_button(message: types.Message) -> None:
    """Обработчик кнопки '⚙️ Админ'"""
    if message.from_user.id == ADMIN_ID:
        send_admin_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")


@bot.message_handler(func=lambda message: message.text == "🔙 Назад в админку")
def handle_back_to_admin(message: types.Message) -> None:
    """Обработчик кнопки '🔙 Назад в админку'"""
    if message.from_user.id == ADMIN_ID:
        send_admin_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "🕒 Изменить дни")
def handle_manage_days_menu(message: types.Message) -> None:
    """Меню управления днями подписки"""
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
        btn_add = types.KeyboardButton("➕ Добавить дни")
        btn_remove = types.KeyboardButton("➖ Вычесть дни")
        btn_delete = types.KeyboardButton("🗑 Удалить пользователя")
        btn_back = types.KeyboardButton("🔙 Назад в админку")
        markup.add(btn_add, btn_remove, btn_delete, btn_back)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")


@bot.message_handler(func=lambda message: message.text == "➕ Добавить дни")
def handle_add_days_button(message: types.Message) -> None:
    """Обработчик кнопки '➕ Добавить дни'"""
    logger.info(f"Add days requested by {message.from_user.id}")
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton("🔙 Назад в админку"))
        msg = bot.send_message(message.chat.id, "Введите ID пользователя:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_add_days_user_id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")


def process_add_days_user_id(message: types.Message) -> None:
    """Обработка ввода ID пользователя для добавления дней"""
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return
    
    try:
        user_id = validate_user_id(message.text)
        msg = bot.send_message(message.chat.id, f"Введите количество дней для добавления для пользователя {user_id}:")
        bot.register_next_step_handler(msg, process_add_days_amount, user_id)
    except ValidationError as e:
        logger.warning(f"Invalid user_id input from admin {message.from_user.id}: {message.text}. Error: {e}")
        bot.send_message(message.chat.id, f"Некорректный ID пользователя: {e}. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)
    except Exception as e:
        logger.error(f"Unexpected error in process_add_days_user_id: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)


def process_add_days_amount(message: types.Message, user_id: int) -> None:
    """Обработка ввода количества дней для добавления"""
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return

    try:
        days_to_add = validate_days(message.text)
        add_subscription_days_logic(user_id, days_to_add, message.chat.id)
        send_admin_menu(message.chat.id)
    except ValidationError as e:
        logger.warning(f"Invalid days input from admin {message.from_user.id}: {message.text}. Error: {e}")
        bot.send_message(message.chat.id, f"Некорректное количество дней: {e}. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)
    except Exception as e:
        logger.error(f"Unexpected error in process_add_days_amount: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "➖ Вычесть дни")
def handle_remove_days_button(message: types.Message) -> None:
    """Обработчик кнопки '➖ Вычесть дни'"""
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton("🔙 Назад в админку"))
        msg = bot.send_message(message.chat.id, "Введите ID пользователя:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_remove_days_user_id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")


def process_remove_days_user_id(message: types.Message) -> None:
    """Обработка ввода ID пользователя для вычитания дней"""
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return
        
    try:
        user_id = validate_user_id(message.text)
        msg = bot.send_message(message.chat.id, f"Введите количество дней для вычитания для пользователя {user_id}:")
        bot.register_next_step_handler(msg, process_remove_days_amount, user_id)
    except ValidationError as e:
        logger.warning(f"Invalid user_id input from admin {message.from_user.id}: {message.text}. Error: {e}")
        bot.send_message(message.chat.id, f"Некорректный ID пользователя: {e}. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)
    except Exception as e:
        logger.error(f"Unexpected error in process_remove_days_user_id: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)


def process_remove_days_amount(message: types.Message, user_id: int) -> None:
    """Обработка ввода количества дней для вычитания"""
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return

    try:
        days_to_remove = validate_days(message.text)
        remove_subscription_days_logic(user_id, days_to_remove, message.chat.id)
        send_admin_menu(message.chat.id)
    except ValidationError as e:
        logger.warning(f"Invalid days input from admin {message.from_user.id}: {message.text}. Error: {e}")
        bot.send_message(message.chat.id, f"Некорректное количество дней: {e}. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)
    except Exception as e:
        logger.error(f"Unexpected error in process_remove_days_amount: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "🗑 Удалить пользователя")
def handle_delete_user_btn(message: types.Message) -> None:
    """Обработчик кнопки '🗑 Удалить пользователя'"""
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton("🔙 Назад в админку"))
        msg = bot.send_message(message.chat.id, "Введите ID пользователя для удаления:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_delete_user_id)


def process_delete_user_id(message: types.Message) -> None:
    """Обработка ввода ID пользователя для удаления"""
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return
        
    try:
        user_id = validate_user_id(message.text)
        
        now = datetime.now()
        now_str = format_db_date(now)
        
        with get_db_connection() as conn:
            conn.execute("UPDATE users SET subscription_status = 'inactive', subscription_end_date = ?, last_notification_level = 'kicked' WHERE telegram_id = ?", (now_str, user_id))
            conn.commit()
        
        if remove_user_from_group(user_id, GROUP_CHAT_ID):
             bot.send_message(message.chat.id, f"Пользователь {user_id} удален из группы и его подписка аннулирована.")
        else:
             bot.send_message(message.chat.id, f"Подписка пользователя {user_id} аннулирована, но удалить из группы не удалось (возможно, его там нет).")
             
        send_admin_menu(message.chat.id)
        
    except ValidationError as e:
        logger.warning(f"Invalid user_id input from admin {message.from_user.id}: {message.text}. Error: {e}")
        bot.send_message(message.chat.id, f"Некорректный ID: {e}. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)
    except Exception as e:
        logger.error(f"Unexpected error in process_delete_user_id: {e}")
        bot.send_message(message.chat.id, "Произошла ошибка. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)


@bot.message_handler(func=lambda message: message.text == "👥 Все участники")
def handle_all_users_button(message: types.Message) -> None:
    """Обработчик кнопки '👥 Все участники'"""
    logger.info(f"All users requested by {message.from_user.id}")
    if message.from_user.id == ADMIN_ID:
        send_users_filter_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")


@bot.message_handler(func=lambda message: message.text == "✅ Текущие участники")
def handle_active_users(message: types.Message) -> None:
    """Обработчик кнопки '✅ Текущие участники'"""
    if message.from_user.id == ADMIN_ID:
        get_users_by_status(message, 'active')


@bot.message_handler(func=lambda message: message.text == "❌ Бывшие участники")
def handle_inactive_users(message: types.Message) -> None:
    """Обработчик кнопки '❌ Бывшие участники'"""
    if message.from_user.id == ADMIN_ID:
        get_users_by_status(message, 'inactive')


@bot.message_handler(func=lambda message: message.text == "🧾 Чеки и оплаты")
def handle_receipts_main_menu(message: types.Message) -> None:
    """Обработчик кнопки '🧾 Чеки и оплаты'"""
    if message.from_user.id != ADMIN_ID:
        return
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_show_receipts = types.KeyboardButton("👁 Показать чеки")
    btn_clear_receipts = types.KeyboardButton("🗑 Удалить старые чеки")
    btn_back = types.KeyboardButton("🔙 Назад в админку")
    markup.add(btn_show_receipts, btn_clear_receipts, btn_back)
    bot.send_message(message.chat.id, "*Управление чеками:*", parse_mode='Markdown', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "👁 Показать чеки")
def handle_show_receipts(message: types.Message) -> None:
    """Обработчик кнопки '👁 Показать чеки'"""
    if message.from_user.id != ADMIN_ID:
        return
    handle_receipts_menu(message) 


@bot.message_handler(func=lambda message: message.text == "🗑 Удалить старые чеки")
def handle_clear_receipts(message: types.Message) -> None:
    """Обработчик кнопки '🗑 Удалить старые чеки'"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        with get_db_connection() as conn:
            conn.execute("DELETE FROM receipts")
            conn.commit()
        bot.send_message(message.chat.id, "Все записи о чеках удалены из базы данных.")
    except Exception as e:
        logger.error(f"Error clearing receipts: {e}")
        bot.send_message(message.chat.id, "Ошибка при удалении чеков.")


@bot.message_handler(func=lambda message: message.text == "🧾 Чеки")
def handle_receipts_menu(message: types.Message) -> None:
    """Показать последние 10 чеков"""
    if message.from_user.id != ADMIN_ID:
        return

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT r.file_id, r.file_type, r.created_at, u.first_name, u.username, u.telegram_id 
                FROM receipts r 
                JOIN users u ON r.user_id = u.telegram_id 
                ORDER BY r.created_at DESC LIMIT 10
            """)
            receipts = cursor.fetchall()
        
        if receipts:
            for r in receipts:
                file_id = r['file_id']
                file_type = r['file_type']
                created_at = parse_db_date(r['created_at'])
                created_at_str = created_at.strftime('%d.%m.%Y %H:%M') if created_at else "N/A"
                first_name = r['first_name']
                username = r['username']
                uid = r['telegram_id']
                
                caption = f"Чек от: {first_name} (@{username})\nID: {uid}\nДата: {created_at_str}"
                
                try:
                    if file_type == 'photo':
                        bot.send_photo(message.chat.id, file_id, caption=caption)
                    elif file_type == 'document':
                        bot.send_document(message.chat.id, file_id, caption=caption)
                except Exception as e:
                    logger.error(f"Failed to send receipt {file_id}: {e}")
        else:
            bot.send_message(message.chat.id, "Чеков пока нет.")
            
    except Exception as e:
        logger.error(f"Error fetching receipts: {e}")
        bot.send_message(message.chat.id, "Ошибка при загрузке чеков.")


@bot.message_handler(func=lambda message: message.text == "💰 Неподтверждённые оплаты")
def handle_pending_payments(message: types.Message) -> None:
    """Показать неподтвержденные оплаты"""
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT telegram_id, first_name, username FROM users WHERE payment_status = 'pending_review'")
            users = cursor.fetchall()
            
        if users:
            for user in users:
                markup = types.InlineKeyboardMarkup()
                btn_confirm = types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_pay_{user['telegram_id']}")
                btn_reject = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_pay_{user['telegram_id']}")
                markup.add(btn_confirm, btn_reject)
                
                user_info = f"Оплата от: {user['first_name']} (@{user['username']})\nID: {user['telegram_id']}"
                bot.send_message(message.chat.id, user_info, reply_markup=markup)
        else:
            bot.send_message(message.chat.id, "Нет неподтвержденных оплат.")
    except Exception as e:
        logger.error(f"Error fetching pending payments: {e}")
        bot.send_message(message.chat.id, "Ошибка при поиске оплат.")


@bot.message_handler(content_types=['photo'], func=lambda message: message.chat.id == ADMIN_ID)
def get_file_id_admin(message: types.Message) -> None:
    """Получить file_id фотографии (для админа)"""
    file_id = message.photo[-1].file_id
    logger.info(f"ADMIN SENT PHOTO. File_id: {file_id}")
    bot.send_message(message.chat.id, f"File ID этой картинки:\n{file_id}")


# Админские команды через /command
@bot.message_handler(commands=['set_subscription'])
def set_subscription(message: types.Message) -> None:
    """Команда /set_subscription для установки подписки вручную"""
    if message.from_user.id != ADMIN_ID: 
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    args = message.text.split()[1:]
    if len(args) == 5:
        user_id, status, start_date_str, end_date_str, payment_status = args
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d') if start_date_str != 'None' else None
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') if end_date_str != 'None' else None
            
            s_date_db = format_db_date(start_date)
            e_date_db = format_db_date(end_date)

            with get_db_connection() as conn:
                conn.execute("""
                    INSERT INTO users (telegram_id, subscription_status, subscription_start_date, subscription_end_date, payment_status, last_notification_level) VALUES (?, ?, ?, ?, ?, NULL) 
                    ON CONFLICT (telegram_id) 
                    DO UPDATE SET subscription_status = ?, subscription_start_date = ?, subscription_end_date = ?, payment_status = ?, last_notification_level = NULL
                """, (int(user_id), status, s_date_db, e_date_db, payment_status, status, s_date_db, e_date_db, payment_status))
                conn.commit()

            if status == 'active':
                bot.send_message(int(user_id), f"Ваша подписка активирована! Теперь вы можете отправить заявку на вступление в группу по ссылке: {GROUP_INVITE_LINK}. Ваша заявка будет автоматически одобрена.")
                bot.send_message(message.chat.id, f"Пользователю {user_id} активирована подписка. Он получил инструкцию по вступлению в группу.")
            else:
                if remove_user_from_group(int(user_id), GROUP_CHAT_ID):
                    bot.send_message(message.chat.id, f"Пользователь {user_id} удален из группы.")
                else:
                    bot.send_message(message.chat.id, f"Не удалось удалить пользователя {user_id} из группы (возможно, он там и не был).")

            bot.send_message(message.chat.id, f"Статус подписки для пользователя {user_id} обновлен.")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при обновлении статуса подписки: {e}")
            logger.error(f"Error setting subscription: {e}")
    else:
        bot.send_message(message.chat.id, "Использование: /set_subscription <user_id> <status> <start_date(YYYY-MM-DD)> <end_date(YYYY-MM-DD)> <payment_status>")


@bot.message_handler(commands=['get_all_users'])
def get_all_users(message: types.Message) -> None:
    """Команда /get_all_users для получения списка всех пользователей"""
    if message.from_user.id != ADMIN_ID: 
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT telegram_id, first_name, username, subscription_status, subscription_start_date, subscription_end_date, payment_status FROM users")
            users = cursor.fetchall()
            
        if users:
            response = "Список пользователей:\n"
            for user in users:
                start_date = parse_db_date(user['subscription_start_date'])
                end_date = parse_db_date(user['subscription_end_date'])
                
                start_date_str = start_date.strftime('%H:%M:%S %d.%m.%Y') if start_date else 'N/A'
                end_date_str = end_date.strftime('%H:%M:%S %d.%m.%Y') if end_date else 'N/A'
                response += f"ID: {user['telegram_id']}, Имя: {user['first_name']}, Ник: {user['username']}, Статус подписки: {user['subscription_status']}, Начало: {start_date_str}, Конец: {end_date_str}, Оплата: {user['payment_status']}\n"
            bot.send_message(message.chat.id, response)
        else:
            bot.send_message(message.chat.id, "Пользователи не найдены.")
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при получении списка пользователей: {e}")
        logger.error(f"Error getting all users: {e}")


@bot.message_handler(commands=['add_subscription_days'])
def add_subscription_days(message: types.Message) -> None:
    """Команда /add_subscription_days для добавления дней через команду"""
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    args = message.text.split()[1:]
    if len(args) == 2:
        try:
            user_id = validate_user_id(args[0])
            days_to_add = validate_days(args[1])
            add_subscription_days_logic(user_id, days_to_add, message.chat.id)
        except ValidationError as e:
            logger.warning(f"Invalid input in /add_subscription_days from admin {message.from_user.id}: {args}. Error: {e}")
            bot.send_message(message.chat.id, f"Некорректные данные: {e}")
        except Exception as e:
            logger.error(f"Unexpected error in /add_subscription_days: {e}")
            bot.send_message(message.chat.id, "Произошла ошибка при добавлении дней.")
    else:
        bot.send_message(message.chat.id, "Использование: /add_subscription_days <user_id> <количество_дней>")


@bot.message_handler(commands=['remove_subscription_days'])
def remove_subscription_days(message: types.Message) -> None:
    """Команда /remove_subscription_days для удаления дней через команду"""
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    args = message.text.split()[1:]
    if len(args) == 2:
        try:
            user_id = int(args[0])
            days_to_remove = int(args[1])
            remove_subscription_days_logic(user_id, days_to_remove, message.chat.id)
        except ValueError:
            bot.send_message(message.chat.id, "Некорректные данные. ID и дни должны быть числами.")
    else:
        bot.send_message(message.chat.id, "Использование: /remove_subscription_days <user_id> <количество_дней>")


@bot.message_handler(commands=['migrate_all_members'])
def migrate_all_members(message: types.Message) -> None:
    """Команда /migrate_all_members для миграции всех участников группы"""
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return
    
    try:
        bot.send_message(message.chat.id, "Начинаю миграцию участников группы...")
        
        # Получаем всех участников группы
        administrators = bot.get_chat_administrators(GROUP_CHAT_ID)
        member_ids = []
        
        bot.send_message(message.chat.id, "Для миграции всех участников используйте команду /migrate_user <user_id> для каждого участника, или /migrate_user_list для массовой миграции по списку ID.")
        logger.info(f"Admin {message.from_user.id} requested member migration")
        
    except Exception as e:
        bot.send_message(message.chat.id, f"Ошибка при миграции: {e}")
        logger.error(f"Error in migrate_all_members: {e}")


@bot.message_handler(commands=['migrate_user'])
def migrate_single_user(message: types.Message) -> None:
    """Команда /migrate_user для миграции одного участника"""
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return
    
    args = message.text.split()[1:]
    if len(args) == 1:
        try:
            user_id = validate_user_id(args[0])
            
            # Проверяем, есть ли пользователь в группе
            try:
                member = bot.get_chat_member(GROUP_CHAT_ID, user_id)
                if member.status not in ['member', 'administrator', 'creator']:
                    bot.send_message(message.chat.id, f"Пользователь {user_id} не найден в группе или имеет статус: {member.status}")
                    return
            except Exception as e:
                bot.send_message(message.chat.id, f"Не удалось проверить участника в группе: {e}")
                return
            
            # Получаем информацию о пользователе из группы
            try:
                member = bot.get_chat_member(GROUP_CHAT_ID, user_id)
                first_name = member.user.first_name if member.user.first_name else "Unknown"
                username = member.user.username
            except:
                # Если не удалось получить через группу, пробуем через chat
                try:
                    user_chat = bot.get_chat(user_id)
                    first_name = user_chat.first_name if user_chat.first_name else "Unknown"
                    username = user_chat.username
                except:
                    first_name = "Unknown"
                    username = None
            
            # Выдаем подписку до конца месяца
            now = datetime.now()
            if now.month == 12:
                next_month = now.replace(year=now.year+1, month=1, day=1)
            else:
                next_month = now.replace(month=now.month+1, day=1)
            
            end_date = next_month
            now_str = format_db_date(now)
            end_date_str = format_db_date(end_date)
            
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT INTO users (telegram_id, first_name, username, subscription_status, subscription_start_date, subscription_end_date, payment_status, last_notification_level) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, NULL)
                    ON CONFLICT (telegram_id) 
                    DO UPDATE SET subscription_status = 'active', subscription_end_date = ?, payment_status = 'paid', first_name = ?, username = ?, last_notification_level = NULL
                """, (user_id, first_name, username, 'active', now_str, end_date_str, 'paid', end_date_str, first_name, username))
                conn.commit()
            
            bot.send_message(message.chat.id, f"✅ Пользователь {user_id} ({first_name}) получил подписку до {end_date.strftime('%d.%m.%Y')}")
            logger.info(f"User {user_id} migrated with subscription until {end_date}")
            
        except ValueError:
            bot.send_message(message.chat.id, "Некорректный ID пользователя.")
        except Exception as e:
            bot.send_message(message.chat.id, f"Ошибка при миграции пользователя: {e}")
            logger.error(f"Error migrating user: {e}")
    else:
        bot.send_message(message.chat.id, "Использование: /migrate_user <user_id>")
