import os
import time
import logging
import smtplib
from email.message import EmailMessage
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from models.reminder import Reminder
from models.user import User, Profile
from models.opportunity import Opportunity


class NotificationService:
    """Service for managing notifications and reminders."""
    
    # SMS character limit
    SMS_MAX_LENGTH = 160
    
    def __init__(self, db_session: Session):
        """Initialize the notification service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def schedule_reminder(
        self,
        user_id: str,
        opportunity_id: str,
        scheduled_time: datetime
    ) -> Dict[str, Any]:
        """Schedule a deadline reminder for a user.
        
        Args:
            user_id: User ID
            opportunity_id: Opportunity ID
            scheduled_time: When to send the reminder
            
        Returns:
            Dictionary containing reminder data
        """
        # Check if reminder already exists
        existing = self.db.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.opportunity_id == opportunity_id,
            Reminder.scheduled_time == scheduled_time
        ).first()
        
        if existing:
            return self._format_reminder(existing)
        
        # Create new reminder
        reminder = Reminder(
            user_id=user_id,
            opportunity_id=opportunity_id,
            scheduled_time=scheduled_time,
            sent=False
        )
        
        self.db.add(reminder)
        self.db.commit()
        self.db.refresh(reminder)
        
        return self._format_reminder(reminder)
    
    def schedule_deadline_reminders(
        self,
        user_id: str,
        opportunity_id: str,
        deadline: datetime
    ) -> List[Dict[str, Any]]:
        """Schedule both 7-day and 24-hour reminders for an opportunity.
        
        Args:
            user_id: User ID
            opportunity_id: Opportunity ID
            deadline: Opportunity deadline
            
        Returns:
            List of created reminders
        """
        reminders = []
        now = datetime.utcnow()
        
        # Schedule 7-day reminder (if deadline is more than 7 days away)
        seven_days_before = deadline - timedelta(days=7)
        if seven_days_before > now:
            reminder_7d = self.schedule_reminder(user_id, opportunity_id, seven_days_before)
            reminders.append(reminder_7d)
        
        # Schedule 24-hour reminder (if deadline is more than 24 hours away)
        one_day_before = deadline - timedelta(hours=24)
        if one_day_before > now:
            reminder_24h = self.schedule_reminder(user_id, opportunity_id, one_day_before)
            reminders.append(reminder_24h)
        
        return reminders
    
    def cancel_reminder(self, reminder_id: str) -> bool:
        """Cancel a scheduled reminder.
        
        Args:
            reminder_id: Reminder ID
            
        Returns:
            True if cancelled, False if not found
        """
        reminder = self.db.query(Reminder).filter(Reminder.id == reminder_id).first()
        
        if not reminder:
            return False
        
        self.db.delete(reminder)
        self.db.commit()
        
        return True
    
    def cancel_opportunity_reminders(self, user_id: str, opportunity_id: str) -> int:
        """Cancel all reminders for a specific opportunity.
        
        Args:
            user_id: User ID
            opportunity_id: Opportunity ID
            
        Returns:
            Number of reminders cancelled
        """
        count = self.db.query(Reminder).filter(
            Reminder.user_id == user_id,
            Reminder.opportunity_id == opportunity_id,
            Reminder.sent == False
        ).delete()
        
        self.db.commit()
        
        return count
    
    def process_scheduled_reminders(self) -> int:
        """Process all due reminders and send notifications.
        
        This method should be called by a scheduled job (e.g., every hour).
        
        Returns:
            Number of reminders processed
        """
        now = datetime.utcnow()
        
        # Get all unsent reminders that are due
        due_reminders = self.db.query(Reminder, User, Profile, Opportunity).join(
            User, Reminder.user_id == User.id
        ).join(
            Profile, User.id == Profile.user_id
        ).join(
            Opportunity, Reminder.opportunity_id == Opportunity.id
        ).filter(
            Reminder.sent == False,
            Reminder.scheduled_time <= now
        ).all()
        
        processed_count = 0
        
        for reminder, user, profile, opportunity in due_reminders:
            try:
                # Send notification based on user preferences
                success = self.send_notification(
                    user=user,
                    profile=profile,
                    opportunity=opportunity,
                    reminder_type="deadline"
                )
                
                if success:
                    # Mark as sent
                    reminder.sent = True
                    processed_count += 1
            
            except Exception as e:
                # Log error but continue processing other reminders
                print(f"Error sending reminder {reminder.id}: {str(e)}")
                continue
        
        self.db.commit()
        
        return processed_count
    
    def send_notification(
        self,
        user: User,
        profile: Profile,
        opportunity: Opportunity,
        reminder_type: str = "deadline"
    ) -> bool:
        """Send notification to user via their preferred channels.
        
        Args:
            user: User object
            profile: Profile object
            opportunity: Opportunity object
            reminder_type: Type of reminder (deadline, update, etc.)
            
        Returns:
            True if at least one notification was sent successfully
        """
        success = False
        
        # Send email if enabled
        if profile.notification_email:
            # Check for low-bandwidth mode
            is_low_bandwidth = getattr(profile, 'low_bandwidth_mode', False)
            email_sent = self._send_email_notification(user, opportunity, reminder_type, is_low_bandwidth)
            success = success or email_sent
        
        # Send SMS if enabled
        if profile.notification_sms and user.phone:
            sms_sent = self._send_sms_notification(user, opportunity, reminder_type)
            success = success or sms_sent
        
        return success
    def send_deadline_reminder(
        self,
        user_id: str,
        opportunity: Opportunity,
        reminder_type: str = "general"
    ) -> bool:
        """Send deadline reminder to user.

        Args:
            user_id: User ID
            opportunity: Opportunity object
            reminder_type: Type of reminder (7_day, 24_hour, general)

        Returns:
            True if notification was sent successfully
        """
        from models.user import User, Profile

        # Get user and profile
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            return False

        profile = self.db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return False

        # Send notification
        return self.send_notification(user, profile, opportunity, reminder_type)

    
    def _send_email_notification(
        self,
        user: User,
        opportunity: Opportunity,
        reminder_type: str,
        is_low_bandwidth: bool = False
    ) -> bool:
        """Send email notification with adaptive fallback.
        
        Args:
            user: User object
            opportunity: Opportunity object
            reminder_type: Type of reminder
            is_low_bandwidth: Whether to send plain-text only
            
        Returns:
            True if sent successfully
        """
        subject, body = self.format_email_message(opportunity, reminder_type, is_low_bandwidth)
        
        # Log delivery mode
        mode = "LITE-TEXT" if is_low_bandwidth else "HTML/RICH"
        print(f"[EMAIL] Mode: {mode} | To: {user.email}")
        
        # TODO: Implement actual email sending using SMTP or email service
        # For now, just log the email
        print(f"[EMAIL] To: {user.email}")
        print(f"[EMAIL] Subject: {subject}")
        print(f"[EMAIL] Body: {body}")
        
        # Simulate email sending with retry logic
        return self._send_with_retry(
            lambda: self._send_email(user.email, subject, body),
            max_retries=3
        )
    
    def _send_sms_notification(
        self,
        user: User,
        opportunity: Opportunity,
        reminder_type: str
    ) -> bool:
        """Send SMS notification.
        
        Args:
            user: User object
            opportunity: Opportunity object
            reminder_type: Type of reminder
            
        Returns:
            True if sent successfully
        """
        message = self.format_sms_message(opportunity, reminder_type)
        
        # TODO: Implement actual SMS sending using SMS gateway
        # For now, just log the SMS
        print(f"[SMS] To: {user.phone}")
        print(f"[SMS] Message: {message}")
        
        # Simulate SMS sending with retry logic
        return self._send_with_retry(
            lambda: self._send_sms(user.phone, message),
            max_retries=3
        )
    
    def format_email_message(
        self,
        opportunity: Opportunity,
        reminder_type: str,
        is_low_bandwidth: bool = False
    ) -> tuple[str, str]:
        """Format email notification message.
        
        Args:
            opportunity: Opportunity object
            reminder_type: Type of reminder
            is_low_bandwidth: If True, returns ultra-minimal plain text
            
        Returns:
            Tuple of (subject, body)
        """
        if reminder_type == "deadline":
            days_until = (opportunity.deadline - datetime.utcnow()).days
            
            if days_until <= 1:
                subject = f"⏰ DEADLINE TOMORROW: {opportunity.title}"
                urgency = "tomorrow"
            elif days_until <= 7:
                subject = f"📅 {days_until} days left: {opportunity.title}"
                urgency = f"in {days_until} days"
            else:
                subject = f"📅 Upcoming: {opportunity.title}"
                urgency = f"on {opportunity.deadline.strftime('%B %d, %Y')}"
            
            if is_low_bandwidth:
                # Minimal plain text for poor connections
                body = (
                    f"Reminder: {opportunity.title} is due {urgency}.\n\n"
                    f"Deadline: {opportunity.deadline.strftime('%m/%d/%Y %I:%M%p')}\n"
                    f"Apply: {opportunity.application_link}\n\n"
                    f"---\n"
                    f"Sent via HackItAll Lite"
                ).strip()
            else:
                body = f"""
