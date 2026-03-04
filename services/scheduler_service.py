"""Scheduled jobs for background tasks."""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from typing import List
import logging

from database import SessionLocal
from models.opportunity import Opportunity
from models.tracking import TrackedOpportunity
from models.reminder import Reminder
from services.notification_service import NotificationService
from services.recommendation_service import RecommendationEngine

logger = logging.getLogger(__name__)


class SchedulerService:
    """Service for managing scheduled background jobs."""
    
    @staticmethod
    def process_deadline_reminders():
        """
        Process deadline reminders for tracked opportunities.
        Sends reminders at 7 days and 24 hours before deadline.
        Should run every hour.
        """
        db = SessionLocal()
        try:
            notification_service = NotificationService(db)
            now = datetime.utcnow()
            
            # Find reminders that need to be sent
            pending_reminders = db.query(Reminder).filter(
                Reminder.sent == False,
                Reminder.scheduled_time <= now
            ).all()
            
            logger.info(f"Processing {len(pending_reminders)} pending reminders")
            
            for reminder in pending_reminders:
                try:
                    # Get opportunity details
                    opportunity = db.query(Opportunity).filter(
                        Opportunity.id == reminder.opportunity_id
                    ).first()
                    
                    if not opportunity:
                        logger.warning(f"Opportunity {reminder.opportunity_id} not found for reminder {reminder.id}")
                        reminder.sent = True
                        continue
                    
                    # Calculate time until deadline
                    time_until = opportunity.deadline - now
                    days_until = time_until.days
                    hours_until = time_until.total_seconds() / 3600
                    
                    # Determine reminder type
                    if days_until >= 6 and days_until <= 8:
                        reminder_type = "7_day"
                    elif hours_until >= 20 and hours_until <= 28:
                        reminder_type = "24_hour"
                    else:
                        reminder_type = "general"
                    
                    # Send notification
                    success = notification_service.send_deadline_reminder(
                        reminder.user_id,
                        opportunity,
                        reminder_type
                    )
                    
                    if success:
                        reminder.sent = True
                        logger.info(f"Sent reminder {reminder.id} for opportunity {opportunity.id}")
                    else:
                        logger.error(f"Failed to send reminder {reminder.id}")
                
                except Exception as e:
                    logger.error(f"Error processing reminder {reminder.id}: {str(e)}")
            
            db.commit()
            logger.info("Deadline reminder processing completed")
        
        except Exception as e:
            logger.error(f"Error in deadline reminder job: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    @staticmethod
    def archive_expired_opportunities():
        """
        Archive opportunities that have passed their deadline.
        Should run daily at midnight.
        """
        db = SessionLocal()
        try:
            now = datetime.utcnow()
            
            # Find expired opportunities
            expired = db.query(Opportunity).filter(
                Opportunity.deadline < now,
                Opportunity.status == "active"
            ).all()
            
            logger.info(f"Archiving {len(expired)} expired opportunities")
            
            for opportunity in expired:
                opportunity.status = "archived"
            
            # Mark tracked opportunities as expired
            expired_ids = [opp.id for opp in expired]
            if expired_ids:
                db.query(TrackedOpportunity).filter(
                    TrackedOpportunity.opportunity_id.in_(expired_ids)
                ).update({"is_expired": True}, synchronize_session=False)
            
            db.commit()
            logger.info("Opportunity archival completed")
        
        except Exception as e:
            logger.error(f"Error in archival job: {str(e)}")
            db.rollback()
        finally:
            db.close()
    
    @staticmethod
    def update_recommendations():
        """
        Recalculate recommendations for all users.
        Should run every 6 hours.
        """
        db = SessionLocal()
        try:
            from models.user import User
            
            # Get all users
            users = db.query(User).all()
            logger.info(f"Updating recommendations for {len(users)} users")
            
            recommendation_engine = RecommendationEngine(db)
            
            for user in users:
                try:
                    # Generate fresh recommendations (will update cache)
                    recommendations = recommendation_engine.generate_recommendations(
                        user.id,
                        limit=20
                    )
                    logger.debug(f"Updated {len(recommendations)} recommendations for user {user.id}")
                
                except Exception as e:
                    logger.error(f"Error updating recommendations for user {user.id}: {str(e)}")
            
            logger.info("Recommendation update completed")
        
        except Exception as e:
            logger.error(f"Error in recommendation update job: {str(e)}")
        finally:
            db.close()
    
    @staticmethod
    def cleanup_old_reminders():
        """
        Clean up old sent reminders (older than 30 days).
        Should run daily.
        """
        db = SessionLocal()
        try:
            cutoff_date = datetime.utcnow() - timedelta(days=30)
            
            deleted = db.query(Reminder).filter(
                Reminder.sent == True,
                Reminder.scheduled_time < cutoff_date
            ).delete()
            
            db.commit()
            logger.info(f"Cleaned up {deleted} old reminders")
        
        except Exception as e:
            logger.error(f"Error in reminder cleanup job: {str(e)}")
            db.rollback()
        finally:
            db.close()
