import asyncio
import logging

from aiogram import types, utils
from aiogram.dispatcher.filters import Text

from database.getters import get_data
from keyboards.keyboards import get_keyboard
from loader import dp
from utils import states_users as su
from data import config

logger = logging.getLogger(__name__)


@dp.callback_query_handler(Text("broadcast"))
async def broadcast_menu(call: types.CallbackQuery):
    """Меню выбора аудитории для рассылки"""
    await call.answer()
    
    if call.from_user.id not in config.ADMINS:
        return
    
    buttons = [
        [
            ("Все пользователи", "broadcast_all"),
            ("Только активные", "broadcast_active"),
            ("Только неактивные", "broadcast_inactive"),
        ],
        [
            ("Отмена", "menu_admin"),
        ]
    ]
    
    await call.message.answer(
        "Выберите аудиторию для рассылки:",
        reply_markup=await get_keyboard(buttons)
    )


@dp.callback_query_handler(Text(startswith="broadcast_"))
async def broadcast_select_audience(call: types.CallbackQuery):
    """Выбор аудитории и запрос текста сообщения"""
    await call.answer()
    
    if call.from_user.id not in config.ADMINS:
        return
    
    audience_type = call.data.split("_")[-1]  # "all", "active", "inactive"
    
    # Сохраняем тип аудитории
    await su.save_data_state(call.from_user.id, broadcast_audience=audience_type)
    
    buttons = [
        [("Отмена", "menu_admin")],
    ]
    
    await call.message.answer(
        "Отправьте текст сообщения для рассылки:",
        reply_markup=await get_keyboard(buttons)
    )
    await su.set_state(call.from_user.id, "broadcast_text")


@dp.message_handler(state="broadcast_text")
async def broadcast_confirm(message: types.Message):
    """Подтверждение рассылки"""
    if message.from_user.id not in config.ADMINS:
        await su.reset_state_user(message.from_user.id, clear_data=True)
        return
    
    text = message.text.strip()
    
    if not text:
        await message.answer("Текст сообщения не может быть пустым. Попробуйте снова:")
        return
    
    # Сохраняем текст
    await su.save_data_state(message.from_user.id, broadcast_text=text)
    
    # Получаем тип аудитории
    audience_type = await su.get_data_from_state(message.from_user.id, "broadcast_audience")
    
    # Подсчитываем количество получателей
    all_users = await get_data("users", fetch="all")
    active_subscriptions = await get_data("user_subscriptions", fetch="all")
    active_user_ids = {sub["user_id"] for sub in active_subscriptions} if active_subscriptions else set()
    
    if audience_type == "active":
        count = len([u for u in all_users if u["user_id"] in active_user_ids])
        audience_name = "активных пользователей"
    elif audience_type == "inactive":
        count = len([u for u in all_users if u["user_id"] not in active_user_ids])
        audience_name = "неактивных пользователей"
    else:
        count = len(all_users)
        audience_name = "всех пользователей"
    
    buttons = [
        [
            ("✅ Отправить", "broadcast_confirm_send"),
            ("❌ Отмена", "broadcast_cancel"),
        ]
    ]
    
    await message.answer(
        f"Подтвердите рассылку:\n\n"
        f"<b>Аудитория:</b> {audience_name}\n"
        f"<b>Количество получателей:</b> {count}\n\n"
        f"<b>Текст сообщения:</b>\n{text[:500]}{'...' if len(text) > 500 else ''}",
        reply_markup=await get_keyboard(buttons),
        parse_mode="HTML"
    )


@dp.callback_query_handler(Text("broadcast_confirm_send"))
async def broadcast_send(call: types.CallbackQuery):
    """Отправка рассылки"""
    await call.answer()
    
    if call.from_user.id not in config.ADMINS:
        await su.reset_state_user(call.from_user.id, clear_data=True)
        return
    
    # Получаем данные из state
    audience_type = await su.get_data_from_state(call.from_user.id, "broadcast_audience")
    text = await su.get_data_from_state(call.from_user.id, "broadcast_text")
    
    # Сбрасываем state
    await su.reset_state_user(call.from_user.id, clear_data=True)
    
    if not text:
        await call.message.answer("Ошибка: текст сообщения не найден")
        return
    
    # Получаем список получателей
    all_users = await get_data("users", fetch="all")
    active_subscriptions = await get_data("user_subscriptions", fetch="all")
    active_user_ids = {sub["user_id"] for sub in active_subscriptions} if active_subscriptions else set()
    
    if audience_type == "active":
        recipients = [u["user_id"] for u in all_users if u["user_id"] in active_user_ids]
    elif audience_type == "inactive":
        recipients = [u["user_id"] for u in all_users if u["user_id"] not in active_user_ids]
    else:
        recipients = [u["user_id"] for u in all_users]
    
    if not recipients:
        await call.message.answer("Нет получателей для рассылки")
        return
    
    # Отправляем уведомление о начале рассылки
    total = len(recipients)
    await call.message.answer(f"Начинаю рассылку для {total} пользователей...")
    
    # Статистика
    sent = 0
    failed = 0
    blocked = 0
    
    # Отправка с rate limiting
    for i, user_id in enumerate(recipients, 1):
        try:
            await dp.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
            sent += 1
            
            # Rate limiting: 20 сообщений в секунду (лимит Telegram)
            if i % 20 == 0:
                await asyncio.sleep(1)
            else:
                await asyncio.sleep(0.05)  # Небольшая задержка между сообщениями
                
        except utils.exceptions.BotBlocked:
            blocked += 1
            logger.warning(f"Пользователь {user_id} заблокировал бота")
        except utils.exceptions.RetryAfter as e:
            logger.warning(f"Rate limit: жду {e.timeout} секунд")
            await asyncio.sleep(e.timeout)
            # Повторная попытка
            try:
                await dp.bot.send_message(chat_id=user_id, text=text, parse_mode="HTML")
                sent += 1
            except Exception as e:
                failed += 1
                logger.error(f"Ошибка при отправке пользователю {user_id}: {e}")
        except Exception as e:
            failed += 1
            logger.error(f"Ошибка при отправке пользователю {user_id}: {e}")
        
        # Прогресс каждые 50 сообщений
        if i % 50 == 0:
            await call.message.edit_text(
                f"Рассылка в процессе...\n"
                f"Отправлено: {sent}/{total}\n"
                f"Ошибок: {failed}\n"
                f"Заблокировали: {blocked}"
            )
    
    # Финальный отчет
    report = (
        f"✅ Рассылка завершена!\n\n"
        f"<b>Статистика:</b>\n"
        f"Всего получателей: {total}\n"
        f"Успешно отправлено: {sent}\n"
        f"Ошибок: {failed}\n"
        f"Заблокировали бота: {blocked}"
    )
    
    await call.message.answer(report, parse_mode="HTML")
    logger.info(f"Рассылка завершена: отправлено {sent}/{total}, ошибок {failed}, заблокировали {blocked}")


@dp.callback_query_handler(Text("broadcast_cancel"))
async def broadcast_cancel(call: types.CallbackQuery):
    """Отмена рассылки"""
    await call.answer()
    await su.reset_state_user(call.from_user.id, clear_data=True)
    await call.message.answer("Рассылка отменена", reply_markup=await get_keyboard([[("Назад", "menu_admin")]]))


























