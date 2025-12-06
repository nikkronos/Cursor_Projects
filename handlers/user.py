"""
User handlers for TradeTherapyBot.
Contains all user-facing commands and menus.
"""
from telebot import types
from datetime import datetime
from loader import bot, logger, ADMIN_ID, GROUP_CHAT_ID
from database import get_db_connection, parse_db_date, format_db_date, get_user_status, save_tariff_answer, get_user_tariff_answers, clear_user_tariff_answers
from handlers.helpers import send_main_menu, send_payment_info, send_answers_to_admin, TARIFF_QUESTIONS
from utils import rate_limit


@bot.message_handler(commands=['start'])
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_start(message: types.Message) -> None:
    """Обработчик команды /start - регистрация пользователя и показ главного меню"""
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


@bot.message_handler(func=lambda message: message.text == "⬅️ Главное меню")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_back_to_main_menu(message: types.Message) -> None:
    """Обработчик кнопки '⬅️ Главное меню'"""
    logger.info(f"Back to main menu requested by {message.from_user.id}")
    send_main_menu(message.from_user.id, message.chat.id, message.from_user.first_name)


@bot.message_handler(func=lambda message: message.text == "Вернутся в главное меню🏡")
@bot.message_handler(func=lambda message: message.text == "🔄 Перезагрузить бота")  # оставляем для совместимости
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_restart_bot(message: types.Message) -> None:
    """Обработчик кнопки 'Вернутся в главное меню🏡' и '🔄 Перезагрузить бота'"""
    handle_start(message)


@bot.message_handler(func=lambda message: message.text == "Тарифы")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def send_tariffs(message: types.Message) -> None:
    """Показать информацию о тарифах"""
    user_id = message.from_user.id
    user_data = get_user_status(user_id)
    
    # Если у пользователя есть активная подписка - показываем кнопку "Остаться в Сообществе"
    if user_data and user_data['subscription_status'] == 'active':
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        btn_payment = types.KeyboardButton("Остаться в Сообществе")
        back_button = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(btn_payment, back_button)
        bot.send_message(message.chat.id,
                         "*Тарифы*\n\n" 
                         "Для продления подписки нажмите кнопку 'Остаться в Сообществе'.",
                         parse_mode='Markdown',
                         reply_markup=markup)
    else:
        # Заглушка для пользователей без подписки - не даем проходить дальше
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        back_button = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(back_button)
        
        bot.send_message(message.chat.id,
                         "*Тарифы*\n\n"
                         "Информация появится здесь 25 декабря.",
                         parse_mode='Markdown',
                         reply_markup=markup)


@rate_limit(max_requests=15, time_window=10.0, block_duration=30.0)
def ask_tariff_question(message: types.Message, question_index: int) -> None:
    """Задать вопрос из опроса"""
    user_id = message.from_user.id
    
    if question_index >= len(TARIFF_QUESTIONS):
        # Все вопросы заданы - отправляем ответы админу
        send_answers_to_admin(user_id, message.from_user.first_name, message.from_user.username)
        
        # Пользователю отправляем сообщение об ожидании
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(home_btn)
        bot.send_message(user_id, "Ожидайте, лидер сообщества изучает ваши ответы", reply_markup=markup)
        return
    
    question_num = question_index + 1
    question_text = TARIFF_QUESTIONS[question_index]
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(home_btn)
    
    msg = bot.send_message(user_id, f"Вопрос {question_num} из {len(TARIFF_QUESTIONS)}:\n{question_text}", reply_markup=markup)
    bot.register_next_step_handler(msg, process_tariff_answer, question_index)


@rate_limit(max_requests=15, time_window=10.0, block_duration=30.0)
def process_tariff_answer(message: types.Message, question_index: int) -> None:
    """Обработать ответ на вопрос"""
    if message.text == "Вернутся в главное меню🏡":
        handle_start(message)
        return
    
    user_id = message.from_user.id
    question_num = question_index + 1
    answer = message.text
    
    # Сохраняем ответ
    save_tariff_answer(user_id, question_num, answer)
    
    # Задаем следующий вопрос
    ask_tariff_question(message, question_index + 1)


