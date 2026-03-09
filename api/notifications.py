from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_db
from api.auth import get_current_user
from models.reminder import Reminder
from models.opportunity import Opportunity

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

class NotificationResponse(BaseModel):
    id: str
    opportunity_id: str
    opportunity_title: str
    message: str
    type: str
    scheduled_time: str
    is_read: bool
    sent: bool

@router.get("", response_model=List[NotificationResponse])
async def get_notifications(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get notifications for the current user."""
    # Fetch recent reminders
    reminders = db.query(Reminder, Opportunity).join(
        Opportunity, Reminder.opportunity_id == Opportunity.id
    ).filter(
        Reminder.user_id == current_user_id
    ).order_by(Reminder.scheduled_time.desc()).limit(20).all()
    
    result = []
    for reminder, opportunity in reminders:
        # Generate message based on type
        msg = f"Reminder for {opportunity.title}"
        if reminder.type == "submission_3h":
            msg = f"Urgent: 3 hours left for {opportunity.title}!"
        elif reminder.type == "submission_24h":
            msg = f"Deadline tomorrow for {opportunity.title}."
        elif reminder.type == "hackathon_1d":
            msg = f"Hackathon starts tomorrow: {opportunity.title}."
            
        result.append(NotificationResponse(
            id=reminder.id,
            opportunity_id=opportunity.id,
            opportunity_title=opportunity.title,
            message=msg,
            type=reminder.type,
            scheduled_time=reminder.scheduled_time.isoformat(),
            is_read=reminder.is_read,
            sent=reminder.sent
        ))
    return result

@router.patch("/{notification_id}/read", status_code=status.HTTP_204_NO_CONTENT)
async def mark_as_read(
    notification_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark a notification as read."""
    notification = db.query(Reminder).filter(
        Reminder.id == notification_id,
        Reminder.user_id == current_user_id
    ).first()
    
    if not notification:
        raise HTTPException(status_code=404, detail="Notification not found")
        
    notification.is_read = True
    db.commit()
    return None
