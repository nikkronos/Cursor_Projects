"""
Join request and chat member update handlers for TradeTherapyBot.
Handles group join requests and member status changes.
"""
from loader import bot, logger, ADMIN_ID, GROUP_CHAT_ID
from database import get_user_status
from utils import safe_send_message, retry_telegram_api
from handlers.helpers import send_main_menu


@bot.chat_join_request_handler()
def handle_join_request(join_request):
    """Обработчик заявок на вступление в группу"""
    user_id = join_request.from_user.id
    chat_id = join_request.chat.id
    user_data = get_user_status(user_id)

    if user_data and user_data['subscription_status'] == 'active': 
        try:
            def approve_request():
                bot.approve_chat_join_request(chat_id, user_id)
            retry_telegram_api(approve_request, max_attempts=3)
            welcome_text = (
                "Ваша заявка на вступление в группу одобрена! Добро пожаловать в *Сообщество Trade Therapy*!\n\n"
                "Повторно ознакомьтесь с правилами в ветке *\"Объявления\"*, оставьте уведомления на эту ветку включёнными.\n\n"
                "Если вы активно торгуете, то так же оставьте включёнными уведомления на ветку *\"События рынка\"*.\n\n"
                "Представьтесь в ветке *\"Нетворкинг\"* по примеру в закрепе этой ветки.\n\n"
                "*Соблюдайте правила и чувствуйте себя собой в этой безопасной среде.*"
            )
            safe_send_message(bot, user_id, welcome_text, parse_mode='Markdown')
            logger.info(f"Заявка пользователя {user_id} в группу {chat_id} одобрена.")
        except Exception as e:
            logger.error(f"Ошибка при одобрении заявки пользователя {user_id}: {e}")
    else:
        try:
            def decline_request():
                bot.decline_chat_join_request(chat_id, user_id)
            retry_telegram_api(decline_request, max_attempts=2)
            safe_send_message(bot, user_id, f"Ваша заявка на вступление в группу отклонена, так как у вас нет активной подписки. Пожалуйста, продлите ее через бота.")
            logger.info(f"Заявка пользователя {user_id} в группу {chat_id} отклонена (нет активной подписки).")
        except Exception as e:
            logger.error(f"Ошибка при отклонении заявки пользователя {user_id}: {e}")


@bot.chat_member_handler()
def handle_chat_member_update(update):
    """Обработчик обновлений статуса участников группы (failsafe kick)"""
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
