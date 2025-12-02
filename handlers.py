from telebot import types
from datetime import datetime
from loader import bot, logger, ADMIN_ID, GROUP_CHAT_ID, GROUP_INVITE_LINK
from database import get_db_connection, parse_db_date, format_db_date, get_user_status, get_users_by_status, DB_FILE
from services import remove_user_from_group, add_subscription_days_logic, remove_subscription_days_logic

# --- Helper Handlers ---
def send_initial_welcome(message):
    markup = types.InlineKeyboardMarkup()
    start_button = types.InlineKeyboardButton("Запустить бота", callback_data='start_bot')
    markup.add(start_button)
    bot.send_message(message.chat.id, 
                     f"👋 Добро пожаловать в чат-бот Сообщества *Trade Therapy*\n\n" 
                     "Здесь вы сможете получить доступ к Сообществу следуя инструкциям.\n\n" 
                     "Для начала нажмите кнопку \"Запустить бота\"",
                     parse_mode='Markdown',
                     reply_markup=markup)

def send_main_menu(user_id, chat_id, first_name):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn1 = types.KeyboardButton("Тарифы")
    btn2 = types.KeyboardButton("Правила Клуба")
    btn3 = types.KeyboardButton("О Нас")
    btn4 = types.KeyboardButton("Обратная связь")
    btn5 = types.KeyboardButton("Статус подписки")
    btn6 = types.KeyboardButton("Отзывы")
    btn7 = types.KeyboardButton("Публичная оферта")
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7)
    
    if user_id == ADMIN_ID:
        btn_admin = types.KeyboardButton("⚙️ Админ")
        markup.add(btn_admin)

    bot.send_message(chat_id, 
                     f"Здравствуйте, {first_name} !\n\n" 
                     f"Добро пожаловать в бот платной подписки в Сообщество *Trade Therapy*.\n\n" 
                     "Тарифы — ознакомиться с тарифами и получить доступ к нашей закрытой группе\n" 
                     "О Нас — ознакомиться с информацией о нашем закрытом сообществе\n" 
                     "Статус подписки — узнать статус действующей подписки\n" 
                     "Обратная связь — если не нашли ответ на ваш вопрос\n" 
                     "Публичная оферта — ознакомиться с юридической стороной",
                     parse_mode='Markdown',
                     reply_markup=markup)

def send_admin_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_manage_days = types.KeyboardButton("🕒 Изменить дни")
    btn_all_users = types.KeyboardButton("👥 Все участники")
    btn_pending = types.KeyboardButton("💰 Неподтверждённые оплаты")
    btn_receipts = types.KeyboardButton("🧾 Чеки и оплаты")
    btn_back_to_main = types.KeyboardButton("⬅️ Главное меню")
    markup.add(btn_manage_days, btn_all_users, btn_pending, btn_receipts, btn_back_to_main)
    bot.send_message(chat_id, "*Административное меню:*", parse_mode='Markdown', reply_markup=markup)

def send_users_filter_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_active = types.KeyboardButton("✅ Текущие участники")
    btn_inactive = types.KeyboardButton("❌ Бывшие участники")
    btn_back = types.KeyboardButton("🔙 Назад в админку")
    markup.add(btn_active, btn_inactive, btn_back)
    bot.send_message(chat_id, "Какие участники вас интересуют?", reply_markup=markup)

def send_payment_info(message, amount):
    user_id = message.from_user.id
    user_data = get_user_status(user_id)
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    
    if user_data and user_data['subscription_status'] == 'active':
        wont_pay = types.KeyboardButton("Не буду платить")
        markup.add(wont_pay)
        
    restart_btn = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(restart_btn)
    
    bot.send_message(message.chat.id,
                     f"Для оплаты подписки переведите сумму {amount} руб. на \n\n" 
                     "Номер телефона: +79213032918 (Т-Банк)\n\n" 
                     "Или через СБП по этому номеру телефона.\n\n" 
                     "После оплаты, пожалуйста, отправьте скриншот чека в этот чат для активации подписки.",
                     reply_markup=markup)

# --- Handlers ---

