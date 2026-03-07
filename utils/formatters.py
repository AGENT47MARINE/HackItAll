"""Response formatters for API endpoints."""
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class ResponseFormatter:
    """Utility class for formatting API responses."""
    
    @staticmethod
    def format_profile_response(user, profile, participation_history: List = None) -> Dict[str, Any]:
        """Format profile data for API response.
        
        Ensures all profile fields are included in the response with proper formatting.
        
        Args:
            user: User model instance
            profile: Profile model instance
            participation_history: Optional list of participation history entries
            
        Returns:
            Dictionary containing formatted profile data
        """
        if not user or not profile:
            return None
        
        # Parse JSON fields
        interests = json.loads(profile.interests) if isinstance(profile.interests, str) else profile.interests
        skills = json.loads(profile.skills) if isinstance(profile.skills, str) else profile.skills
        
        # Calculate activity streak (days with participation)
        activity_streak = 0
        if participation_history:
            # Simple streak calculation based on consecutive days with activity
            dates = sorted(set(entry.get('created_at', '')[:10] for entry in participation_history))
            if dates:
                current_streak = 1
                for i in range(1, len(dates)):
                    prev_date = datetime.fromisoformat(dates[i-1])
                    curr_date = datetime.fromisoformat(dates[i])
                    diff = (curr_date - prev_date).days
                    if diff == 1:
                        current_streak += 1
                    elif diff > 1:
                        current_streak = 1
                activity_streak = current_streak
        
        return {
            "id": user.id,
            "email": user.email,
            "username": getattr(user, 'username', None),
            "phone": user.phone,
            "interests": interests if isinstance(interests, list) else [],
            "skills": skills if isinstance(skills, list) else [],
            "education_level": profile.education_level,
            "notification_email": profile.notification_email,
            "notification_sms": profile.notification_sms,
            "low_bandwidth_mode": profile.low_bandwidth_mode,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": profile.updated_at.isoformat() if profile.updated_at else None,
            "participation_history": participation_history or [],
            "activity_streak": activity_streak
        }
    
    @staticmethod
    def format_opportunity_response(opportunity, tracked_count: int = 0, participant_count: int = 0, source_registration_count: int = 0) -> Dict[str, Any]:
        """Format opportunity data for API response.
        
        Ensures all opportunity fields are included in the response with proper formatting.
        
        Args:
            opportunity: Opportunity model instance
            tracked_count: Number of users tracking this opportunity
            participant_count: Number of users participating in this opportunity
            source_registration_count: Number of users registered on the source site
            
        Returns:
            Dictionary containing formatted opportunity data
        """
        if not opportunity:
            return None
        
        # Parse JSON fields if they're strings
        tags = json.loads(opportunity.tags) if isinstance(opportunity.tags, str) else opportunity.tags
        required_skills = json.loads(opportunity.required_skills) if isinstance(opportunity.required_skills, str) else opportunity.required_skills
        timeline = json.loads(opportunity.timeline) if hasattr(opportunity, 'timeline') and isinstance(opportunity.timeline, str) else getattr(opportunity, 'timeline', [])
        prizes = json.loads(opportunity.prizes) if hasattr(opportunity, 'prizes') and isinstance(opportunity.prizes, str) else getattr(opportunity, 'prizes', [])
        
        # Safety fallback for counts if not passed
        final_tracked = tracked_count or getattr(opportunity, 'tracked_count', 0)
        final_participant = participant_count or getattr(opportunity, 'participant_count', 0)
        final_source_reg = source_registration_count or getattr(opportunity, 'source_registration_count', 0)

        return {
            "id": opportunity.id,
            "title": opportunity.title,
            "description": opportunity.description,
            "type": opportunity.type,
            "deadline": opportunity.deadline.isoformat() if hasattr(opportunity.deadline, 'isoformat') else str(opportunity.deadline) if opportunity.deadline else None,
            "application_link": opportunity.application_link,
            "image_url": getattr(opportunity, 'image_url', None),
            "tags": tags if isinstance(tags, list) else [],
            "required_skills": required_skills if isinstance(required_skills, list) else [],
            "timeline": timeline if isinstance(timeline, list) else [],
            "prizes": prizes if isinstance(prizes, list) else [],
            "eligibility": opportunity.eligibility,
            "status": opportunity.status,
            "tracked_count": final_tracked,
            "participant_count": final_participant,
            "source_registration_count": final_source_reg,
            "created_at": opportunity.created_at.isoformat() if hasattr(opportunity.created_at, 'isoformat') else str(opportunity.created_at) if opportunity.created_at else None,
            "updated_at": opportunity.updated_at.isoformat() if hasattr(opportunity.updated_at, 'isoformat') else str(opportunity.updated_at) if opportunity.updated_at else None
        }
    
    @staticmethod
    def format_tracked_opportunities_response(
        tracked_opportunities: List,
        sort_by_deadline: bool = True
    ) -> List[Dict[str, Any]]:
        """Format tracked opportunities list for API response.
        
        Ensures tracked opportunities are properly formatted and sorted by deadline.
        
        Args:
            tracked_opportunities: List of tracked opportunity tuples (TrackedOpportunity, Opportunity)
            sort_by_deadline: Whether to sort by deadline (ascending)
            
        Returns:
            List of formatted tracked opportunity dictionaries
        """
        if not tracked_opportunities:
            return []
        
        formatted_list = []
        
        for tracked, opportunity in tracked_opportunities:
            # Format opportunity data
            opportunity_data = ResponseFormatter.format_opportunity_response(opportunity)
            
            formatted_list.append({
                "user_id": tracked.user_id,
                "opportunity_id": tracked.opportunity_id,
                "saved_at": tracked.saved_at.isoformat() if tracked.saved_at else None,
                "is_expired": tracked.is_expired,
                "opportunity": opportunity_data
            })
        
        # Sort by deadline if requested
        if sort_by_deadline:
            formatted_list.sort(
                key=lambda x: x["opportunity"]["deadline"] if x["opportunity"]["deadline"] else "9999-12-31"
            )
        
        return formatted_list
    
    @staticmethod
    def format_participation_history_response(participation_entry) -> Dict[str, Any]:
        """Format participation history entry for API response.
        
        Ensures all participation history fields are included with proper formatting.
        
        Args:
            participation_entry: ParticipationHistory model instance
            
        Returns:
            Dictionary containing formatted participation history data
        """
        if not participation_entry:
            return None
        
        return {
            "id": participation_entry.id,
            "user_id": participation_entry.user_id,
            "opportunity_id": participation_entry.opportunity_id,
            "status": participation_entry.status,
            "notes": participation_entry.notes,
            "created_at": participation_entry.timestamp.isoformat() if participation_entry.timestamp else None
        }
    
    @staticmethod
    def format_participation_history_list(
        participation_entries: List,
        include_opportunity_details: bool = False
    ) -> List[Dict[str, Any]]:
        """Format participation history list for API response.
        
        Args:
            participation_entries: List of participation history entries
            include_opportunity_details: Whether to include full opportunity details
            
        Returns:
            List of formatted participation history dictionaries
        """
        if not participation_entries:
            return []
        
        formatted_list = []
        
        for entry in participation_entries:
            formatted_entry = ResponseFormatter.format_participation_history_response(entry)
            
            # Optionally include opportunity details
            if include_opportunity_details and hasattr(entry, 'opportunity'):
                formatted_entry["opportunity"] = ResponseFormatter.format_opportunity_response(
                    entry.opportunity
                )
            
            formatted_list.append(formatted_entry)
        
        return formatted_list
    
    @staticmethod
    def format_recommendation_response(
        opportunity,
        relevance_score: float,
        tracked_count: int = 0
    ) -> Dict[str, Any]:
        """Format recommendation with opportunity and score.
        
        Args:
            opportunity: Opportunity model instance
            relevance_score: Calculated relevance score (0-1)
            tracked_count: Number of users tracking this opportunity
            
        Returns:
            Dictionary containing formatted recommendation data
        """
        return {
            "opportunity": ResponseFormatter.format_opportunity_response(opportunity, tracked_count),
            "relevance_score": round(relevance_score, 3)
        }
    
    @staticmethod
    def format_user_export_data(
        user,
        profile,
        tracked_opportunities: List,
        participation_history: List,
        reminders: List
    ) -> Dict[str, Any]:
        """Format complete user data export.
        
        Args:
            user: User model instance
            profile: Profile model instance
            tracked_opportunities: List of tracked opportunities
            participation_history: List of participation history entries
            reminders: List of reminders
            
        Returns:
            Dictionary containing complete user data export
        """
        # Parse JSON fields
        interests = json.loads(profile.interests) if isinstance(profile.interests, str) else profile.interests
        skills = json.loads(profile.skills) if isinstance(profile.skills, str) else profile.skills
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "username": getattr(user, 'username', None),
                "phone": user.phone,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            },
            "profile": {
                "interests": interests if isinstance(interests, list) else [],
                "skills": skills if isinstance(skills, list) else [],
                "education_level": profile.education_level,
                "notification_email": profile.notification_email,
                "notification_sms": profile.notification_sms,
                "low_bandwidth_mode": profile.low_bandwidth_mode,
                "updated_at": profile.updated_at.isoformat() if profile.updated_at else None
            },
            "tracked_opportunities": [
                {
                    "opportunity_id": t.opportunity_id,
                    "saved_at": t.saved_at.isoformat() if t.saved_at else None,
                    "is_expired": t.is_expired
                }
                for t in tracked_opportunities
            ],
            "participation_history": [
                {
                    "id": p.id,
                    "opportunity_id": p.opportunity_id,
                    "status": p.status,
                    "notes": p.notes,
                    "timestamp": p.timestamp.isoformat() if p.timestamp else None
                }
                for p in participation_history
            ],
            "reminders": [
                {
                    "id": r.id,
                    "opportunity_id": r.opportunity_id,
                    "scheduled_time": r.scheduled_time.isoformat() if r.scheduled_time else None,
                    "sent": r.sent
                }
                for r in reminders
            ],
            "export_date": datetime.utcnow().isoformat()
        }
    
    @staticmethod
    def format_error_response(
        error_type: str,
        message: str,
        details: Optional[List[Dict[str, Any]]] = None
    ) -> Dict[str, Any]:
        """Format error response.
        
        Args:
            error_type: Type of error (e.g., "Validation Error", "Not Found")
            message: Human-readable error message
            details: Optional list of detailed error information
            
        Returns:
            Dictionary containing formatted error data
        """
        response = {
            "error": error_type,
            "message": message
        }
        
        if details:
            response["details"] = details
        
        return response
