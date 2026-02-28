"""Authentication API endpoints and middleware."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy.orm import Session

from database import get_db
from services.auth_service import AuthService, AuthenticationError
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


# Dependency to get current user from token
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency to extract and verify current user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User ID from token
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        user_id = payload["user_id"]
        
        # Verify user exists
        user = auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user_id
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


async def require_admin(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """Dependency to verify current user has admin privileges.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        User ID from token
        
    Raises:
        HTTPException: If authentication fails or user is not admin
    """
    auth_service = AuthService(db)
    
    try:
        token = credentials.credentials
        payload = auth_service.verify_token(token)
        user_id = payload["user_id"]
        
        # Verify user exists
        user = auth_service.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check for admin role in token payload
        # For now, we'll check if the payload has an 'is_admin' field
        # In a production system, this would be stored in the database
        is_admin = payload.get("is_admin", False)
        
        if not is_admin:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin privileges required"
            )
        
        return user_id
        
    except AuthenticationError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """Register a new user and return access token.
    
    Args:
        request: Registration request data
        db: Database session
        
    Returns:
        Access token and user information
        
    Raises:
        HTTPException: If registration fails
    """
    profile_service = ProfileService(db)
    auth_service = AuthService(db)
    
    try:
        # Create profile (includes user creation)
        profile_data = profile_service.create_profile(
            email=request.email,
            password=request.password,
            education_level=request.education_level,
            interests=request.interests,
            skills=request.skills,
            phone=request.phone,
            notification_email=request.notification_email,
            notification_sms=request.notification_sms,
            low_bandwidth_mode=request.low_bandwidth_mode
        )
        
        # Create access token
        access_token = auth_service.create_access_token(
            user_id=profile_data["id"],
            email=profile_data["email"]
        )
        
        return TokenResponse(
            access_token=access_token,
            user_id=profile_data["id"],
            email=profile_data["email"]
        )
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        # Handle duplicate email
        if "already exists" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered"
            )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Registration failed"
        )


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access token.
    
    Args:
        request: Login request data
        db: Database session
        
    Returns:
        Access token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    auth_service = AuthService(db)
    
    # Authenticate user
    user = auth_service.authenticate_user(request.email, request.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        user_id=user.id,
        email=user.email
    )
    
    return TokenResponse(
        access_token=access_token,
        user_id=user.id,
        email=user.email
    )


@router.post("/google", response_model=TokenResponse)
async def google_auth(request: GoogleAuthRequest, db: Session = Depends(get_db)):
    """Authenticate user with Google OAuth token.
    
    Args:
        request: Google auth request with token
        db: Database session
        
    Returns:
        Access token and user information
        
    Raises:
        HTTPException: If authentication fails
    """
    from google.oauth2 import id_token
    from google.auth.transport import requests
    import os
    
    auth_service = AuthService(db)
    profile_service = ProfileService(db)
    
    try:
        # Verify Google token
        google_client_id = os.getenv('GOOGLE_CLIENT_ID')
        if not google_client_id:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Google OAuth not configured"
            )
        
        idinfo = id_token.verify_oauth2_token(
            request.token, 
            requests.Request(), 
            google_client_id
        )
        
        # Extract user info from Google token
        email = idinfo.get('email')
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not provided by Google"
            )
        
        # Check if user exists
        user = auth_service.get_user_by_email(email)
        
        if user:
            # User exists, log them in
            access_token = auth_service.create_access_token(
                user_id=user.id,
                email=user.email
            )
            
            return TokenResponse(
                access_token=access_token,
                user_id=user.id,
                email=user.email
            )
        else:
            # New user, create account
            # For Google OAuth, we'll use a random password since they won't use it
            import secrets
            random_password = secrets.token_urlsafe(32)
            
            profile_data = profile_service.create_profile(
                email=email,
                password=random_password,
                education_level=request.education_level or "Not specified",
                interests=request.interests or [],
                skills=request.skills or [],
                notification_email=True,
                notification_sms=False,
                low_bandwidth_mode=False
            )
            
            # Create access token
            access_token = auth_service.create_access_token(
                user_id=profile_data["id"],
                email=profile_data["email"]
            )
            
            return TokenResponse(
                access_token=access_token,
                user_id=profile_data["id"],
                email=profile_data["email"]
            )
            
    except ValueError as e:
        # Invalid token
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid Google token: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Google authentication failed: {str(e)}"
        )


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