@bot.chat_join_request_handler()
def handle_join_request(join_request):
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id
    user_data = get_user_status(user_id)

    if user_data and user_data['subscription_status'] == 'active': 
        bot.approve_chat_join_request(chat_id, user_id)
        bot.send_message(user_id, f"Ваша заявка на вступление в группу одобрена! Добро пожаловать.")
        logger.info(f"Заявка пользователя {user_id} в группу {chat_id} одобрена.")
    else:
        bot.decline_chat_join_request(chat_id, user_id)
        bot.send_message(user_id, f"Ваша заявка на вступление в группу отклонена, так как у вас нет активной подписки. Пожалуйста, продлите ее через бота.")
        logger.info(f"Заявка пользователя {user_id} в группу {chat_id} отклонена (нет активной подписки).")

@bot.message_handler(commands=['backup'])
def handle_backup_command(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    try:
        with open(DB_FILE, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"Backup от {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info(f"Backup sent to admin {message.from_user.id}")
    except Exception as e:
        bot.send_message(message.chat.id, "Ошибка при создании бэкапа.")
        logger.error(f"Error sending backup: {e}")

@bot.message_handler(func=lambda message: message.text == "🧾 Чеки и оплаты")
def handle_receipts_main_menu(message):
    if message.from_user.id != ADMIN_ID:
        return
    
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_show_receipts = types.KeyboardButton("👁 Показать чеки")
    btn_clear_receipts = types.KeyboardButton("🗑 Удалить старые чеки")
    btn_back = types.KeyboardButton("🔙 Назад в админку")
    markup.add(btn_show_receipts, btn_clear_receipts, btn_back)
    bot.send_message(message.chat.id, "*Управление чеками:*", parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "👁 Показать чеки")
def handle_show_receipts(message):
    if message.from_user.id != ADMIN_ID:
        return
    handle_receipts_menu(message) 

@bot.message_handler(func=lambda message: message.text == "🗑 Удалить старые чеки")
def handle_clear_receipts(message):
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

@bot.message_handler(func=lambda message: message.text == "🕒 Изменить дни")
def handle_manage_days_menu(message):
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

@bot.message_handler(commands=['admin'])
def handle_admin_command(message):
    logger.info(f"Admin command requested by {message.from_user.id}")
    if message.from_user.id == ADMIN_ID:
        send_admin_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")

@bot.message_handler(commands=['me'])
def handle_me_command(message):
    bot.send_message(message.chat.id, f"Ваш ID: {message.from_user.id}")

@bot.message_handler(func=lambda message: message.text == "⬅️ Главное меню")
def handle_back_to_main_menu(message):
    logger.info(f"Back to main menu requested by {message.from_user.id}")
    send_main_menu(message.from_user.id, message.chat.id, message.from_user.first_name)

@bot.message_handler(func=lambda message: message.text == "👥 Все участники")
def handle_all_users_button(message):
    logger.info(f"All users requested by {message.from_user.id}")
    if message.from_user.id == ADMIN_ID:
        send_users_filter_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")

@bot.message_handler(func=lambda message: message.text == "🔙 Назад в админку")
def handle_back_to_admin(message):
    if message.from_user.id == ADMIN_ID:
        send_admin_menu(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "✅ Текущие участники")
def handle_active_users(message):
    if message.from_user.id == ADMIN_ID:
        get_users_by_status(message, 'active')

@bot.message_handler(func=lambda message: message.text == "❌ Бывшие участники")
def handle_inactive_users(message):
    if message.from_user.id == ADMIN_ID:
        get_users_by_status(message, 'inactive')

@bot.message_handler(func=lambda message: message.text == "➕ Добавить дни")
def handle_add_days_button(message):
    logger.info(f"Add days requested by {message.from_user.id}")
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton("🔙 Назад в админку"))
        msg = bot.send_message(message.chat.id, "Введите ID пользователя:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_add_days_user_id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")

def process_add_days_user_id(message):
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return
    
    try:
        user_id = int(message.text)
        msg = bot.send_message(message.chat.id, f"Введите количество дней для добавления для пользователя {user_id}:")
        bot.register_next_step_handler(msg, process_add_days_amount, user_id)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID пользователя. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)

def process_add_days_amount(message, user_id):
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return

    try:
        days_to_add = int(message.text)
        add_subscription_days_logic(user_id, days_to_add, message.chat.id)
        send_admin_menu(message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное количество дней. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "➖ Вычесть дни")