@bot.message_handler(func=lambda message: message.text == "Я согласен")
@rate_limit(max_requests=15, time_window=10.0, block_duration=30.0)
def handle_agree_button(message: types.Message) -> None:
    """Обработчик кнопки 'Я согласен' для начала опроса"""
    user_id = message.from_user.id
    clear_user_tariff_answers(user_id)  # Очищаем старые ответы, если есть
    ask_tariff_question(message, 0)


@bot.message_handler(func=lambda message: message.text == "Я уже отвечал на вопросы")
@rate_limit(max_requests=15, time_window=10.0, block_duration=30.0)
def handle_already_answered(message: types.Message) -> None:
    """Обработчик кнопки 'Я уже отвечал на вопросы'"""
    user_id = message.from_user.id
    
    # Проверяем, есть ли у пользователя сохраненные ответы
    answers = get_user_tariff_answers(user_id)
    
    if answers:
        # Если есть ответы, отправляем их админу для повторного рассмотрения
        username = message.from_user.username if message.from_user.username else None
        send_answers_to_admin(user_id, message.from_user.first_name, username)
        
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(home_btn)
        bot.send_message(user_id, "Ваши ответы отправлены на повторное рассмотрение. Ожидайте, лидер сообщества изучает ваши ответы.", reply_markup=markup)
    else:
        # Если ответов нет, начинаем опрос заново
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
        markup.add(home_btn)
        msg = bot.send_message(user_id, "Ответы не найдены. Давайте начнем опрос заново. Первый вопрос:", reply_markup=markup)
        clear_user_tariff_answers(user_id)
        ask_tariff_question(message, 0)


@bot.message_handler(func=lambda message: message.text == "Тариф \"Базисный 🤝\"")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_tariff_basic(message: types.Message) -> None:
    """Обработчик кнопки 'Тариф \"Базисный 🤝\"'"""
    send_payment_info(message, 3000)


@bot.message_handler(func=lambda message: message.text == "Тариф \"Смелый✊\"")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_tariff_brave(message: types.Message) -> None:
    """Обработчик кнопки 'Тариф \"Смелый✊\"'"""
    send_payment_info(message, 9000)


@bot.message_handler(func=lambda message: message.text == "Остаться в Сообществе")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_payment_button(message: types.Message) -> None:
    """Обработчик кнопки 'Остаться в Сообществе' для пользователей с активной подпиской"""
    user_id = message.from_user.id
    user_data = get_user_status(user_id)
    
    if user_data and user_data['subscription_status'] == 'active':
        # Показываем реквизиты для оплаты
        send_payment_info(message, "любую сумму")
    else:
        # Если подписка неактивна, перенаправляем в тарифы
        send_tariffs(message)