Hello!

This is a reminder that the deadline for "{opportunity.title}" is {urgency}.

Opportunity Details:
- Title: {opportunity.title}
- Type: {opportunity.type.capitalize()}
- Deadline: {opportunity.deadline.strftime('%B %d, %Y at %I:%M %p UTC')}
- Application Link: {opportunity.application_link}

Description:
{opportunity.description}

Don't miss this opportunity! Apply now.

Best regards,
Opportunity Access Platform
                """.strip()
        
        else:
            subject = f"Update: {opportunity.title}"
            body = f"There's an update regarding {opportunity.title}."
        
        return subject, body
    
    def format_sms_message(
        self,
        opportunity: Opportunity,
        reminder_type: str
    ) -> str:
        """Format SMS notification message (max 160 characters).
        
        Args:
            opportunity: Opportunity object
            reminder_type: Type of reminder
            
        Returns:
            SMS message string (max 160 chars)
        """
        if reminder_type == "deadline":
            days_until = (opportunity.deadline - datetime.utcnow()).days
            
            if days_until <= 1:
                message = f"⏰ TOMORROW: {opportunity.title} deadline! Apply: {opportunity.application_link}"
            elif days_until <= 7:
                message = f"📅 {days_until}d left: {opportunity.title}. Apply: {opportunity.application_link}"
            else:
                deadline_str = opportunity.deadline.strftime('%m/%d')
                message = f"📅 {opportunity.title} due {deadline_str}. Apply: {opportunity.application_link}"
        else:
            message = f"Update: {opportunity.title}. Check: {opportunity.application_link}"
        
        # Truncate if too long
        if len(message) > self.SMS_MAX_LENGTH:
            message = message[:self.SMS_MAX_LENGTH - 3] + "..."
        
        return message
    
    def _send_with_retry(self, send_func, max_retries: int = 3) -> bool:
        """Send notification with exponential backoff retry logic.
        
        Args:
            send_func: Function to call for sending
            max_retries: Maximum number of retry attempts
            
        Returns:
            True if sent successfully
        """
        for attempt in range(max_retries):
            try:
                send_func()
                return True
            except Exception as e:
                if attempt < max_retries - 1:
                    # Exponential backoff: 1s, 2s, 4s
                    wait_time = 2 ** attempt
                    print(f"Retry attempt {attempt + 1} after {wait_time}s: {str(e)}")
                    time.sleep(wait_time)
                else:
                    print(f"Failed after {max_retries} attempts: {str(e)}")
                    return False
        
        return False
    
    def _send_email(self, to: str, subject: str, body: str):
        """Actual email sending implementation using SMTP or AWS SES."""
        # 1. Check for AWS SES Configuration (Preferred for production)
        use_ses = os.getenv("USE_AWS_SES", "False").lower() == "true"
        
        if use_ses:
            import boto3
            try:
                ses_client = boto3.client("ses", region_name=os.getenv("AWS_REGION", "us-east-1"))
                ses_client.send_email(
                    Source=os.getenv("SMTP_USER"), # SES Verified Identity
                    Destination={"ToAddresses": [to]},
                    Message={
                        "Subject": {"Data": subject},
                        "Body": {"Text": {"Data": body}}
                    }
                )
                print(f"Successfully sent email via AWS SES to {to}")
                return
            except Exception as e:
                print(f"AWS SES failed, falling back to SMTP: {e}")

        # 2. Fallback to Standard SMTP
        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_user = os.getenv("SMTP_USER")
        smtp_password = os.getenv("SMTP_PASSWORD")

        if not smtp_user or not smtp_password:
            # Fallback to logging if not configured
            print(f"[PREVIEW ONLY] Email to {to} would be sent if SMTP/SES was configured.")
            return

        msg = EmailMessage()
        msg.set_content(body)
        msg['Subject'] = subject
        msg['From'] = smtp_user
        msg['To'] = to

        try:
            with smtplib.SMTP(smtp_host, smtp_port) as server:
                server.starttls()  # Secure the connection
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            print(f"Successfully sent email to {to}")
        except Exception as e:
            print(f"Failed to send email to {to}: {str(e)}")
            raise
    
    def _send_sms(self, to: str, message: str):
        """Actual SMS sending implementation (placeholder).
        
        TODO: Implement using SMS gateway (Twilio, AWS SNS, etc.)
        """
        # Placeholder - would use SMS gateway
        sms_api_key = os.getenv("SMS_API_KEY")
        if not sms_api_key:
            raise Exception("SMS gateway not configured")
        
        # Simulate success
        pass
    
    def _format_reminder(self, reminder: Reminder) -> Dict[str, Any]:
        """Format reminder data for response.
        
        Args:
            reminder: Reminder model instance
            
        Returns:
            Dictionary containing formatted reminder data
        """
        return {
            "id": reminder.id,
            "user_id": reminder.user_id,
            "opportunity_id": reminder.opportunity_id,
            "scheduled_time": reminder.scheduled_time.isoformat(),
            "sent": reminder.sent,
            "created_at": reminder.created_at.isoformat()
        }