def handle_remove_days_button(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton("🔙 Назад в админку"))
        msg = bot.send_message(message.chat.id, "Введите ID пользователя:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_remove_days_user_id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")

def process_remove_days_user_id(message):
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return
        
    try:
        user_id = int(message.text)
        msg = bot.send_message(message.chat.id, f"Введите количество дней для вычитания для пользователя {user_id}:")
        bot.register_next_step_handler(msg, process_remove_days_amount, user_id)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID пользователя. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)

def process_remove_days_amount(message, user_id):
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return

    try:
        days_to_remove = int(message.text)
        remove_subscription_days_logic(user_id, days_to_remove, message.chat.id)
        send_admin_menu(message.chat.id)
    except ValueError:
        bot.send_message(message.chat.id, "Некорректное количество дней. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "⚙️ Админ")
def handle_admin_button(message):
    if message.from_user.id == ADMIN_ID:
        send_admin_menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "У вас нет прав администратора.")

@bot.message_handler(commands=['start'])
def handle_start(message):
    user_id = message.from_user.id
    first_name = message.from_user.first_name
    username = message.from_user.username

    user_data = get_user_status(user_id)

    try:
        member = bot.get_chat_member(GROUP_CHAT_ID, user_id)
        if member.status in ['member', 'administrator', 'creator']:
            if not user_data or user_data['subscription_status'] != 'active':
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
                        DO UPDATE SET subscription_status = 'active', subscription_end_date = ?, payment_status = 'paid', last_notification_level = NULL
                    """, (user_id, first_name, username, 'active', now_str, end_date_str, 'paid', end_date_str))
                    conn.commit()
                logger.info(f"Existing member {user_id} auto-migrated with active sub until {end_date}.")
                
                user_data = get_user_status(user_id)
    except Exception as e:
        logger.error(f"Error checking existing member status in handle_start: {e}")


    if not user_data:
        try:
            with get_db_connection() as conn:
                conn.execute("INSERT INTO users (telegram_id, first_name, username, subscription_status, subscription_start_date, subscription_end_date, payment_status) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (user_id, first_name, username, 'inactive', None, None, 'pending'))
                conn.commit()
        except Exception as e:
            logger.error(f"Error adding new user to database: {e}")
    
    send_main_menu(user_id, message.chat.id, first_name)

@bot.callback_query_handler(func=lambda call: call.data == 'start_bot')
def callback_start_bot(call):
    bot.answer_callback_query(call.id)
    user_id = call.message.chat.id
    
    # Вызываем handle_start логику, чтобы сработала миграция
    msg = types.Message(call.message.message_id, call.message.from_user, call.message.date, call.message.chat, 'text', {}, '/start')
    handle_start(msg)

@bot.message_handler(func=lambda message: message.text == "Тарифы")
def send_tariffs(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    btn_basic = types.KeyboardButton("Тариф \"Базисный 🤝\"")
    btn_brave = types.KeyboardButton("Тариф \"Смелый✊\"")
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(btn_basic, btn_brave, back_button)
    bot.send_message(message.chat.id,
                     "*Тарифы*\n\n" 
                     f"На настоящий момент в нашем закрытом сообществе «*Trade Therapy*» действует два тарифных плана:\n\n" 
                     "◻️ Тариф \"Базисный 🤝\" - 1 календарный месяц доступа к закрытому клубу.\n" 
                     "   Стоимость: 3000 руб.\n" 
                     "   Срок действия : 1 календарный месяц.\n\n" 
                     "◻️ Тариф \"Смелый✊\" - 3 календарных месяца доступа к закрытому клубу.\n" 
                     "   Стоимость: 9000 руб.\n" 
                     "   Срок действия : 3 календарных месяца.\n\n" 
                     "Для оплаты выберите интересующий ваш тариф.",
                     parse_mode='Markdown',
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Тариф \"Базисный 🤝\"")
def handle_tariff_basic(message):
    send_payment_info(message, 3000)

@bot.message_handler(func=lambda message: message.text == "Тариф \"Смелый✊\"")
def handle_tariff_brave(message):
    send_payment_info(message, 9000)

@bot.message_handler(func=lambda message: message.text == "Вернутся в главное меню🏡")
@bot.message_handler(func=lambda message: message.text == "🔄 Перезагрузить бота") # оставляем для совместимости
def handle_restart_bot(message):
    handle_start(message)

@bot.message_handler(func=lambda message: message.text == "Не буду платить")
def handle_wont_pay_menu(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    reason1 = types.KeyboardButton("Я не торгую")
    reason2 = types.KeyboardButton("Не буду платить по другой причине")
    back = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(reason1, reason2, back)
    bot.send_message(message.chat.id, "Почему вы решили не платить?", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Я не торгую")
def handle_reason_trading(message):
    msg = bot.send_message(message.chat.id, "Напиши, пожалуйста, подробно, чем ты занимаешься и когда вернёшься в рынок?")
    bot.register_next_step_handler(msg, process_reason_trading)

def process_reason_trading(message):
    if message.text == "Вернутся в главное меню🏡" or message.text == "Назад":
        handle_wont_pay_menu(message)
        return

    user_id = message.from_user.id
    reason = message.text
    logger.info(f"User {user_id} reason (trading): {reason}")
    
    add_subscription_days_logic(user_id, 30, ADMIN_ID) 
    
    bot.send_message(ADMIN_ID, f"Пользователь {user_id} ({message.from_user.first_name}) выбрал 'Я не торгую'.\nОтвет: {reason}")

@bot.message_handler(func=lambda message: message.text == "Не буду платить по другой причине")
def handle_reason_other(message):
    msg = bot.send_message(message.chat.id, "Напиши, пожалуйста, подробно, почему ты не будешь платить. Плюсы и минусы сообщества.")
    bot.register_next_step_handler(msg, process_reason_other)

def process_reason_other(message):
    if message.text == "Вернутся в главное меню🏡" or message.text == "Назад":
        handle_wont_pay_menu(message)
        return

    user_id = message.from_user.id
    reason = message.text
    logger.info(f"User {user_id} reason (other): {reason}")

    add_subscription_days_logic(user_id, 30, ADMIN_ID) 

    bot.send_message(ADMIN_ID, f"Пользователь {user_id} ({message.from_user.first_name}) выбрал 'Другая причина'.\nОтвет: {reason}")

@bot.message_handler(func=lambda message: message.text == "Назад")
def handle_back_button_payment(message):
    send_main_menu(message.from_user.id, message.chat.id, message.from_user.first_name)

@bot.message_handler(func=lambda message: message.text == "Правила Клуба")
def send_rules(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    bot.send_message(message.chat.id,
                     "*Правила Клуба*\n\n" 
                     "1. Уважительно относиться друг к другу.\n" 
                     "2. Не перебивать друг друга.\n" 
                     "3. Не флудить во время активной торговли и во время важных новостных событий.\n" 
                     "4. Если находитесь в голосовом чате (ГЧ), то включайте микрофон только тогда, когда хотите взять слово.\n" 
                     "5. По возможности стараемся меньше материться.\n" 
                     "6. Используем ветки в группе по назначению.",
                     parse_mode='Markdown',
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "О Нас")
def send_about_us(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    
    file_id_1 = 'AgACAgIAAxkBAAIEVWktlnhZ-lksHTT_8mMF_rMBZ1juAAJsEGsbhNZoSU0rol3-wvFxAQADAgADeQADNgQ'
    file_id_2 = 'AgACAgIAAxkBAAIEV2ktlpFww7VEv6Sb3xRCKDOQ13NTAAJwEGsbhNZoSRonbqyrw44MAQADAgADeQADNgQ'
    bot.send_photo(message.chat.id, file_id_1)
    bot.send_photo(message.chat.id, file_id_2)
    
    bot.send_message(message.chat.id,
                     "*О Нас*\n\n" 
                     f"В нашем закрытом сообществе «*Trade Therapy*»:\n\n" 
                     "✅ Торговые идеи по российским акциям внутри дня, локально-среднесрочно\n" 
                     "✅ Обсуждение и обоснование сделок\n" 
                     "✅ Обзор и аналитика по событиям рынка (товарный рынок, технический анализ, новостной фон)\n" 
                     "✅ Поддержка в голосовом чате во время активных торговых сессий + чат 💬\n" 
                     "✅ Проведение стримов-брифов\n" 
                     "✅ Записи психологических сессий для личностного понимания куда двигаться и зачем\n\n" 
                     "Мы поможем вам развивать навыки и улучшать свою стратегию торговли.\n\n" 
                     "☝️ Подписываясь на закрытое сообщество, вы должны учитывать, что операции на финансовом рынке сопряжены с риском и могут вести как к прибыли, так и к убыткам.\n" 
                     "Вы сами отвечаете за сделки, которые совершали.",
                     parse_mode='Markdown',
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Отзывы")
def handle_reviews(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    
    file_id_screen1 = 'AgACAgIAAxkBAAIEU2ktlk9Bu7e5xcSYQrSt9mx5I4e4AAJrEGsbhNZoSdThsmpCxUMJAQADAgADeAADNgQ'
    bot.send_photo(message.chat.id, file_id_screen1)

    bot.send_message(message.chat.id, "Больше отзывов здесь: https://t.me/feedbacktradetherapy", reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Обратная связь")
def send_feedback_contact(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    bot.send_message(message.chat.id, "*Обратная связь*\n\n" 
                     "Если у вас есть вопросы, претензии или предложения, свяжитесь со мной: @nikkronos",
                     parse_mode='Markdown',
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Публичная оферта")
def send_oferta(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    bot.send_message(message.chat.id, "*Публичная оферта*\n\n"
                     "Документ будет добавлен позже.", 
                     parse_mode='Markdown',
                     reply_markup=markup)

@bot.message_handler(commands=['tariffs'])
def handle_tariffs_command(message):
    send_tariffs(message)

@bot.message_handler(commands=['rules'])
def handle_rules_command(message):
    send_rules(message)

@bot.message_handler(commands=['about'])
def handle_about_command(message):
    send_about_us(message)

@bot.message_handler(commands=['feedback'])
def handle_feedback_command(message):
    send_feedback_contact(message)

@bot.message_handler(commands=['status'])
def handle_status_command(message):
    user_id = message.from_user.id
    user_data = get_user_status(user_id)

    status_message = ""
    if user_data:
        first_name = user_data['first_name']
        sub_status = user_data['subscription_status']
        start_date = parse_db_date(user_data['subscription_start_date'])
        end_date = parse_db_date(user_data['subscription_end_date'])

        if sub_status == 'active':
            status_message = f"Текущий статус подписки, {first_name}:\n\n"
            status_message += f"Статус: Активна\n"
            if start_date and end_date:
                status_message += f"Начало подписки: {start_date.strftime('%H:%M:%S %d.%m.%Y')}\n"
                status_message += f"Конец подписки: {end_date.strftime('%H:%M:%S %d.%m.%Y')}\n"
        else:
            status_message = "К сожалению, у вас нет подписки."
    else:
        status_message = "К сожалению, у вас нет подписки."

    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    if "К сожалению" in status_message:
         btn_tariffs = types.KeyboardButton("Тарифы")
         markup.add(btn_tariffs)
    
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    bot.send_message(message.chat.id, "*Статус подписки*\n\n" 
                     + status_message,
                     parse_mode='Markdown',
                     reply_markup=markup)

@bot.message_handler(func=lambda message: message.text == "Статус подписки")
def handle_status_button(message):
    handle_status_command(message)

@bot.message_handler(commands=['set_subscription'])
def set_subscription(message):
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
def get_all_users(message):
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
def add_subscription_days(message):
    if message.from_user.id != ADMIN_ID:
        bot.send_message(message.chat.id, "У вас нет прав для выполнения этой команды.")
        return

    args = message.text.split()[1:]
    if len(args) == 2:
        try:
            user_id = int(args[0])
            days_to_add = int(args[1])
            add_subscription_days_logic(user_id, days_to_add, message.chat.id)
        except ValueError:
            bot.send_message(message.chat.id, "Некорректные данные. ID и дни должны быть числами.")
    else:
        bot.send_message(message.chat.id, "Использование: /add_subscription_days <user_id> <количество_дней>")

@bot.message_handler(commands=['remove_subscription_days'])
def remove_subscription_days(message):
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

@bot.message_handler(func=lambda message: message.text == "🧾 Чеки")
def handle_receipts_menu(message):
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

@bot.message_handler(func=lambda message: message.text == "🗑 Удалить пользователя")
def handle_delete_user_btn(message):
    if message.from_user.id == ADMIN_ID:
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        markup.add(types.KeyboardButton("🔙 Назад в админку"))
        msg = bot.send_message(message.chat.id, "Введите ID пользователя для удаления:", reply_markup=markup)
        bot.register_next_step_handler(msg, process_delete_user_id)

def process_delete_user_id(message):
    if message.text == "🔙 Назад в админку":
        send_admin_menu(message.chat.id)
        return
        
    try:
        user_id = int(message.text)
        
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
        
    except ValueError:
        bot.send_message(message.chat.id, "Некорректный ID. Попробуйте еще раз.")
        send_admin_menu(message.chat.id)

@bot.message_handler(func=lambda message: message.text == "💰 Неподтверждённые оплаты")
def handle_pending_payments(message):
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
def get_file_id_admin(message):
    file_id = message.photo[-1].file_id
    logger.info(f"ADMIN SENT PHOTO. File_id: {file_id}")
    bot.send_message(message.chat.id, f"File ID этой картинки:\n{file_id}")

@bot.message_handler(content_types=['text', 'photo', 'document'])
def handle_payment_confirmation(message):
    if message.chat.id != ADMIN_ID:
        if message.content_type in ['photo', 'document']:
             try:
                 with get_db_connection() as conn:
                     conn.execute("UPDATE users SET payment_status = 'pending_review' WHERE telegram_id = ?", (message.from_user.id,))
                     conn.commit()
             except Exception as e:
                 logger.error(f"Error updating payment status: {e}")

             try:
                 file_id = None
                 file_type = 'unknown'
                 
                 if message.content_type == 'photo':
                     file_id = message.photo[-1].file_id
                     file_type = 'photo'
                 elif message.content_type == 'document':
                     file_id = message.document.file_id
                     file_type = 'document'
                 
                 if file_id:
                     with get_db_connection() as conn:
                         conn.execute("INSERT INTO receipts (user_id, file_id, file_type) VALUES (?, ?, ?)", (message.from_user.id, file_id, file_type))
                         conn.commit()
             except Exception as e:
                 logger.error(f"Error saving receipt: {e}")

             markup = types.InlineKeyboardMarkup()
             btn_confirm = types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_pay_{message.from_user.id}")
             btn_reject = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_pay_{message.from_user.id}")
             markup.add(btn_confirm, btn_reject)
             
             bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
             
             bot.send_message(ADMIN_ID, f"Пользователь {message.from_user.first_name} прислал чек.", reply_markup=markup)
             
             bot.send_message(message.chat.id, "Ваше подтверждение отправлено администратору. Ожидайте активации.")
        
        else:
            pass

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_pay_'))
def callback_confirm_payment(call):
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
def callback_reject_payment(call):
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

@bot.chat_member_handler()
def handle_chat_member_update(update):
    if update.chat.id == GROUP_CHAT_ID:
        user_id = update.from_user.id
        new_status = update.new_chat_member.status
        
        if new_status == 'member':
             user_data = get_user_status(user_id)
             
             is_admin = (user_id == ADMIN_ID)
             has_active_sub = (user_data and user_data['subscription_status'] == 'active')
             
             if not is_admin and not has_active_sub:
                 try:
                     bot.kick_chat_member(GROUP_CHAT_ID, user_id)
                     bot.unban_chat_member(GROUP_CHAT_ID, user_id) 
                     bot.send_message(user_id, "Вы вступили в группу без активной подписки. Доступ запрещен. Пожалуйста, оплатите подписку.")
                     logger.info(f"Kicked user {user_id} who joined without active subscription.")
                     return 
                 except Exception as e:
                     logger.error(f"Failed to kick unauthorized joiner {user_id}: {e}")

             try:
                 first_name = update.from_user.first_name
                 send_main_menu(user_id, user_id, first_name)
             except Exception as e:
                 logger.error(f"Error sending welcome menu to new member {user_id}: {e}")

