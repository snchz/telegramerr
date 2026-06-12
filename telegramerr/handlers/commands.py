from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from telegramerr.locales.i18n import t
from telegramerr.config import settings

router = Router()

@router.message(Command("start", "help"))
async def cmd_start(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    
    if user_id not in settings.get_user_mapping and chat_id not in settings.get_user_mapping:
        await message.answer(t("unauthorized", user_id=f"Usuario: {user_id} | Grupo: {chat_id}"))
        return
    await message.answer(t("welcome"))
