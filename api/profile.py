from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from pydantic import BaseModel
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
    username: Optional[str] = None
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
    activity_streak: int = 0
    
class ResumeSyncResponse(ProfileResponse):
    """Response model for resume synchronization."""
    extracted_skills: list[str] = []
    extracted_interests: list[str] = []
    raw_text: str = ""
    new_skills_count: int = 0
    new_interests_count: int = 0


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



@router.get("/export")
async def export_user_data(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data (GDPR compliance).
    
    This endpoint allows users to download a complete copy of all their data
    stored in the platform. This includes:
    - Account information (email, phone, creation date)
    - Profile data (interests, skills, education level, preferences)
    - Tracked opportunities
    - Participation history with notes
    
    The data is returned in JSON format for easy readability and portability.
    
    This endpoint fulfills GDPR Article 20 (Right to data portability) and
    CCPA requirements for data access.
    
    Args:
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        Complete user data export in JSON format
        
    Raises:
        HTTPException: If user not found (404)
    """
    profile_service = ProfileService(db)
    
    export_data = profile_service.export_user_data(current_user_id)
    
    if not export_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User data not found"
        )
    
    return export_data


@router.post("/profile/resume", response_model=ResumeSyncResponse)
async def upload_resume(
    file: UploadFile = File(...),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload and parse a resume to update the user's profile.
    
    Args:
        file: The PDF resume file
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        Updated profile information based on resume parsing
        
    Raises:
        HTTPException: If file is not a PDF or parsing fails
    """
    if not file.filename.endswith(".pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are supported for resume parsing."
        )
    
    profile_service = ProfileService(db)
    
    try:
        content = await file.read()
        profile_data = profile_service.update_profile_from_resume(current_user_id, content)
        
        if not profile_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile could not be updated from resume."
            )
        
        # The service returns a dict with combined profile and metadata
        # Create response model while ensuring no duplicate keys if merged in service
        return ResumeSyncResponse(
            **profile_data,
            # These are already in profile_data if updated by service, 
            # but explicit override for clarity is only safe if not in profile_data
            # or if profile_data is filtered.
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse resume: {str(e)}"
        )
