from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from config.db import get_db
from services.trash_service import auto_permanent_delete
from utils.logger import get_logger

logger = get_logger("scheduler")

def run_auto_delete():
    try:
        db = next(get_db())
        auto_permanent_delete(db)
    except Exception:
        logger.exception("Error running auto permanent delete")

def start_scheduler():
    logger.info("Starting Trash Scheduler...")

    run_auto_delete()

    scheduler = BackgroundScheduler()
    scheduler.add_job(run_auto_delete, "cron", hour=0, minute=0)
    scheduler.start()