from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from telegramerr.api.overseerr_client import overseerr
from telegramerr.locales.i18n import t
from telegramerr.config import settings

router = Router()

@router.callback_query(F.data.startswith("req:"))
async def handle_request(callback: CallbackQuery):
    _, media_type, media_id_str = callback.data.split(":")
    media_id = int(media_id_str)
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    
    overseerr_user_id = settings.get_user_mapping.get(user_id) or settings.get_user_mapping.get(chat_id)
    if not overseerr_user_id:
        await callback.answer(t("unauthorized", user_id=f"User: {user_id} Chat: {chat_id}"), show_alert=True)
        return

    if media_type == "movie":
        success = await overseerr.request_media("movie", media_id, None, overseerr_user_id)
        if success:
            await callback.answer(t("request_success", title="Película"), show_alert=True)
        else:
            await callback.answer(t("request_failed"), show_alert=True)
    elif media_type == "tv":
        try:
            details = await overseerr.get_tv_details(media_id)
            seasons = details.get("seasons", [])
            keyboard = []
            keyboard.append([InlineKeyboardButton(text=t("all_seasons"), callback_data=f"reqtv:{media_id}:all")])
            row = []
            for s in seasons:
                s_num = s.get("seasonNumber")
                if s_num is not None and s_num > 0: 
                    row.append(InlineKeyboardButton(text=t("season_x", season=s_num), callback_data=f"reqtv:{media_id}:{s_num}"))
                    if len(row) == 3:
                        keyboard.append(row)
                        row = []
            if row:
                keyboard.append(row)
            
            title = details.get("name", "Serie")
            markup = InlineKeyboardMarkup(inline_keyboard=keyboard)
            await callback.message.answer(t("select_season", title=title), reply_markup=markup)
            await callback.answer()
        except Exception as e:
            print(f"Error fetching TV details: {e}")
            await callback.answer("Error obteniendo detalles de la serie", show_alert=True)

@router.callback_query(F.data.startswith("reqtv:"))
async def handle_tv_request(callback: CallbackQuery):
    _, media_id_str, season_choice = callback.data.split(":")
    media_id = int(media_id_str)
    user_id = callback.from_user.id
    chat_id = callback.message.chat.id
    
    overseerr_user_id = settings.get_user_mapping.get(user_id) or settings.get_user_mapping.get(chat_id)
    if not overseerr_user_id:
        await callback.answer(t("unauthorized", user_id=f"User: {user_id} Chat: {chat_id}"), show_alert=True)
        return
        
    seasons = []
    if season_choice != "all":
        seasons = [int(season_choice)]
        
    success = await overseerr.request_media("tv", media_id, seasons if seasons else None, overseerr_user_id)
    if success:
        await callback.answer(t("request_success", title="Serie"), show_alert=True)
        await callback.message.delete()
    else:
        await callback.answer(t("request_failed"), show_alert=True)
