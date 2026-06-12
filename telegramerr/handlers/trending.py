from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from telegramerr.api.overseerr_client import overseerr
from telegramerr.locales.i18n import t
from telegramerr.config import settings
from telegramerr.handlers.search import user_search_cache, send_search_result
import logging

router = Router()

@router.message(Command("trending", "discover"))
async def cmd_trending(message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in settings.get_user_mapping and chat_id not in settings.get_user_mapping:
        await message.answer(t("unauthorized", user_id=f"Usuario: {user_id} | Grupo: {chat_id}"))
        return
        
    status_msg = await message.answer(f"🔥 Buscando tendencias...")
    
    try:
        data = await overseerr.get_trending()
        results = data.get("results", [])
        user_search_cache[chat_id] = {
            "query": "Trending",
            "results": results,
            "index": 0,
            "total_pages": data.get("totalPages", 1)
        }
        await status_msg.delete()
        await message.answer(t("trending_title"), parse_mode="HTML")
        await send_search_result(message, chat_id)
    except Exception as e:
        logging.error(f"Error fetching trending: {e}")
        await status_msg.edit_text(f"❌ Error buscando tendencias: {str(e)}")
