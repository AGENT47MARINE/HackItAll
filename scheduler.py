"""Background scheduler for running periodic jobs."""
import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from services.scheduler_service import SchedulerService

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_scheduler():
    """Create and configure the background scheduler."""
    scheduler = BackgroundScheduler()
    
    # Job 1: Process deadline reminders every hour
    scheduler.add_job(
        SchedulerService.process_deadline_reminders,
        trigger=IntervalTrigger(hours=1),
        id='deadline_reminders',
        name='Process deadline reminders',
        replace_existing=True
    )
    logger.info("Scheduled job: Process deadline reminders (every hour)")
    
    # Job 2: Archive expired opportunities daily at midnight
    scheduler.add_job(
        SchedulerService.archive_expired_opportunities,
        trigger=CronTrigger(hour=0, minute=0),
        id='archive_opportunities',
        name='Archive expired opportunities',
        replace_existing=True
    )
    logger.info("Scheduled job: Archive expired opportunities (daily at midnight)")
    
    # Job 3: Update recommendations every 6 hours
    scheduler.add_job(
        SchedulerService.update_recommendations,
        trigger=IntervalTrigger(hours=6),
        id='update_recommendations',
        name='Update user recommendations',
        replace_existing=True
    )
    logger.info("Scheduled job: Update recommendations (every 6 hours)")
    
    # Job 4: Cleanup old reminders daily at 2 AM
    scheduler.add_job(
        SchedulerService.cleanup_old_reminders,
        trigger=CronTrigger(hour=2, minute=0),
        id='cleanup_reminders',
        name='Cleanup old reminders',
        replace_existing=True
    )
    logger.info("Scheduled job: Cleanup old reminders (daily at 2 AM)")
    
    return scheduler


def start_scheduler():
    """Start the background scheduler."""
    scheduler = create_scheduler()
    scheduler.start()
    logger.info("Background scheduler started")
    return scheduler


if __name__ == "__main__":
    # For testing - run scheduler in foreground
    import time
    
    scheduler = start_scheduler()
    
    try:
        # Keep the script running
        while True:
            time.sleep(60)
    except (KeyboardInterrupt, SystemExit):
        scheduler.shutdown()
        logger.info("Scheduler shut down")
