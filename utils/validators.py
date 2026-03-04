"""Input validation utilities."""
import re
from datetime import datetime
from typing import Optional
from urllib.parse import urlparse


class ValidationError(Exception):
    """Custom validation error."""
    pass


class InputValidator:
    """Utility class for input validation."""
    
    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^\+?1?\d{9,15}$')
    URL_PATTERN = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """
        Validate email format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not email:
            return False
        return bool(InputValidator.EMAIL_PATTERN.match(email))
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """
        Validate phone number format.
        Accepts international format with optional + prefix.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not phone:
            return False
        # Remove spaces and dashes for validation
        cleaned = phone.replace(' ', '').replace('-', '')
        return bool(InputValidator.PHONE_PATTERN.match(cleaned))
    
    @staticmethod
    def validate_url(url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not url:
            return False
        
        try:
            result = urlparse(url)
            return all([result.scheme, result.netloc]) and result.scheme in ['http', 'https']
        except Exception:
            return False
    
    @staticmethod
    def validate_date(date_str: str, format: str = "%Y-%m-%d") -> Optional[datetime]:
        """
        Validate and parse date string.
        
        Args:
            date_str: Date string to validate
            format: Expected date format (default: YYYY-MM-DD)
            
        Returns:
            Parsed datetime object if valid, None otherwise
        """
        if not date_str:
            return None
        
        try:
            return datetime.strptime(date_str, format)
        except ValueError:
            return None
    
    @staticmethod
    def validate_deadline(deadline: datetime) -> bool:
        """
        Validate that deadline is in the future.
        
        Args:
            deadline: Deadline datetime to validate
            
        Returns:
            True if deadline is in the future, False otherwise
        """
        if not deadline:
            return False
        return deadline > datetime.utcnow()
    
    @staticmethod
    def sanitize_search_query(query: str) -> str:
        """
        Sanitize search query to prevent injection attacks.
        
        Args:
            query: Search query to sanitize
            
        Returns:
            Sanitized query string
        """
        if not query:
            return ""
        
        # Remove potentially dangerous characters
        # Allow alphanumeric, spaces, and common punctuation
        sanitized = re.sub(r'[^\w\s\-.,!?@#]', '', query)
        
        # Limit length
        return sanitized[:500]
    
    @staticmethod
    def validate_education_level(level: str) -> bool:
        """
        Validate education level.
        
        Args:
            level: Education level to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_levels = [
            "high_school",
            "associate",
            "bachelor",
            "master",
            "doctorate",
            "other"
        ]
        return level.lower() in valid_levels
    
    @staticmethod
    def validate_opportunity_type(opp_type: str) -> bool:
        """
        Validate opportunity type.
        
        Args:
            opp_type: Opportunity type to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_types = [
            "hackathon",
            "scholarship",
            "internship",
            "fellowship",
            "grant",
            "competition",
            "workshop",
            "conference",
            "other"
        ]
        return opp_type.lower() in valid_types
    
    @staticmethod
    def validate_participation_status(status: str) -> bool:
        """
        Validate participation status.
        
        Args:
            status: Status to validate
            
        Returns:
            True if valid, False otherwise
        """
        valid_statuses = [
            "interested",
            "applied",
            "accepted",
            "rejected",
            "completed",
            "withdrawn"
        ]
        return status.lower() in valid_statuses
    
    @staticmethod
    def validate_required_fields(data: dict, required_fields: list) -> tuple[bool, Optional[str]]:
        """
        Validate that all required fields are present and non-empty.
        
        Args:
            data: Dictionary of data to validate
            required_fields: List of required field names
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        for field in required_fields:
            if field not in data or data[field] is None or data[field] == "":
                return False, f"Required field '{field}' is missing or empty"
        return True, None
    
    @staticmethod
    def validate_string_length(value: str, min_length: int = 0, max_length: int = None) -> bool:
        """
        Validate string length.
        
        Args:
            value: String to validate
            min_length: Minimum length (default: 0)
            max_length: Maximum length (default: None)
            
        Returns:
            True if valid, False otherwise
        """
        if not value:
            return min_length == 0
        
        length = len(value)
        if length < min_length:
            return False
        if max_length is not None and length > max_length:
            return False
        return True
