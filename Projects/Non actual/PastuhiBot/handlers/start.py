from aiogram import types
from aiogram.dispatcher.filters import Text

import keyboards
from database.getters import get_data
from database.setters import add_new_data
from loader import dp
from utils.states_users import reset_state_user


@dp.message_handler(commands="start", state="*")
@dp.callback_query_handler(Text("start"), state="*")
async def start(message: types.Message):
    """Стартовое сообщение"""
    user_id = message.from_user.id
    await reset_state_user(user_id, clear_data=True)
    user_data = await get_data("users", user_id=user_id)

    if not user_data:
        user_data = (
            user_id,
            message.from_user.first_name,
            message.from_user.username,
            message.date,
        )
        await add_new_data(
            "users",
            user_data,
            start_index=0,
        )

    await dp.bot.send_message(
        user_id,
        (
            "Важный дисклеймер: здесь нет индивидуальных инвестиционных рекомендаций (ИИР), "
            "всю информацию необходимо использовать с личной ответственностью.\n"
            "\n"
            "Информационный канал по обновлениям бота - https://t.me/+MQ6Y0CBYEG1lYjJi \n"
            "\n"
            "Любые вопросы и предложения - @hamster93_support_bot \n"
            "\n"
            "Для продолжения нажмите кнопку ниже."
        ),
        disable_web_page_preview=True,
        reply_markup=await keyboards.users.start(user_id),
    )

    if "data" in message:
        await message.answer()
