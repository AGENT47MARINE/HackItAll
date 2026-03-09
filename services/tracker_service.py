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
        from services.gamification_service import GamificationService
        
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
            
            # AWARD XP: 10 XP for tracking an opportunity
            gamification = GamificationService(self.db)
            gamification.award_xp(user_id, "track", reference_id=opportunity_id)
            
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
            Opportunity.deadline.asc()
        ).all()

        # Batch fetch team memberships to avoid N+1
        from models.team import Team, TeamMember
        user_team_members = self.db.query(TeamMember).join(Team).filter(
            TeamMember.user_id == user_id
        ).all()
        
        # Map opportunity_id -> TeamMember
        teams_map = {tm.team.opportunity_id: tm for tm in user_team_members}
        
        # Format results
        result = []
        for tracked, opportunity in tracked_list:
            team_member = teams_map.get(opportunity.id)
            result.append(self._format_tracked_opportunity(tracked, opportunity, team_member))
        
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
                                   opportunity: Opportunity,
                                   team_member: Optional[Any] = None) -> Dict[str, Any]:
        """Format tracked opportunity data for response.
        
        Args:
            tracked: TrackedOpportunity model instance
            opportunity: Opportunity model instance
            team_member: Optional TeamMember model instance if already fetched
            
        Returns:
            Dictionary containing formatted tracked opportunity data
        """
        # If team_member wasn't provided, try to fetch it (fallback)
        if team_member is None:
            from models.team import Team, TeamMember
            team_member = self.db.query(TeamMember).join(Team).filter(
                Team.opportunity_id == opportunity.id,
                TeamMember.user_id == tracked.user_id
            ).first()

        team_status = "solo"
        team_id = None
        if team_member:
            team_status = "leader" if team_member.role == "leader" else "member"
            team_id = team_member.team_id

        # Use centralized formatter
        from utils.formatters import ResponseFormatter
        opportunity_data = ResponseFormatter.format_opportunity_response(opportunity)

        # Fetch latest status/participation record
        from models.tracking import ParticipationHistory
        latest_participation = self.db.query(ParticipationHistory).filter(
            ParticipationHistory.user_id == tracked.user_id,
            ParticipationHistory.opportunity_id == opportunity.id
        ).order_by(ParticipationHistory.created_at.desc()).first()

        status = "saved"
        current_round = "1"
        participation_id = None
        if latest_participation:
            status = latest_participation.status
            current_round = latest_participation.current_round
            participation_id = latest_participation.id

        return {
            "user_id": tracked.user_id,
            "opportunity_id": tracked.opportunity_id,
            "participation_id": participation_id,
            "saved_at": tracked.saved_at.isoformat(),
            "is_expired": tracked.is_expired,
            "team_status": team_status,
            "team_id": team_id,
            "status": status,
            "current_round": current_round,
            "opportunity": opportunity_data
        }
