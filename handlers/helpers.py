"""
Helper functions for creating menus and UI elements.
These functions don't have decorators and can be used by other handlers.
"""
from typing import Optional
from telebot import types
from loader import bot, ADMIN_ID
from database import get_user_status, get_user_tariff_answers

# Список вопросов для опроса
TARIFF_QUESTIONS = [
    "какой у вас рабочий депозит?",
    "сколько портфелей/счетов?",
    "какой опыт торговли, сколько знакомы с рынком?",
    "какой стиль торговли/какую стратегию используете?",
    "какие результаты торговли? сколько заработано/потеряно?",
    "что хотите получить от рынка?",
    "что хотите получить от сообщества?",
    "какие у вас цели и мечты в жизни?",
    "из какого города (важен часовой пояс)?",
    "полная дата рождения (важен возраст)?",
    "какой любимый/интересный канал по рыночной тематике?",
    "хотели бы вы что-то изменить в себе или может уже изменили? Если да, что конкретно?",
    "какое ваше самое выдающееся достижение?"
]


def send_initial_welcome(message: types.Message) -> None:
    """Отправляет приветственное сообщение с кнопкой запуска бота"""
    markup = types.InlineKeyboardMarkup()
    start_button = types.InlineKeyboardButton("Запустить бота", callback_data='start_bot')
    markup.add(start_button)
    bot.send_message(message.chat.id, 
                     f"👋 Добро пожаловать в чат-бот Сообщества *Trade Therapy*\n\n" 
                     "Здесь вы сможете получить доступ к Сообществу следуя инструкциям.\n\n" 
                     "Для начала нажмите кнопку \"Запустить бота\"",
                     parse_mode='Markdown',
                     reply_markup=markup)


def send_main_menu(user_id: int, chat_id: int, first_name: str) -> None:
    """Отправляет главное меню пользователю"""
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
                     "*Тарифы* — ознакомиться с тарифами и получить доступ к нашей закрытой группе\n" 
                     "*О Нас* — ознакомиться с информацией о нашем закрытом сообществе\n" 
                     "*Правила Клуба* — изучить внутренний регламент\n"
                     "*Статус подписки* — узнать статус действующей подписки\n"
                     "*Отзывы* — посмотреть отзывы участников\n" 
                     "*Обратная связь* — если не нашли ответ на ваш вопрос\n" 
                     "*Публичная оферта* — ознакомиться с юридической стороной",
                     parse_mode='Markdown',
                     reply_markup=markup)


def send_admin_menu(chat_id: int) -> None:
    """Отправляет административное меню"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_manage_days = types.KeyboardButton("🕒 Изменить дни")
    btn_all_users = types.KeyboardButton("👥 Все участники")
    btn_pending = types.KeyboardButton("💰 Неподтверждённые оплаты")
    btn_receipts = types.KeyboardButton("🧾 Чеки и оплаты")
    btn_back_to_main = types.KeyboardButton("⬅️ Главное меню")
    markup.add(btn_manage_days, btn_all_users, btn_pending, btn_receipts, btn_back_to_main)
    bot.send_message(chat_id, "*Административное меню:*", parse_mode='Markdown', reply_markup=markup)


def send_users_filter_menu(chat_id: int) -> None:
    """Отправляет меню фильтрации пользователей"""
    markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_active = types.KeyboardButton("✅ Текущие участники")
    btn_inactive = types.KeyboardButton("❌ Бывшие участники")
    btn_back = types.KeyboardButton("🔙 Назад в админку")
    markup.add(btn_active, btn_inactive, btn_back)
    bot.send_message(chat_id, "Какие участники вас интересуют?", reply_markup=markup)


def send_payment_info(message: types.Message, amount: int) -> None:
    """Отправляет информацию о реквизитах для оплаты"""
    user_id = message.from_user.id
    user_data = get_user_status(user_id)
    
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    
    if user_data and user_data['subscription_status'] == 'active':
        wont_pay = types.KeyboardButton("Не буду платить")
        markup.add(wont_pay)
    
    back_btn = types.KeyboardButton("Назад 🔙")
    restart_btn = types.KeyboardButton("Вернутся в главное меню🏡")
    markup.add(back_btn, restart_btn)
    
    # Разный текст для активных пользователей и новых
    if user_data and user_data['subscription_status'] == 'active':
        payment_text = (
            "Для *поддержки* развития Сообщества переведите *любую сумму*, которую считаете равнозначным *вкладом* за ту *ценность*, что вы получаете, будучи участником (например, рабочие идеи, эмоциональная поддержка, возможность высказывать своё мнение, отсутствие флуда, разносторонее и альтернативное мнение).\n\n"
            "1. Номер телефона: +79213032918 (Т-Банк)\n\n"
            "2. Или через СБП по этому номеру телефона.\n\n"
            "После оплаты, пожалуйста, отправьте скриншот чека в этот чат для активации подписки.\n\n"
            "Либо нажмите кнопку ниже."
        )
    else:
        payment_text = (
            f"Для оплаты подписки переведите сумму {amount} руб. на \n\n" 
            "Номер телефона: +79213032918 (Т-Банк)\n\n" 
            "Или через СБП по этому номеру телефона.\n\n" 
            "После оплаты, пожалуйста, отправьте скриншот чека в этот чат для активации подписки."
        )
    
    bot.send_message(message.chat.id, payment_text, parse_mode='Markdown', reply_markup=markup)


def send_answers_to_admin(user_id: int, first_name: str, username: Optional[str]) -> None:
    """Отправить все ответы пользователя админу с кнопками подтвердить/отклонить"""
    from database import get_user_tariff_answers
    
    answers = get_user_tariff_answers(user_id)
    
    if not answers:
        return
    
    response = f"Ответы на вопросы от пользователя:\n\n"
    response += f"ID: {user_id}\n"
    response += f"Имя: {first_name}\n"
    username_str = f"@{username}" if username else "нет username"
    response += f"Username: {username_str}\n\n"
    
    for answer_row in answers:
        question_num = answer_row['question_number']
        answer_text = answer_row['answer']
        question_text = TARIFF_QUESTIONS[question_num - 1]
        response += f"{question_num}. {question_text}\n"
        response += f"Ответ: {answer_text}\n\n"
    
    # Разбиваем на части, если сообщение слишком длинное
    if len(response) > 4000:
        parts = response.split("\n\n")
        current_part = ""
        for part in parts:
            if len(current_part + part) > 4000:
                bot.send_message(ADMIN_ID, current_part, parse_mode='Markdown')
                current_part = part + "\n\n"
            else:
                current_part += part + "\n\n"
        if current_part:
            bot.send_message(ADMIN_ID, current_part, parse_mode='Markdown')
    else:
        bot.send_message(ADMIN_ID, response, parse_mode='Markdown')
    
    # Добавляем кнопки подтвердить/отклонить
    markup = types.InlineKeyboardMarkup()
    btn_confirm = types.InlineKeyboardButton("✅ Подтвердить", callback_data=f"confirm_tariff_{user_id}")
    btn_reject = types.InlineKeyboardButton("❌ Отклонить", callback_data=f"reject_tariff_{user_id}")
    markup.add(btn_confirm, btn_reject)
    bot.send_message(ADMIN_ID, "Подтвердить или отклонить ответы?", reply_markup=markup)

