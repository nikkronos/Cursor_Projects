"""
User handlers for Копия иксуюемся.
Minimal handlers (no subscription system - access is granted manually).
"""
from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Handle /start command."""
    await message.answer(
        "Привет. Это бот для копирования сообщений из канала. "
        "Доступ к целевому каналу выдаётся вручную."
    )