@bot.message_handler(func=lambda message: message.text == "Не буду платить")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_wont_pay_menu(message: types.Message) -> None:
    """Меню выбора причины отказа от оплаты"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    reason1 = types.KeyboardButton("Я не торгую")
    reason2 = types.KeyboardButton("Не буду платить по другой причине")
    back_btn = types.KeyboardButton("Назад 🔙")
    home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(reason1, reason2, back_btn, home_btn)
    bot.send_message(message.chat.id, "Почему вы решили не платить?", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Я не торгую")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_reason_trading(message: types.Message) -> None:
    """Обработчик кнопки 'Я не торгую'"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_btn = types.KeyboardButton("Назад 🔙")
    home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_btn, home_btn)
    msg = bot.send_message(message.chat.id, "Напиши, пожалуйста, подробно, чем ты занимаешься и когда вернёшься в рынок?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_reason_trading)


@rate_limit(max_requests=15, time_window=10.0, block_duration=30.0)
def process_reason_trading(message: types.Message) -> None:
    """Обработка ответа на вопрос 'Я не торгую'"""
    if message.text == "Вернутся в главное меню🏡" or message.text == "Назад 🔙":
        if message.text == "Назад 🔙":
            handle_wont_pay_menu(message)
        else:
            handle_start(message)
        return

    user_id = message.from_user.id
    reason = message.text
    logger.info(f"User {user_id} reason (trading): {reason}")
    
    # Отправляем админу с кнопками подтвердить/отклонить
    username = message.from_user.username if message.from_user.username else "нет username"
    response = f"Пользователь {user_id} ({message.from_user.first_name}) выбрал 'Я не торгую'.\n\n"
    response += f"Username: @{username}\n\n"
    response += f"Ответ: {reason}"
    
    markup = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_reason_trading_{user_id}")
    btn_reject = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_reason_trading_{user_id}")
    markup.add(btn_confirm, btn_reject)
    
    bot.send_message(ADMIN_ID, response, reply_markup=markup)
    
    # После ответа - только кнопка в главное меню
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(home_btn)
    bot.send_message(message.chat.id, "Ожидайте, лидер сообщества изучает ваш ответ.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Не буду платить по другой причине")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_reason_other(message: types.Message) -> None:
    """Обработчик кнопки 'Не буду платить по другой причине'"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_btn = types.KeyboardButton("Назад 🔙")
    home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_btn, home_btn)
    msg = bot.send_message(message.chat.id, "Напиши, пожалуйста, подробно, почему ты не будешь платить. Плюсы и минусы сообщества. Какая твоя роль в нём?", reply_markup=markup)
    bot.register_next_step_handler(msg, process_reason_other)


@rate_limit(max_requests=15, time_window=10.0, block_duration=30.0)
def process_reason_other(message: types.Message) -> None:
    """Обработка ответа на вопрос 'Не буду платить по другой причине'"""
    if message.text == "Вернутся в главное меню🏡" or message.text == "Назад 🔙":
        if message.text == "Назад 🔙":
            handle_wont_pay_menu(message)
        else:
            handle_start(message)
        return

    user_id = message.from_user.id
    reason = message.text
    logger.info(f"User {user_id} reason (other): {reason}")

    # Отправляем админу с кнопками подтвердить/отклонить
    username = message.from_user.username if message.from_user.username else "нет username"
    response = f"Пользователь {user_id} ({message.from_user.first_name}) выбрал 'Не буду платить по другой причине'.\n\n"
    response += f"Username: @{username}\n\n"
    response += f"Ответ: {reason}"
    
    markup = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_reason_other_{user_id}")
    btn_reject = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_reason_other_{user_id}")
    markup.add(btn_confirm, btn_reject)
    
    bot.send_message(ADMIN_ID, response, reply_markup=markup)
    
    # После ответа - только кнопка в главное меню
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    home_btn = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(home_btn)
    bot.send_message(message.chat.id, "Ожидайте, лидер сообщества изучает ваш ответ.", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Назад 🔙")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_back_button(message: types.Message) -> None:
    """Обработчик кнопки 'Назад 🔙' - возврат к тарифам"""
    send_tariffs(message)


@bot.message_handler(func=lambda message: message.text == "Правила Клуба")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def send_rules(message: types.Message) -> None:
    """Показать правила клуба"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    bot.send_message(message.chat.id,
                     "*Правила Клуба*\n\n" 
                     "У меня была создана задача создать *безопасное пространство* в достаточно агрессивной среде, такой как рынок. Чтобы *каждый участник* мог не бояться и имел право голоса.\n\n"
                     "1. Уважительно относиться друг к другу.\n" 
                     "2. Не перебивать друг друга.\n" 
                     "3. Не флудить во время активной торговли и во время важных новостных событий.\n" 
                     "4. Если находитесь в голосовом чате (ГЧ), то включайте микрофон только тогда, когда хотите взять слово.\n" 
                     "5. По возможности стараемся меньше материться.\n" 
                     "6. Используем ветки в группе по назначению.",
                     parse_mode='Markdown',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "О Нас")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def send_about_us(message: types.Message) -> None:
    """Показать информацию о сообществе"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    
    file_id_1 = 'AgACAgIAAxkBAAIEVWktlnhZ-lksHTT_8mMF_rMBZ1juAAJsEGsbhNZoSU0rol3-wvFxAQADAgADeQADNgQ'
    file_id_2 = 'AgACAgIAAxkBAAIEV2ktlpFww7VEv6Sb3xRCKDOQ13NTAAJwEGsbhNZoSRonbqyrw44MAQADAgADeQADNgQ'
    bot.send_photo(message.chat.id, file_id_1)
    bot.send_photo(message.chat.id, file_id_2)
    
    bot.send_message(message.chat.id,
                     "*О Нас*\n\n" 
                     f"В нашем закрытом сообществе *Trade Therapy*:\n\n" 
                     "✅ Торговые идеи по российским акциям внутри дня, локально-среднесрочно\n" 
                     "✅ Обсуждение и обоснование сделок\n" 
                     "✅ Обзор и аналитика по событиям рынка (товарный рынок, технический анализ, новостной фон)\n" 
                     "✅ Поддержка в голосовом чате во время активных торговых сессий + чат 💬\n" 
                     "✅ Проведение стримов-брифов\n" 
                     "✅ Записи психологических сессий для личностного понимания куда двигаться и зачем\n\n" 
                     "*Мы поможем* вам развивать навыки и улучшать свою стратегию торговли. Однако, помните, что *Сообщество* - это не курс и не образовательная платформа. Здесь поощряются *навыки самообучения* с *максимальной поддержкой*.\n\n" 
                     "☝️ Подписываясь на закрытое сообщество, вы должны учитывать, что операции на финансовом рынке сопряжены с риском и могут вести как к прибыли, так и к убыткам.\n" 
                     "Вы сами отвечаете за сделки, которые совершали.",
                     parse_mode='Markdown',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Отзывы")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_reviews(message: types.Message) -> None:
    """Показать отзывы"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    
    file_id_screen1 = 'AgACAgIAAxkBAAIEU2ktlk9Bu7e5xcSYQrSt9mx5I4e4AAJrEGsbhNZoSdThsmpCxUMJAQADAgADeAADNgQ'
    bot.send_photo(message.chat.id, file_id_screen1)

    bot.send_message(message.chat.id, "Больше отзывов здесь: https://t.me/feedbacktradetherapy", reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Обратная связь")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def send_feedback_contact(message: types.Message) -> None:
    """Показать контакты для обратной связи"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    bot.send_message(message.chat.id, "*Обратная связь*\n\n" 
                     "Если у вас есть вопросы, претензии или предложения, свяжитесь со мной: @nikkronos",
                     parse_mode='Markdown',
                     reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == "Публичная оферта")
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def send_oferta(message: types.Message) -> None:
    """Показать публичную оферту"""
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    back_button = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_button)
    bot.send_message(message.chat.id, "*Публичная оферта*\n\n"
                     "Документ будет добавлен позже.", 
                     parse_mode='Markdown',
                     reply_markup=markup)


@bot.message_handler(commands=['tariffs'])
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_tariffs_command(message: types.Message) -> None:
    """Команда /tariffs"""
    send_tariffs(message)


@bot.message_handler(commands=['rules'])
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_rules_command(message: types.Message) -> None:
    """Команда /rules"""
    send_rules(message)


@bot.message_handler(commands=['about'])
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_about_command(message: types.Message) -> None:
    """Команда /about"""
    send_about_us(message)


@bot.message_handler(commands=['feedback'])
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_feedback_command(message: types.Message) -> None:
    """Команда /feedback"""
    send_feedback_contact(message)


@bot.message_handler(commands=['status'])
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_status_command(message: types.Message) -> None:
    """Команда /status - показать статус подписки"""
    from utils import escape_markdown
    
    user_id = message.from_user.id
    user_data = get_user_status(user_id)

    status_message = ""
    if user_data:
        first_name = user_data['first_name']
        sub_status = user_data['subscription_status']
        start_date = parse_db_date(user_data['subscription_start_date'])
        end_date = parse_db_date(user_data['subscription_end_date'])

        if sub_status == 'active':
            # Экранируем имя пользователя для безопасного использования в Markdown
            first_name_escaped = escape_markdown(first_name if first_name else 'Пользователь')
            status_message = f"Текущий статус подписки, {first_name_escaped}:\n\n"
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
@rate_limit(max_requests=10, time_window=15.0, block_duration=30.0)
def handle_status_button(message: types.Message) -> None:
    """Обработчик кнопки 'Статус подписки'"""
    handle_status_command(message)


@bot.message_handler(content_types=['text', 'photo', 'document'])
@rate_limit(max_requests=6, time_window=60.0, block_duration=60.0)
def handle_payment_confirmation(message: types.Message) -> None:
    """Обработчик отправки чека для подтверждения оплаты"""
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
