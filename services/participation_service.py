"""Participation history service for managing user participation records."""
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from models.tracking import ParticipationHistory
from models.opportunity import Opportunity


class ParticipationService:
    """Service for managing user participation history."""
    
    VALID_STATUSES = ["applied", "submitted", "in_review", "accepted", "rejected", "completed"]
    
    def __init__(self, db_session: Session):
        """Initialize the participation service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def add_participation(
        self,
        user_id: str,
        opportunity_id: str,
        status: str,
        current_round: Optional[str] = "1",
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a participation history entry.
        
        Args:
            user_id: User ID
            opportunity_id: Opportunity ID
            status: Participation status (applied, accepted, rejected, completed)
            notes: Optional notes about the participation
            
        Returns:
            Dictionary containing participation history data
            
        Raises:
            ValueError: If status is invalid or opportunity doesn't exist
        """
        # Validate status
        if status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}"
            )
        
        # Verify opportunity exists
        opportunity = self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id
        ).first()
        
        if not opportunity:
            raise ValueError(f"Opportunity with id {opportunity_id} not found")
        
        from services.gamification_service import GamificationService
        
        # Create participation entry
        participation = ParticipationHistory(
            user_id=user_id,
            opportunity_id=opportunity_id,
            status=status,
            current_round=current_round,
            notes=notes
        )
        
        self.db.add(participation)
        
        # Increment the participant count for the Trending Algorithm
        opportunity.participant_count += 1
        
        # AWARD XP: 25 for applied, 50 for accepted, 100 for completed
        gamification = GamificationService(self.db)
        gamification.award_xp(user_id, status, reference_id=f"{opportunity_id}_{status}")
        
        self.db.commit()
        self.db.refresh(participation)
        
        # Reschedule reminders based on new status
        try:
            from services.notification_service import NotificationService
            notif_service = NotificationService(self.db)
            notif_service.cancel_opportunity_reminders(user_id, opportunity_id)
            if status not in ["completed", "rejected"]:
                notif_service.schedule_deadline_reminders(user_id, opportunity_id, opportunity.deadline)
        except Exception as e:
            print(f"[ParticipationService] Failed to reschedule reminders: {e}")
        
        return self._format_participation(participation)
    
    def update_participation(
        self,
        participation_id: str,
        user_id: str,
        status: Optional[str] = None,
        current_round: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Update a participation history entry.
        
        Args:
            participation_id: Participation history entry ID
            user_id: User ID (for authorization)
            status: Updated status (optional)
            notes: Updated notes (optional)
            
        Returns:
            Dictionary containing updated participation data, or None if not found
            
        Raises:
            ValueError: If status is invalid
        """
        from services.gamification_service import GamificationService
        
        # Validate status if provided
        if status is not None and status not in self.VALID_STATUSES:
            raise ValueError(
                f"Invalid status '{status}'. Must be one of: {', '.join(self.VALID_STATUSES)}"
            )
        
        # Find participation entry
        participation = self.db.query(ParticipationHistory).filter(
            ParticipationHistory.id == participation_id,
            ParticipationHistory.user_id == user_id
        ).first()
        
        if not participation:
            return None
        
        # Update fields
        if status is not None:
            participation.status = status
            # AWARD XP: 25 for applied, 50 for accepted, 100 for completed
            gamification = GamificationService(self.db)
            gamification.award_xp(user_id, status, reference_id=f"{participation.opportunity_id}_{status}")
            
        if current_round is not None:
            participation.current_round = current_round
            
        if notes is not None:
            participation.notes = notes
        
        self.db.commit()
        self.db.refresh(participation)
        
        # Reschedule reminders if status or round changed
        if status is not None or current_round is not None:
            try:
                from services.notification_service import NotificationService
                from models.opportunity import Opportunity
                notif_service = NotificationService(self.db)
                opportunity = self.db.query(Opportunity).filter(Opportunity.id == participation.opportunity_id).first()
                if opportunity:
                    notif_service.cancel_opportunity_reminders(user_id, participation.opportunity_id)
                    if status not in ["completed", "rejected"]:
                        notif_service.schedule_deadline_reminders(user_id, participation.opportunity_id, opportunity.deadline)
            except Exception as e:
                print(f"[ParticipationService] Failed to reschedule reminders: {e}")
        
        return self._format_participation(participation)
    
    def get_participation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all participation history entries for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            List of dictionaries containing participation history data,
            ordered by created_at (most recent first)
        """
        # Query participation history with opportunity details
        history = self.db.query(ParticipationHistory, Opportunity).join(
            Opportunity,
            ParticipationHistory.opportunity_id == Opportunity.id
        ).filter(
            ParticipationHistory.user_id == user_id
        ).order_by(
            ParticipationHistory.created_at.desc()
        ).all()
        
        # Format results
        result = []
        for participation, opportunity in history:
            entry = self._format_participation(participation)
            entry["opportunity"] = {
                "id": opportunity.id,
                "title": opportunity.title,
                "type": opportunity.type,
                "deadline": opportunity.deadline.isoformat(),
                "current_round": participation.current_round
            }
            result.append(entry)
        
        return result
    
    def _format_participation(self, participation: ParticipationHistory) -> Dict[str, Any]:
        """Format participation history data for response.
        
        Args:
            participation: ParticipationHistory model instance
            
        Returns:
            Dictionary containing formatted participation data
        """
        return {
            "id": participation.id,
            "user_id": participation.user_id,
            "opportunity_id": participation.opportunity_id,
            "status": participation.status,
            "current_round": participation.current_round,
            "notes": participation.notes,
            "created_at": participation.created_at.isoformat()
        }
