import os
import logging
from fastapi import APIRouter, Request, Header, HTTPException, Depends
from sqlalchemy.orm import Session
from svix.webhooks import Webhook, WebhookVerificationError

from database import get_db
from models.user import User, Profile
from services.profile_service import ProfileService

router = APIRouter(prefix="/api/webhooks", tags=["webhooks"])
logger = logging.getLogger(__name__)

@router.post("/clerk")
async def clerk_webhook(
    request: Request,
    svix_id: str = Header(default=None, alias="svix-id"),
    svix_timestamp: str = Header(default=None, alias="svix-timestamp"),
    svix_signature: str = Header(default=None, alias="svix-signature"),
    db: Session = Depends(get_db)
):
    """Handle Clerk webhooks for user synchronization."""
    
    # Get the webhook secret from environment variables
    clerk_webhook_secret = os.getenv("CLERK_WEBHOOK_SECRET")
    if not clerk_webhook_secret:
        logger.error("CLERK_WEBHOOK_SECRET not configured")
        raise HTTPException(status_code=500, detail="Webhook secret not configured")
        
    # Check if headers are present
    if not svix_id or not svix_timestamp or not svix_signature:
        raise HTTPException(status_code=400, detail="Missing Svix headers")
        
    # Get the request body
    payload = await request.body()
    
    # Verify the webhook signature
    try:
        wh = Webhook(clerk_webhook_secret)
        msg = wh.verify(
            payload,
            {
                "svix-id": svix_id,
                "svix-timestamp": svix_timestamp,
                "svix-signature": svix_signature,
            }
        )
    except WebhookVerificationError as e:
        logger.error(f"Webhook verification failed: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid webhook signature")
        
    # Process the webhook payload
    event_type = msg.get("type")
    data = msg.get("data", {})
    
    logger.info(f"Received Clerk webhook event: {event_type}")
    
    if event_type == "user.created":
        # Handle user creation
        primary_email_id = data.get("primary_email_address_id")
        emails = data.get("email_addresses", [])
        
        email = None
        for e in emails:
            if e.get("id") == primary_email_id:
                email = e.get("email_address")
                break
                
        if not email and emails:
            email = emails[0].get("email_address")
            
        user_id = data.get("id")
        
        if user_id and email:
            try:
                profile_service = ProfileService(db)
                
                # Check if user already exists to prevent duplicate key errors
                existing_user = db.query(User).filter(User.id == user_id).first()
                if not existing_user:
                    profile_service.create_profile(
                        user_id=user_id,
                        email=email,
                        education_level="Not Specified", # Default since Clerk form might not collect this natively
                        interests=[],
                        skills=[]
                    )
                    logger.info(f"Successfully synced new user {user_id} from Clerk")
            except Exception as e:
                logger.error(f"Error syncing user {user_id}: {str(e)}")
                # We still return 200 to Clerk so it doesn't retry indefinitely,
                # but we log the error for monitoring
                
    elif event_type == "user.deleted":
        user_id = data.get("id")
        if user_id:
            try:
                # SQLAlchemy cascade will delete the associated profile
                user = db.query(User).filter(User.id == user_id).first()
                if user:
                    db.delete(user)
                    db.commit()
                    logger.info(f"Successfully deleted synced user {user_id}")
            except Exception as e:
                db.rollback()
                logger.error(f"Error deleting user {user_id}: {str(e)}")

    return {"status": "success"}
