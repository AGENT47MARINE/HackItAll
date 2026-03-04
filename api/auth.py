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
from services.profile_service import ProfileService, ValidationError


# Security scheme
security = HTTPBearer()

# Router
router = APIRouter(prefix="/api/auth", tags=["authentication"])


# Request/Response Models
class RegisterRequest(BaseModel):
    """Request model for user registration."""
    email: EmailStr
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
    email: str
    phone: Optional[str]
    interests: list[str]
    skills: list[str]
    education_level: str
    notification_email: bool
    notification_sms: bool
    low_bandwidth_mode: bool
    created_at: str
    updated_at: str


import os
from clerk_backend_api import Clerk

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Validate Clerk JWT token and return user ID.
    
    Args:
        credentials: Bearer token from authorization header
        
    Returns:
        String UUID/Subject of the authenticated Clerk user
        
    Raises:
        HTTPException: If token is missing, invalid, or expired
    """
    token = credentials.credentials
    
    clerk_secret = os.getenv("CLERK_SECRET_KEY")
    if not clerk_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="CLERK_SECRET_KEY not configured on server"
        )
        
    try:
        clerk = Clerk(bearer_auth=clerk_secret)
        # Verify the token natively using Clerk's SDK
        # This checks the signature, expiration, and issuer automatically
        token_payload = clerk.authenticate_request(
            request=None, # SDK supports passing raw request, but we have the raw JWT string
            header_token=token
        )
        
        if not token_payload.is_signed_in or not token_payload.payload:
             raise AuthenticationError("Invalid or expired session")
             
        # Extract the user ID from the verified token
        # In Clerk, 'sub' is the unique user ID string
        user_id = token_payload.payload.get("sub")
        email = token_payload.payload.get("email") # Check if email is in payload
        
        if not user_id:
             raise AuthenticationError("Token payload missing user identifier")

        # Lazy init: Ensure user exists in our local DB
        # This solves the issue of webhooks not being reachable on localhost
        from models.user import User, Profile
        from services.profile_service import ProfileService
        
        db = next(get_db())
        try:
            existing_user = db.query(User).filter(User.id == user_id).first()
            if not existing_user:
                # If we don't have the email from the token, we can try to get it from Clerk API
                if not email:
                    try:
                        user_obj = clerk.users.get(user_id=user_id)
                        email = user_obj.email_addresses[0].email_address if user_obj.email_addresses else None
                    except:
                        email = f"user_{user_id[:8]}@temporary.com"
                
                profile_service = ProfileService(db)
                profile_service.create_profile(
                    user_id=user_id,
                    email=email or f"user_{user_id[:8]}@temporary.com",
                    education_level="Not Specified",
                    interests=[],
                    skills=[]
                )
        finally:
            db.close()
             
        return user_id
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
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
