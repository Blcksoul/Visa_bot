"""
visa-bot/scheduler.py
APScheduler async background worker — runs slot-check jobs every CHECK_INTERVAL seconds.
"""

import logging

from aiogram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger

from config import settings
from database import async_session, get_active_applicants
from services.booking_service import attempt_booking
from services.vfs_service import check_vfs_slots
from services.tls_service import check_tls_slots

logger = logging.getLogger(__name__)


async def check_all_slots(bot: Bot) -> None:
    """
    Main scheduled task:
    1. Load all active applicants with auto_book=True.
    2. For each, call the appropriate scraper to detect available slots.
    3. If a slot is found, attempt automatic booking and notify the user.
    """
    logger.info("Running slot check …")
    async with async_session() as session:
        applicants = await get_active_applicants(session)

    for applicant in applicants:
        try:
            if applicant.provider == "vfs":
                slots = await check_vfs_slots(applicant)
            else:
                slots = await check_tls_slots(applicant)

            if not slots:
                logger.debug("No slots for applicant %s", applicant.id)
                continue

            logger.info("Slot found for applicant %s: %s", applicant.id, slots[0])

            # Notify the user immediately
            await bot.send_message(
                applicant.user_id,
                f"🟢 Slot found for <b>{applicant.full_name}</b>!\n"
                f"📅 Date: <b>{slots[0]['date']}</b>\n"
                f"🕐 Time: <b>{slots[0]['time']}</b>\n"
                f"📍 Centre: <b>{applicant.visa_center}</b>\n\n"
                "⏳ Attempting automatic booking …",
                parse_mode="HTML",
            )

            # Attempt booking
            result = await attempt_booking(applicant, slots[0])

            if result["success"]:
                await bot.send_message(
                    applicant.user_id,
                    f"✅ <b>Booking confirmed!</b>\n"
                    f"👤 Applicant: {applicant.full_name}\n"
                    f"📅 {slots[0]['date']} at {slots[0]['time']}\n"
                    f"📍 {applicant.visa_center}\n"
                    f"🔖 Ref: <code>{result.get('ref', 'N/A')}</code>",
                    parse_mode="HTML",
                )
            else:
                await bot.send_message(
                    applicant.user_id,
                    f"❌ <b>Booking failed</b> for {applicant.full_name}.\n"
                    f"Reason: {result.get('error', 'Unknown error')}\n"
                    "The bot will retry on the next check.",
                    parse_mode="HTML",
                )

        except Exception as exc:
            logger.exception("Error processing applicant %s: %s", applicant.id, exc)


async def start_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone="UTC")
    scheduler.add_job(
        check_all_slots,
        trigger=IntervalTrigger(seconds=settings.CHECK_INTERVAL),
        args=[bot],
        id="slot_check",
        replace_existing=True,
        max_instances=1,  # never overlap
    )
    scheduler.start()
    return scheduler
