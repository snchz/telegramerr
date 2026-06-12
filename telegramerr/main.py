import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from telegramerr.config import settings
from telegramerr.handlers.commands import router as commands_router
from telegramerr.handlers.search import router as search_router
from telegramerr.handlers.requests import router as requests_router
from telegramerr.handlers.trending import router as trending_router
from telegramerr.api.overseerr_client import overseerr
from telegramerr.locales.i18n import t

numeric_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)
logging.basicConfig(
    level=numeric_level,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()

notified_requests = set() 
first_run = True

async def polling_task():
    global first_run
    while True:
        try:
            for tg_user_id, ov_user_id in settings.get_user_mapping.items():
                data = await overseerr.get_requests()
                results = data.get("results", [])
                for req in results:
                    requested_by = req.get("requestedBy", {}).get("id")
                    if requested_by == ov_user_id:
                        req_id = req.get("id")
                        media = req.get("media", {})
                        status = media.get("status")
                        
                        if status == 5 and req_id not in notified_requests:
                            notified_requests.add(req_id)
                            
                            if not first_run:
                                media_type = media.get("mediaType")
                                tmdb_id = media.get("tmdbId")
                                title = "Media"
                                if media_type and tmdb_id:
                                    try:
                                        title = await overseerr.get_media_title(media_type, tmdb_id)
                                    except Exception as e:
                                        logging.error(f"Error fetching title: {e}")
                                        
                                msg = t("polling_notification", title=title)
                                try:
                                    await bot.send_message(chat_id=tg_user_id, text=msg)
                                except Exception as e:
                                    logging.error(f"Error sending notification to {tg_user_id}: {e}")
            first_run = False
        except Exception as e:
            logging.error(f"Error in polling task: {e}")
            
        await asyncio.sleep(settings.POLLING_INTERVAL)

async def main():
    dp.include_router(commands_router)
    dp.include_router(search_router)
    dp.include_router(requests_router)
    dp.include_router(trending_router)
    
    # Start polling task in background
    asyncio.create_task(polling_task())
    
    logging.info("Telegramerr bot started!")
    # Eliminar cualquier webhook huérfano que cause conflictos con el polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
