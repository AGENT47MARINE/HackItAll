"""Utility API endpoints for preferences and data export."""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from database import get_db
from services.profile_service import ProfileService
from api.auth import get_current_user
from models.user import User, Profile
from models.tracking import TrackedOpportunity, ParticipationHistory
from models.reminder import Reminder
import json


router = APIRouter(prefix="/api", tags=["utility"])


class PreferencesUpdate(BaseModel):
    """Model for updating user preferences."""
    notification_email: Optional[bool] = None
    notification_sms: Optional[bool] = None
    low_bandwidth_mode: Optional[bool] = None


@router.put("/preferences")
async def update_preferences(
    preferences: PreferencesUpdate,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user notification and display preferences."""
    profile_service = ProfileService(db)
    
    try:
        # Get current profile
        profile = profile_service.get_profile(current_user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        # Update preferences
        update_data = {}
        if preferences.notification_email is not None:
            update_data["notification_email"] = preferences.notification_email
        if preferences.notification_sms is not None:
            update_data["notification_sms"] = preferences.notification_sms
        if preferences.low_bandwidth_mode is not None:
            update_data["low_bandwidth_mode"] = preferences.low_bandwidth_mode
        
        if update_data:
            updated_profile = profile_service.update_profile(
                current_user_id,
                update_data
            )
            
            return {
                "message": "Preferences updated successfully",
                "preferences": {
                    "notification_email": updated_profile.notification_email,
                    "notification_sms": updated_profile.notification_sms,
                    "low_bandwidth_mode": updated_profile.low_bandwidth_mode
                }
            }
        else:
            return {
                "message": "No preferences to update",
                "preferences": {
                    "notification_email": profile.notification_email,
                    "notification_sms": profile.notification_sms,
                    "low_bandwidth_mode": profile.low_bandwidth_mode
                }
            }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update preferences: {str(e)}"
        )


@router.get("/preferences")
async def get_preferences(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user preferences."""
    profile_service = ProfileService(db)
    
    try:
        profile = profile_service.get_profile(current_user_id)
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Profile not found"
            )
        
        return {
            "notification_email": profile.notification_email,
            "notification_sms": profile.notification_sms,
            "low_bandwidth_mode": profile.low_bandwidth_mode
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get preferences: {str(e)}"
        )


@router.get("/notifications")
async def get_notifications(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get recent notifications (reminders) for the user."""
    try:
        from models.opportunity import Opportunity
        
        # Get reminders joined with opportunity titles
        reminders = db.query(Reminder, Opportunity.title).join(
            Opportunity, Reminder.opportunity_id == Opportunity.id
        ).filter(
            Reminder.user_id == current_user_id
        ).order_by(Reminder.scheduled_time.desc()).limit(10).all()
        
        return [
            {
                "id": reminder.id,
                "opportunity_id": reminder.opportunity_id,
                "opportunity_title": title,
                "scheduled_time": reminder.scheduled_time.isoformat(),
                "sent": reminder.sent,
                "type": "deadline_reminder"
            }
            for reminder, title in reminders
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get notifications: {str(e)}"
        )


@router.get("/export")
async def export_user_data(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export all user data in JSON format."""
    try:
        user_id = current_user_id
        
        # Get user data
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        # Get profile
        profile = db.query(Profile).filter(Profile.user_id == user_id).first()
        
        # Get tracked opportunities
        tracked = db.query(TrackedOpportunity).filter(
            TrackedOpportunity.user_id == user_id
        ).all()
        
        # Get participation history
        participation = db.query(ParticipationHistory).filter(
            ParticipationHistory.user_id == user_id
        ).all()
        
        # Get reminders
        reminders = db.query(Reminder).filter(
            Reminder.user_id == user_id
        ).all()
        
        # Build export data
        export_data = {
            "user": {
                "id": user.id,
                "email": user.email,
                "phone": user.phone,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "updated_at": user.updated_at.isoformat() if user.updated_at else None
            },
            "profile": {
                "interests": json.loads(profile.interests) if profile and profile.interests else [],
                "skills": json.loads(profile.skills) if profile and profile.skills else [],
                "education_level": profile.education_level if profile else None,
                "notification_email": profile.notification_email if profile else True,
                "notification_sms": profile.notification_sms if profile else False,
                "low_bandwidth_mode": profile.low_bandwidth_mode if profile else False,
                "updated_at": profile.updated_at.isoformat() if profile and profile.updated_at else None
            },
            "tracked_opportunities": [
                {
                    "opportunity_id": t.opportunity_id,
                    "saved_at": t.saved_at.isoformat() if t.saved_at else None,
                    "is_expired": t.is_expired
                }
                for t in tracked
            ],
            "participation_history": [
                {
                    "id": p.id,
                    "opportunity_id": p.opportunity_id,
                    "status": p.status,
                    "notes": p.notes,
                    "timestamp": p.timestamp.isoformat() if p.timestamp else None
                }
                for p in participation
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
            "export_date": __import__('datetime').datetime.utcnow().isoformat()
        }
        
        return JSONResponse(
            content=export_data,
            headers={
                "Content-Disposition": f"attachment; filename=user_data_{user_id}.json"
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to export user data: {str(e)}"
        )
