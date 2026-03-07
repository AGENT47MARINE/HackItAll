"""Profile service for user profile management."""
import json
import bcrypt
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from email_validator import validate_email, EmailNotValidError

from models.user import User, Profile
from utils.formatters import ResponseFormatter
from services.nlp.resume_parser_service import ResumeParserService


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


class ProfileService:
    """Service for managing user profiles with CRUD operations."""
    
    def __init__(self, db_session: Session):
        """Initialize the profile service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def _validate_profile_data(self, education_level: Optional[str] = None, 
                              email: Optional[str] = None,
                              interests: Optional[List[str]] = None,
                              skills: Optional[List[str]] = None) -> None:
        """Validate profile data.
        
        Args:
            education_level: Education level (required field)
            email: Email address
            interests: List of interests
            skills: List of skills
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate required field: education_level
        if education_level is not None and not education_level.strip():
            raise ValidationError("education_level is required and cannot be empty")
        
        # Validate email format using email-validator
        if email is not None:
            try:
                # We don't need to check deliverability for basic validation
                validate_email(email, check_deliverability=False)
            except EmailNotValidError as e:
                raise ValidationError(f"Invalid email format: {str(e)}")
        
        # Validate interests and skills are lists if provided
        if interests is not None and not isinstance(interests, list):
            raise ValidationError("interests must be a list")
        
        if skills is not None and not isinstance(skills, list):
            raise ValidationError("skills must be a list")
    
    def create_profile(self, user_id: str, email: str, education_level: str,
                      username: str,
                      interests: Optional[List[str]] = None,
                      skills: Optional[List[str]] = None,
                      phone: Optional[str] = None,
                      notification_email: bool = True,
                      notification_sms: bool = False,
                      low_bandwidth_mode: bool = False) -> Dict[str, Any]:
        """Create a new user profile (Synced from Clerk).
        
        Args:
            user_id: The explicit ID provided by Clerk Webhooks
            email: User email address
            education_level: User's education level (required)
            interests: List of user interests (default: empty list)
            skills: List of user skills (default: empty list)
            phone: Phone number (optional)
            notification_email: Enable email notifications (default: True)
            notification_sms: Enable SMS notifications (default: False)
            low_bandwidth_mode: Enable low bandwidth mode (default: False)
            
        Returns:
            Dictionary containing user and profile data
            
        Raises:
            ValidationError: If validation fails
            IntegrityError: If email already exists
        """
        # Set defaults
        if interests is None:
            interests = []
        if skills is None:
            skills = []
        
        # Validate data
        self._validate_profile_data(
            education_level=education_level,
            email=email,
            interests=interests,
            skills=skills
        )
        
        # Create user linked to Clerk ID
        user = User(
            id=user_id,
            username=username,
            email=email,
            phone=phone
        )
        
        try:
            self.db.add(user)
            self.db.flush()  # Get user ID constraints registered
            
            # Create profile
            profile = Profile(
                user_id=user.id,
                interests=json.dumps(interests),
                skills=json.dumps(skills),
                education_level=education_level,
                notification_email=notification_email,
                notification_sms=notification_sms,
                low_bandwidth_mode=low_bandwidth_mode
            )
            
            self.db.add(profile)
            self.db.commit()
            
            return self._format_profile_response(user, profile)
            
        except (IntegrityError, ValidationError, Exception):
            self.db.rollback()
            raise
    
    def get_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get a user profile by user ID.
        
        Args:
            user_id: User ID
            
        Returns:
            Dictionary containing user and profile data, or None if not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.profile:
            return None
        
        return self._format_profile_response(user, user.profile)
    
    def update_profile(self, user_id: str, 
                      interests: Optional[List[str]] = None,
                      skills: Optional[List[str]] = None,
                      education_level: Optional[str] = None,
                      phone: Optional[str] = None,
                      notification_email: Optional[bool] = None,
                      notification_sms: Optional[bool] = None,
                      low_bandwidth_mode: Optional[bool] = None) -> Optional[Dict[str, Any]]:
        """Update a user profile.
        
        Args:
            user_id: User ID
            interests: Updated list of interests (optional)
            skills: Updated list of skills (optional)
            education_level: Updated education level (optional)
            phone: Updated phone number (optional)
            notification_email: Updated email notification preference (optional)
            notification_sms: Updated SMS notification preference (optional)
            low_bandwidth_mode: Updated low bandwidth mode preference (optional)
            
        Returns:
            Dictionary containing updated user and profile data, or None if not found
            
        Raises:
            ValidationError: If validation fails
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user or not user.profile:
            return None
        
        # Validate updates
        if education_level is not None or interests is not None or skills is not None:
            self._validate_profile_data(
                education_level=education_level,
                interests=interests,
                skills=skills
            )
        
        # Update user fields
        if phone is not None:
            user.phone = phone
        
        # Update profile fields
        profile = user.profile
        
        if interests is not None:
            profile.interests = json.dumps(interests)
        
        if skills is not None:
            profile.skills = json.dumps(skills)
        
        if education_level is not None:
            profile.education_level = education_level
        
        if notification_email is not None:
            profile.notification_email = notification_email
        
        if notification_sms is not None:
            profile.notification_sms = notification_sms
        
        if low_bandwidth_mode is not None:
            profile.low_bandwidth_mode = low_bandwidth_mode
        
        self.db.commit()
        
        return self._format_profile_response(user, profile)
    
    def delete_profile(self, user_id: str) -> bool:
        """Delete a user profile.
        
        Args:
            user_id: User ID
            
        Returns:
            True if deleted successfully, False if not found
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        self.db.delete(user)
        self.db.commit()
        
        return True

    def export_user_data(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Export all user data in a readable format (GDPR compliance).

        This method collects all data associated with a user including:
        - Profile information (email, interests, skills, preferences)
        - Tracked opportunities
        - Participation history
        - Account metadata

        Args:
            user_id: User ID

        Returns:
            Dictionary containing all user data in readable format, or None if user not found
        """
        from models.tracking import TrackedOpportunity, ParticipationHistory
        from models.opportunity import Opportunity
        from datetime import datetime

        # Get user and profile
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return None

        profile = self.db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return None

        # Get tracked opportunities
        tracked = self.db.query(TrackedOpportunity, Opportunity).join(
            Opportunity,
            TrackedOpportunity.opportunity_id == Opportunity.id
        ).filter(
            TrackedOpportunity.user_id == user_id
        ).all()

        tracked_opportunities = []
        for tracked_opp, opportunity in tracked:
            tracked_opportunities.append({
                "opportunity_id": opportunity.id,
                "opportunity_title": opportunity.title,
                "opportunity_type": opportunity.type,
                "opportunity_deadline": opportunity.deadline.isoformat(),
                "saved_at": tracked_opp.saved_at.isoformat(),
                "is_expired": tracked_opp.is_expired
            })

        # Get participation history
        history = self.db.query(ParticipationHistory, Opportunity).join(
            Opportunity,
            ParticipationHistory.opportunity_id == Opportunity.id
        ).filter(
            ParticipationHistory.user_id == user_id
        ).all()

        participation_history = []
        for participation, opportunity in history:
            participation_history.append({
                "participation_id": participation.id,
                "opportunity_id": opportunity.id,
                "opportunity_title": opportunity.title,
                "opportunity_type": opportunity.type,
                "status": participation.status,
                "notes": participation.notes,
                "created_at": participation.created_at.isoformat()
            })

        # Compile complete data export
        export_data = {
            "export_metadata": {
                "export_date": datetime.utcnow().isoformat(),
                "user_id": user_id,
                "data_format_version": "1.0"
            },
            "account_information": {
                "email": user.email,
                "phone": user.phone,
                "account_created": user.created_at.isoformat(),
                "last_updated": user.updated_at.isoformat()
            },
            "profile": {
                "interests": json.loads(profile.interests) if profile.interests else [],
                "skills": json.loads(profile.skills) if profile.skills else [],
                "education_level": profile.education_level,
                "notification_preferences": {
                    "email": profile.notification_email,
                    "sms": profile.notification_sms
                },
                "low_bandwidth_mode": profile.low_bandwidth_mode,
                "profile_updated": profile.updated_at.isoformat()
            },
            "tracked_opportunities": {
                "count": len(tracked_opportunities),
                "opportunities": tracked_opportunities
            },
            "participation_history": {
                "count": len(participation_history),
                "entries": participation_history
            }
        }

        return export_data

    
    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify a user's password (DEPRECATED - Clerk handles auth).
        
        Args:
            user_id: User ID
            password: Plain text password to verify
            
        Returns:
            Always returns True as Clerk handles auth.
        """
        # Clerk handles auth session, this is a placeholder for legacy test compatibility
        return True
    
    def _format_profile_response(self, user: User, profile: Profile) -> Dict[str, Any]:
        """Format user and profile data for response.
        
        Args:
            user: User model instance
            profile: Profile model instance
            
        Returns:
            Dictionary containing formatted user and profile data
        """
        # Get participation history for activity streak calculation
        from models.tracking import ParticipationHistory
        participation_entries = self.db.query(ParticipationHistory).filter(
            ParticipationHistory.user_id == user.id
        ).all()
        
        participation_history = [
            {
                "id": p.id,
                "opportunity_id": p.opportunity_id,
                "status": p.status,
                "notes": p.notes,
                "created_at": p.created_at.isoformat() if p.created_at else None
            }
            for p in participation_entries
        ]
        
        # Use centralized formatter
        return ResponseFormatter.format_profile_response(user, profile, participation_history)
        
    def _calculate_activity_streak(self, user_id: str) -> int:
        """Calculate the consecutive weeks of activity for a user.
        
        Args:
            user_id: User ID
            
        Returns:
            Number of consecutive active weeks
        """
        from models.tracking import TrackedOpportunity, ParticipationHistory
        from datetime import datetime
        
        # Get all activity dates
        tracked_dates = self.db.query(TrackedOpportunity.saved_at).filter(TrackedOpportunity.user_id == user_id).all()
        participation_dates = self.db.query(ParticipationHistory.created_at).filter(ParticipationHistory.user_id == user_id).all()
        
        # Extract datetime objects from tuples
        all_dates = [d[0] for d in tracked_dates if d[0]] + [d[0] for d in participation_dates if d[0]]
        
        if not all_dates:
            return 0
            
        # Convert dates to ISO year and week strings, e.g., "2024-W15"
        active_weeks = set()
        for d in all_dates:
            year, week, _ = d.isocalendar()
            active_weeks.add(f"{year}-W{week:02d}")
            
        # Get current week and check consecutively backwards
        current_date = datetime.utcnow()
        curr_year, curr_week, _ = current_date.isocalendar()
        
        streak = 0
        
        # The streak can start either this week or the previous week (if they haven't been active *yet* this week)
        check_year, check_week = curr_year, curr_week
        
        # Check this week
        if f"{curr_year}-W{curr_week:02d}" in active_weeks:
            streak += 1
            check_week -= 1
        elif curr_week == 1:
            from datetime import date
            check_year_last = curr_year - 1
            check_week_last = date(check_year_last, 12, 28).isocalendar()[1]
            if f"{check_year_last}-W{check_week_last:02d}" in active_weeks:
                # Active last week of previous year
                streak += 1
                check_year = check_year_last
                check_week = check_week_last - 1
            else:
                return 0
        elif f"{curr_year}-W{curr_week - 1:02d}" in active_weeks:
            # They were active last week but not this week, so streak is still alive
            streak += 1
            check_week -= 2
        else:
            return 0
            
        # Continue counting backwards
        while True:
            # Handle year wrap around logically
            if check_week <= 0:
                check_year -= 1
                from datetime import date
                check_week = date(check_year, 12, 28).isocalendar()[1]
                
            week_str = f"{check_year}-W{check_week:02d}"
            
            if week_str in active_weeks:
                streak += 1
                check_week -= 1
            else:
                break
                
        return streak

    def update_profile_from_resume(self, user_id: str, resume_content: bytes) -> Optional[Dict[str, Any]]:
        """Parse a resume and update the user's profile automatically.
        
        Args:
            user_id: User ID
            resume_content: Binary content of the PDF resume
            
        Returns:
            Dictionary containing updated profile data
        """
        parser = ResumeParserService()
        structured_data = parser.get_structured_profile(resume_content)
        
        # Overlay the extracted data onto the existing profile
        return self.update_profile(
            user_id=user_id,
            interests=structured_data.get("interests"),
            skills=structured_data.get("skills"),
            education_level=structured_data.get("education_level")
        )
