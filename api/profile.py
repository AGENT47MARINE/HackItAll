"""Profile management API endpoints."""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from services.profile_service import ProfileService, ValidationError
from api.auth import get_current_user


# Router
router = APIRouter(prefix="/api", tags=["profile"])


# Request/Response Models
class ProfileResponse(BaseModel):
    """Response model for profile data."""
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
    participation_history: list


class UpdateProfileRequest(BaseModel):
    """Request model for profile updates."""
    interests: Optional[list[str]] = None
    skills: Optional[list[str]] = None
    education_level: Optional[str] = None
    phone: Optional[str] = None
    notification_email: Optional[bool] = None
    notification_sms: Optional[bool] = None
    low_bandwidth_mode: Optional[bool] = None


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user's profile.
    
    Args:
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        User profile information
        
    Raises:
        HTTPException: If profile not found
    """
    profile_service = ProfileService(db)
    
    profile_data = profile_service.get_profile(current_user_id)
    
    if not profile_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return ProfileResponse(**profile_data)


@router.put("/profile", response_model=ProfileResponse)
async def update_profile(
    request: UpdateProfileRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user's profile.
    
    Args:
        request: Profile update data
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        Updated profile information
        
    Raises:
        HTTPException: If update fails or profile not found
    """
    profile_service = ProfileService(db)
    
    try:
        profile_data = profile_service.update_profile(
            user_id=current_user_id,
            interests=request.interests,
            skills=request.skills,
            education_level=request.education_level,
            phone=request.phone,
            notification_email=request.notification_email,
            notification_sms=request.notification_sms,
            low_bandwidth_mode=request.low_bandwidth_mode
        )
        
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return ProfileResponse(**profile_data)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/profile", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete current user's account and profile.
    
    Args:
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        No content on successful deletion
        
    Raises:
        HTTPException: If deletion fails or profile not found
    """
    profile_service = ProfileService(db)
    
    success = profile_service.delete_profile(current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found"
        )
    
    return None
