
import os
import sys

# Add the project root to sys.path
sys.path.append('c:/Users/yagye/OneDrive/Desktop/HackItAll')

from database import SessionLocal
from models.reminder import Reminder
from models.opportunity import Opportunity
from models.user import User
from sqlalchemy.orm import Session

def debug_notifications():
    db = SessionLocal()
    try:
        # Get first user
        user = db.query(User).first()
        if not user:
            print("No users found in database")
            return
            
        current_user_id = user.id
        print(f"Testing for user_id: {current_user_id}")
        
        # Exact query from api/notifications.py
        reminders = db.query(Reminder, Opportunity).join(
            Opportunity, Reminder.opportunity_id == Opportunity.id
        ).filter(
            Reminder.user_id == current_user_id
        ).order_by(Reminder.scheduled_time.desc()).limit(20).all()
        
        print(f"Found {len(reminders)} reminders")
        
        for reminder, opportunity in reminders:
            print(f"Reminder ID: {reminder.id}, Opportunity Title: {opportunity.title}")
            # Generate message based on type
            msg = f"Reminder for {opportunity.title}"
            if reminder.type == "submission_3h":
                msg = f"Urgent: 3 hours left for {opportunity.title}!"
            elif reminder.type == "submission_24h":
                msg = f"Deadline tomorrow for {opportunity.title}."
            elif reminder.type == "hackathon_1d":
                msg = f"Hackathon starts tomorrow: {opportunity.title}."
                
            scheduled_time = reminder.scheduled_time.isoformat()
            print(f"  Message: {msg}")
            print(f"  Time: {scheduled_time}")
            
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    debug_notifications()
