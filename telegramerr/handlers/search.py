import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton, URLInputFile
from aiogram.filters import Command
from telegramerr.api.overseerr_client import overseerr
from telegramerr.locales.i18n import t
from telegramerr.config import settings

router = Router()

user_search_cache = {}

def get_media_status_emoji(media_info: dict) -> str:
    if not media_info:
        return ""
    status = media_info.get("status", 1) # 1 is UNKNOWN/NOT_AVAILABLE usually
    if status == 5: # AVAILABLE
        return t("status_available")
    elif status in (4, 3): # PROCESSING / PARTIALLY_AVAILABLE
        return t("status_processing")
    elif status == 2: # PENDING
        return t("status_pending")
    return ""

def is_requestable(media_info: dict) -> bool:
    if not media_info:
        return True
    status = media_info.get("status", 1)
    if status in (2, 3, 4, 5):
        return False
    return True

async def send_search_result(message: Message, chat_id: int, edit_message=False):
    cache = user_search_cache.get(chat_id)
    if not cache or not cache["results"]:
        text = t("no_results", query=cache.get("query", ""))
        if edit_message and isinstance(message, CallbackQuery):
            await message.message.edit_text(text)
        else:
            await message.answer(text)
        return

    index = cache["index"]
    result = cache["results"][index]
    
    media_type = result.get("mediaType")
    title = result.get("title") or result.get("name")
    year = ""
    if result.get("releaseDate"):
        year = result.get("releaseDate")[:4]
    elif result.get("firstAirDate"):
        year = result.get("firstAirDate")[:4]
        
    poster_path = result.get("posterPath")
    overview = result.get("overview", "")[:300] + "..." if result.get("overview") else ""
    media_id = result.get("id")
    
    type_str = t("type_movie") if media_type == "movie" else t("type_tv")
    media_info = result.get("mediaInfo")
    status_str = get_media_status_emoji(media_info)
    
    text = f"<b>{title}</b> ({year})\n"
    text += f"{type_str}\n\n"
    text += f"{overview}\n\n"
    if status_str:
        text += f"<b>{status_str}</b>"

    keyboard = []
    nav_row = []
    if index > 0:
        nav_row.append(InlineKeyboardButton(text=t("btn_prev"), callback_data=f"search_nav:prev"))
    if index < len(cache["results"]) - 1:
        nav_row.append(InlineKeyboardButton(text=t("btn_next"), callback_data=f"search_nav:next"))
    if nav_row:
        keyboard.append(nav_row)
        
    if is_requestable(media_info):
        keyboard.append([InlineKeyboardButton(text=t("btn_request"), callback_data=f"req:{media_type}:{media_id}")])
        
    markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    if poster_path:
        photo_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
        if edit_message and isinstance(message, CallbackQuery):
            await message.message.delete()
            await message.message.answer_photo(URLInputFile(photo_url), caption=text, reply_markup=markup, parse_mode="HTML")
        else:
            await message.answer_photo(URLInputFile(photo_url), caption=text, reply_markup=markup, parse_mode="HTML")
    else:
        if edit_message and isinstance(message, CallbackQuery):
            await message.message.edit_text(text, reply_markup=markup, parse_mode="HTML")
        else:
            await message.answer(text, reply_markup=markup, parse_mode="HTML")

@router.message(Command("search"))
async def cmd_search(message: Message):
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        await message.answer(t("search_prompt"))
        return
        
    query = args[1]
    user_id = message.from_user.id
    chat_id = message.chat.id
    if user_id not in settings.get_user_mapping and chat_id not in settings.get_user_mapping:
        await message.answer(t("unauthorized", user_id=f"Usuario: {user_id} | Grupo: {chat_id}"))
        return
        
    status_msg = await message.answer(f"🔍 Buscando '{query}'...")
    
    try:
        data = await overseerr.search(query)
        results = data.get("results", [])
        user_search_cache[chat_id] = {
            "query": query,
            "results": results,
            "index": 0,
            "total_pages": data.get("totalPages", 1)
        }
        await status_msg.delete()
        await send_search_result(message, chat_id)
    except Exception as e:
        await status_msg.edit_text(f"❌ Error buscando: {str(e)}")

@router.callback_query(F.data.startswith("search_nav:"))
async def search_nav(callback: CallbackQuery):
    action = callback.data.split(":")[1]
    chat_id = callback.message.chat.id
    
    if chat_id not in user_search_cache:
        await callback.answer("Búsqueda expirada", show_alert=True)
        return
        
    cache = user_search_cache[chat_id]
    if action == "prev" and cache["index"] > 0:
        cache["index"] -= 1
    elif action == "next" and cache["index"] < len(cache["results"]) - 1:
        cache["index"] += 1
        
    await send_search_result(callback, chat_id, edit_message=True)
    await callback.answer()
