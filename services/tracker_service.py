"""Application tracker service for managing tracked opportunities."""
from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.tracking import TrackedOpportunity
from models.opportunity import Opportunity
from utils.formatters import ResponseFormatter


class TrackerService:
    """Service for tracking opportunities and managing deadlines."""
    
    def __init__(self, db_session: Session):
        """Initialize the tracker service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def scrape_and_track_opportunity(self, user_id: str, url: str) -> Dict[str, Any]:
        """Scrape an external URL, save it to DB (if new), and track it.

        Args:
            user_id: User ID tracking the opportunity
            url: URL to scrape and track

        Returns:
            Tracked opportunity data
        """
        from services.scraper_service import ScraperService

        base_url = url.rstrip('/')
        existing_opp = self.db.query(Opportunity).filter(
            Opportunity.application_link.ilike(f"%{base_url}%")
        ).first()

        if existing_opp:
            opportunity_to_track = existing_opp
        else:
            scraper = ScraperService()
            scraped_data = scraper.scrape_url(url)

            opportunity_to_track = Opportunity(
                title=scraped_data["title"],
                description=scraped_data["description"],
                type=scraped_data["type"],
                image_url=scraped_data.get("image_url"),
                deadline=datetime.utcnow(),
                application_link=scraped_data["application_link"],
                tags=scraped_data["tags"],
                required_skills=scraped_data["required_skills"],
                status="active"
            )
            self.db.add(opportunity_to_track)
            self.db.commit()
            self.db.refresh(opportunity_to_track)

        return self.save_opportunity(user_id, opportunity_to_track.id)

    def save_opportunity(self, user_id: str, opportunity_id: str) -> Dict[str, Any]:
        """Save an opportunity to the user's tracked list.
        
        Automatically schedules deadline reminders (7 days and 24 hours before deadline).
        
        Args:
            user_id: User ID
            opportunity_id: Opportunity ID to track
            
        Returns:
            Dictionary containing tracked opportunity data
            
        Raises:
            ValueError: If opportunity doesn't exist
            IntegrityError: If opportunity is already tracked by user
        """
        from services.notification_service import NotificationService
        
        # Verify opportunity exists
        opportunity = self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id
        ).first()
        
        if not opportunity:
            raise ValueError(f"Opportunity with id {opportunity_id} not found")
        
        # Check if deadline has already passed
        is_expired = opportunity.deadline < datetime.utcnow()
        
        # Create tracked opportunity
        tracked = TrackedOpportunity(
            user_id=user_id,
            opportunity_id=opportunity_id,
            is_expired=is_expired
        )
        
        try:
            self.db.add(tracked)
            
            # Increment the tracked count for the Trending Algorithm
            opportunity.tracked_count += 1
            
            self.db.commit()
            
            # Schedule deadline reminders if not expired
            if not is_expired:
                notification_service = NotificationService(self.db)
                notification_service.schedule_deadline_reminders(
                    user_id=user_id,
                    opportunity_id=opportunity_id,
                    deadline=opportunity.deadline
                )
            
            return self._format_tracked_opportunity(tracked, opportunity)
            
        except IntegrityError as e:
            self.db.rollback()
            raise IntegrityError(
                "Opportunity already tracked by user",
                params=None,
                orig=e.orig
            )
    
    def get_tracked_opportunities(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all tracked opportunities for a user, sorted by deadline (ascending).
        
        Args:
            user_id: User ID
            
        Returns:
            List of dictionaries containing tracked opportunity data,
            sorted by deadline date (earliest first)
        """
        # Query tracked opportunities with their opportunity details
        tracked_list = self.db.query(TrackedOpportunity, Opportunity).join(
            Opportunity,
            TrackedOpportunity.opportunity_id == Opportunity.id
        ).filter(
            TrackedOpportunity.user_id == user_id
        ).order_by(
            Opportunity.deadline.asc()  # Sort by deadline ascending (earliest first)
        ).all()
        
        # Format results
        result = []
        for tracked, opportunity in tracked_list:
            result.append(self._format_tracked_opportunity(tracked, opportunity))
        
        return result
    
    def remove_tracked_opportunity(self, user_id: str, opportunity_id: str) -> bool:
        """Remove a tracked opportunity from the user's list.
        
        Also cancels any scheduled reminders for this opportunity.
        
        Args:
            user_id: User ID
            opportunity_id: Opportunity ID to remove
            
        Returns:
            True if removed successfully, False if not found
        """
        from services.notification_service import NotificationService
        
        tracked = self.db.query(TrackedOpportunity).filter(
            TrackedOpportunity.user_id == user_id,
            TrackedOpportunity.opportunity_id == opportunity_id
        ).first()
        
        if not tracked:
            return False
        
        self.db.delete(tracked)
        
        # Decrement the tracked count
        opportunity = self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id
        ).first()
        if opportunity and opportunity.tracked_count > 0:
            opportunity.tracked_count -= 1
        
        # Cancel any scheduled reminders
        notification_service = NotificationService(self.db)
        notification_service.cancel_opportunity_reminders(user_id, opportunity_id)
            
        self.db.commit()
        
        return True
    
    def mark_as_expired(self, opportunity_id: str) -> int:
        """Mark all tracked instances of an opportunity as expired.
        
        This is typically called when an opportunity's deadline has passed.
        
        Args:
            opportunity_id: Opportunity ID to mark as expired
            
        Returns:
            Number of tracked opportunities marked as expired
        """
        # Update all tracked instances of this opportunity
        count = self.db.query(TrackedOpportunity).filter(
            TrackedOpportunity.opportunity_id == opportunity_id,
            TrackedOpportunity.is_expired == False
        ).update(
            {"is_expired": True},
            synchronize_session=False
        )
        
        self.db.commit()
        
        return count
    
    def _format_tracked_opportunity(self, tracked: TrackedOpportunity, 
                                   opportunity: Opportunity) -> Dict[str, Any]:
        """Format tracked opportunity data for response.
        
        Args:
            tracked: TrackedOpportunity model instance
            opportunity: Opportunity model instance
            
        Returns:
            Dictionary containing formatted tracked opportunity data
        """
        # Use centralized formatter
        opportunity_data = ResponseFormatter.format_opportunity_response(opportunity)
        
        return {
            "user_id": tracked.user_id,
            "opportunity_id": tracked.opportunity_id,
            "saved_at": tracked.saved_at.isoformat(),
            "is_expired": tracked.is_expired,
            "opportunity": opportunity_data
        }
