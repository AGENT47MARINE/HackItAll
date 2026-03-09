"""Authentication API endpoints and middleware."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db
class AuthenticationError(Exception):
    """Exception raised for authentication errors."""
    pass
from services.profile_service import ProfileService


# Security scheme
security = HTTPBearer(auto_error=False)

# Router
router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models
class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters")
    education_level: str = Field(..., min_length=1, description="Education level is required")
    interests: list[str] = Field(default_factory=list)
    skills: list[str] = Field(default_factory=list)
    phone: Optional[str] = None
    notification_email: bool = True
    notification_sms: bool = False
    low_bandwidth_mode: bool = False


class LoginRequest(BaseModel):
    """Request model for user login."""
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    """Request model for Google OAuth authentication."""
    token: str
    education_level: Optional[str] = None
    interests: Optional[list[str]] = None
    skills: Optional[list[str]] = None


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str


class UserResponse(BaseModel):
    """Response model for user data."""
    id: str
    email: EmailStr
    username: str
    phone: Optional[str]
    interests: list[str]
    skills: list[str]
    education_level: str
    notification_email: bool
    notification_sms: bool
    low_bandwidth_mode: bool
    updated_at: str


import os
from clerk_backend_api import Clerk
import jwt
from jwt import PyJWKClient

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Validate Clerk JWT token and return user ID.
    
    Args:
        credentials: Bearer token from authorization header
        
    Returns:
        String UUID/Subject of the authenticated Clerk user
        
    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    token = credentials.credentials
    
    clerk_secret = os.getenv("CLERK_SECRET_KEY")
    if not clerk_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CLERK_SECRET_KEY not configured on server"
        )
        
    try:
        # Decode the JWT token without verification first to get the issuer
        unverified_payload = jwt.decode(token, options={"verify_signature": False})
        
        # Get the issuer (Clerk domain)
        issuer = unverified_payload.get("iss")
        if not issuer:
            raise AuthenticationError("Token missing issuer")
        
        # Construct JWKS URL from issuer
        jwks_url = f"{issuer}/.well-known/jwks.json"
        
        # Get the signing key from Clerk's JWKS endpoint
        jwks_client = PyJWKClient(jwks_url)
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        
        # Verify and decode the token
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=["RS256"],
            options={"verify_signature": True, "verify_exp": True}
        )
        
        # Extract the user ID from the verified token
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id:
            raise AuthenticationError("Token payload missing user identifier")

        # Lazy init: Ensure user exists in our local DB
        from models.user import User, Profile
        from services.profile_service import ProfileService
        
        db = next(get_db())
        try:
            existing_user = db.query(User).filter(User.id == user_id).first()
            if not existing_user:
                # If we don't have the email from the token, fetch from Clerk API
                if not email:
                    try:
                        clerk = Clerk(bearer_auth=clerk_secret)
                        user_obj = clerk.users.get(user_id=user_id)
                        email = user_obj.email_addresses[0].email_address if user_obj.email_addresses else None
                    except:
                        email = f"user_{user_id[:8]}@temporary.com"
                
                # Extract username from token or email
                clerk_username = payload.get("username") or payload.get("name")
                if not clerk_username:
                    clerk_username = email.split('@')[0] if email else f"user_{user_id[:8]}"
                
                profile_service = ProfileService(db)
                profile_service.create_profile(
                    user_id=user_id,
                    email=email or f"user_{user_id[:8]}@temporary.com",
                    username=clerk_username,
                    education_level="Not Specified",
                    interests=[],
                    skills=[]
                )
            
            # AWARD XP: 10 XP for daily login (once per day)
            from services.gamification_service import GamificationService
            from datetime import datetime
            gamification = GamificationService(db)
            today_str = datetime.utcnow().strftime("%Y-%m-%d")
            gamification.award_xp(user_id, "daily_login", reference_id=f"login_{today_str}")
                
        finally:
            db.close()
             
        return user_id
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_active_user(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> str:
    """Get current active user (used as a dependency).
    
    Since Clerk handles email verification / banned status externally, 
    we just pass through the user ID for our internal DB queries.
    """
    return current_user_id


def get_current_admin_user(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> str:
    """Get current admin user (used as a dependency for admin-only endpoints).
    
    Checks if the current user has admin privileges. Admin status can be determined by:
    1. Checking Clerk metadata for admin role
    2. Checking a whitelist of admin user IDs
    3. Checking a database admin flag
    
    For now, we'll use an environment variable whitelist approach.
    
    Args:
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        User ID if user is admin
        
    Raises:
        HTTPException: If user is not an admin
    """
    import os
    
    # Get admin user IDs from environment variable (comma-separated)
    admin_ids = os.getenv("ADMIN_USER_IDS", "").split(",")
    admin_ids = [id.strip() for id in admin_ids if id.strip()]
    
    if current_user_id not in admin_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required for this operation"
        )
    
    return current_user_id


# User identity and standard login endpoints are fully managed by Clerk externally.
# Only the profile retrieval relies on the internal API relying on `get_current_user`.


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current authenticated user's profile information.
    
    Args:
        current_user_id: Current user ID from token
        db: Database session
        
    Returns:
        User profile information
        
    Raises:
        HTTPException: If user not found
    """
    profile_service = ProfileService(db)
    
    profile_data = profile_service.get_profile(current_user_id)
    
    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User profile not found"
        )
    
    return UserResponse(**profile_data)
