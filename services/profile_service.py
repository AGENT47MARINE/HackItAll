"""Profile service for user profile management."""
import json
import bcrypt
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from models.user import User, Profile


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
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using bcrypt.
        
        Args:
            password: Plain text password
            
        Returns:
            Hashed password string
        """
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
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
        
        # Validate email format if provided
        if email is not None:
            if not email or '@' not in email or '.' not in email.split('@')[-1]:
                raise ValidationError("Invalid email format")
        
        # Validate interests and skills are lists if provided
        if interests is not None and not isinstance(interests, list):
            raise ValidationError("interests must be a list")
        
        if skills is not None and not isinstance(skills, list):
            raise ValidationError("skills must be a list")
    
    def create_profile(self, email: str, password: str, education_level: str,
                      interests: Optional[List[str]] = None,
                      skills: Optional[List[str]] = None,
                      phone: Optional[str] = None,
                      notification_email: bool = True,
                      notification_sms: bool = False,
                      low_bandwidth_mode: bool = False) -> Dict[str, Any]:
        """Create a new user profile.
        
        Args:
            email: User email address
            password: Plain text password (will be hashed)
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
        
        # Hash password
        password_hash = self._hash_password(password)
        
        # Create user
        user = User(
            email=email,
            password_hash=password_hash,
            phone=phone
        )
        
        try:
            self.db.add(user)
            self.db.flush()  # Get user ID
            
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
            
        except IntegrityError as e:
            self.db.rollback()
            raise IntegrityError("Email already exists", params=None, orig=e.orig)
    
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
    
    def verify_password(self, user_id: str, password: str) -> bool:
        """Verify a user's password.
        
        Args:
            user_id: User ID
            password: Plain text password to verify
            
        Returns:
            True if password matches, False otherwise
        """
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            return False
        
        return bcrypt.checkpw(
            password.encode('utf-8'),
            user.password_hash.encode('utf-8')
        )
    
    def _format_profile_response(self, user: User, profile: Profile) -> Dict[str, Any]:
        """Format user and profile data for response.
        
        Args:
            user: User model instance
            profile: Profile model instance
            
        Returns:
            Dictionary containing formatted user and profile data
        """
        return {
            "id": user.id,
            "email": user.email,
            "phone": user.phone,
            "interests": json.loads(profile.interests),
            "skills": json.loads(profile.skills),
            "education_level": profile.education_level,
            "notification_email": profile.notification_email,
            "notification_sms": profile.notification_sms,
            "low_bandwidth_mode": profile.low_bandwidth_mode,
            "created_at": user.created_at.isoformat(),
            "updated_at": profile.updated_at.isoformat(),
            "participation_history": []  # Empty for now, will be populated later
        }
