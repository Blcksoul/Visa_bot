"""
visa-bot/bot.py
Main entry point — registers all handlers and starts the bot + scheduler.
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import settings
from database import init_db
from scheduler import start_scheduler
from handlers import start, applicants, booking, admin

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


async def main() -> None:
    logger.info("Initialising database …")
    await init_db()

    bot = Bot(token=settings.TELEGRAM_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    # ── Register routers ────────────────────────────────────────────────────
    dp.include_router(start.router)
    dp.include_router(applicants.router)
    dp.include_router(booking.router)
    dp.include_router(admin.router)

    # ── Start background scheduler ──────────────────────────────────────────
    scheduler = await start_scheduler(bot)
    logger.info("Scheduler started — checking slots every %s seconds", settings.CHECK_INTERVAL)

    logger.info("Bot is running …")
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown(wait=False)
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
