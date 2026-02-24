"""Authentication service for JWT-based authentication."""
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from sqlalchemy.orm import Session
import bcrypt

from models.user import User
from config import config


class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    pass


class AuthService:
    """Service for handling authentication operations."""
    
    def __init__(self, db_session: Session):
        """Initialize the auth service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def create_access_token(self, user_id: str, email: str, extra_claims: Optional[Dict[str, Any]] = None) -> str:
        """Create a JWT access token.
        
        Args:
            user_id: User ID
            email: User email
            extra_claims: Optional dictionary of additional claims to include in the token
            
        Returns:
            JWT token string
        """
        expire = datetime.utcnow() + timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode = {
            "sub": user_id,
            "email": email,
            "exp": expire
        }
        
        # Add extra claims if provided
        if extra_claims:
            to_encode.update(extra_claims)
        
        encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify a JWT token and extract payload.
        
        Args:
            token: JWT token string
            
        Returns:
            Dictionary containing token payload with all claims
            
        Raises:
            AuthenticationError: If token is invalid or expired
        """
        try:
            payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
            user_id: str = payload.get("sub")
            email: str = payload.get("email")
            
            if user_id is None or email is None:
                raise AuthenticationError("Invalid token payload")
            
            # Return full payload including extra claims
            return {
                "user_id": user_id,
                "email": email,
                **{k: v for k, v in payload.items() if k not in ["sub", "email", "exp"]}
            }
            
        except JWTError as e:
            raise AuthenticationError(f"Invalid token: {str(e)}")
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate a user with email and password.
        
        Args:
            email: User email
            password: Plain text password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        user = self.db.query(User).filter(User.email == email).first()
        
        if not user:
            return None
        
        # Verify password
        if not bcrypt.checkpw(password.encode('utf-8'), user.password_hash.encode('utf-8')):
            return None
        
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID.
        
        Args:
            user_id: User ID
            
        Returns:
            User object if found, None otherwise
        """
        return self.db.query(User).filter(User.id == user_id).first()
