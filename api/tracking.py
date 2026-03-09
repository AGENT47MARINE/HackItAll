"""Tracking and participation history API endpoints."""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from database import get_db
from services.tracker_service import TrackerService
from api.auth import get_current_user


# Router
router = APIRouter(prefix="/api", tags=["tracking"])


# Request/Response Models
class TrackedOpportunityResponse(BaseModel):
    """Response model for tracked opportunity data."""
    user_id: str
    opportunity_id: str
    participation_id: Optional[str] = None
    saved_at: str
    is_expired: bool
    team_status: str
    team_id: Optional[str] = None
    status: str
    current_round: str
    opportunity: dict


class SaveOpportunityRequest(BaseModel):
    """Request model for saving an opportunity."""
    opportunity_id: str = Field(..., description="ID of the opportunity to track")


class ScrapeOpportunityRequest(BaseModel):
    """Request model for scraping and tracking an external opportunity."""
    url: str = Field(..., description="URL of the hackathon/opportunity to scrape and track")


class ParticipationHistoryResponse(BaseModel):
    """Response model for participation history entry."""
    id: str
    user_id: str
    opportunity_id: str
    status: str
    current_round: str
    notes: Optional[str]
    created_at: str


class AddParticipationRequest(BaseModel):
    """Request model for adding participation history."""
    opportunity_id: str = Field(..., description="ID of the opportunity")
    status: str = Field(..., description="Status: applied, accepted, rejected, etc.")
    current_round: Optional[str] = Field(default="1", description="Current round of the hackathon")
    notes: Optional[str] = Field(default=None, description="Optional notes about participation")


class UpdateParticipationRequest(BaseModel):
    """Request model for updating participation status."""
    status: Optional[str] = Field(default=None, description="Updated status")
    current_round: Optional[str] = Field(default=None, description="Updated round")
    notes: Optional[str] = Field(default=None, description="Updated notes")


# Tracked Opportunities Endpoints

@router.post("/tracked", response_model=TrackedOpportunityResponse, status_code=status.HTTP_201_CREATED)
async def save_opportunity(
    request: SaveOpportunityRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Save an opportunity to the user's tracker.
    
    This endpoint allows users to save opportunities they're interested in
    to track deadlines and receive reminders.
    
    Args:
        request: Save opportunity request data
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        Tracked opportunity data
        
    Raises:
        HTTPException: If opportunity not found or already tracked
    """
    tracker_service = TrackerService(db)
    
    try:
        tracked = tracker_service.save_opportunity(
            user_id=current_user_id,
            opportunity_id=request.opportunity_id
        )
        
        return TrackedOpportunityResponse(**tracked)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Opportunity already tracked"
        )


@router.post("/tracked/scrape", response_model=TrackedOpportunityResponse, status_code=status.HTTP_201_CREATED)
async def scrape_and_track_opportunity(
    request: ScrapeOpportunityRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Scrape an external URL, save it to DB (if new), and track it.
    
    Implements the "Scrape-Once" architecture:
    1. Check if URL already exists in database
    2. If not, scrape it using BeautifulSoup
    3. Save opportunity to database
    4. Track it for the user
    """
    from models.opportunity import Opportunity
    from services.scraper.dispatcher import ScraperDispatcher
    
    # 1. Check if URL already exists
    # We do a 'like' search to handle minor http vs https or trailing slash differences
    base_url = request.url.rstrip('/')
    existing_opp = db.query(Opportunity).filter(
        Opportunity.application_link.ilike(f"%{base_url}%")
    ).first()
    
    if existing_opp:
        opportunity_to_track = existing_opp
    else:
        # 2. Doesn't exist, we must scrape using AI Dispatcher
        dispatcher = ScraperDispatcher(use_cloud=False) # Default to local for user-triggered scrapes
        try:
            scraped_data = dispatcher.scrape_single_url(request.url)
        except Exception as e:
            # Fallback to basic ScraperService if AI fails
            from services.scraper_service import ScraperService
            print(f"AI Scraper failed, falling back to basic: {e}")
            scraped_data = ScraperService().scrape_url(request.url)
        
        # 3. Create new Opportunity in Database
        opportunity_to_track = Opportunity(
            title=scraped_data.get("title", "Unknown"),
            description=scraped_data.get("description", ""),
            type=scraped_data.get("type", "hackathon"),
            image_url=scraped_data.get("image_url"),
            deadline=datetime.utcnow(), # Temporary default
            application_link=scraped_data.get("application_link", request.url),
            tags=scraped_data.get("tags", "[]"),
            required_skills=scraped_data.get("required_skills", "[]"),
            status="active"
        )
        db.add(opportunity_to_track)
        db.commit()
        db.refresh(opportunity_to_track)

    # 4. Track it for the user
    tracker_service = TrackerService(db)
    try:
        tracked = tracker_service.save_opportunity(
            user_id=current_user_id,
            opportunity_id=opportunity_to_track.id
        )
        return TrackedOpportunityResponse(**tracked)
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You are already tracking this opportunity!"
        )


@router.get("/tracked", response_model=List[TrackedOpportunityResponse])
async def get_tracked_opportunities(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all tracked opportunities for the current user.
    
    Returns tracked opportunities sorted by deadline (earliest first).
    
    Args:
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        List of tracked opportunities sorted by deadline
    """
    tracker_service = TrackerService(db)
    
    tracked_list = tracker_service.get_tracked_opportunities(current_user_id)
    
    return [TrackedOpportunityResponse(**tracked) for tracked in tracked_list]


@router.delete("/tracked/{opportunity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_tracked_opportunity(
    opportunity_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Remove a tracked opportunity from the user's list.
    
    Args:
        opportunity_id: ID of the opportunity to remove
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        No content on successful deletion
        
    Raises:
        HTTPException: If tracked opportunity not found
    """
    tracker_service = TrackerService(db)
    
    success = tracker_service.remove_tracked_opportunity(
        user_id=current_user_id,
        opportunity_id=opportunity_id
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tracked opportunity not found"
        )
    
    return None



# Import participation service
from services.participation_service import ParticipationService


# Participation History Endpoints

@router.post("/participation", response_model=ParticipationHistoryResponse, status_code=status.HTTP_201_CREATED)
async def add_participation(
    request: AddParticipationRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add a participation history entry.
    
    This endpoint allows users to record their participation in opportunities,
    including application status and outcomes.
    
    Args:
        request: Add participation request data
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        Participation history entry data
        
    Raises:
        HTTPException: If opportunity not found or status is invalid
    """
    participation_service = ParticipationService(db)
    
    try:
        participation = participation_service.add_participation(
            user_id=current_user_id,
            opportunity_id=request.opportunity_id,
            status=request.status,
            current_round=request.current_round,
            notes=request.notes
        )
        
        return ParticipationHistoryResponse(**participation)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/participation/{participation_id}", response_model=ParticipationHistoryResponse)
async def update_participation(
    participation_id: str,
    request: UpdateParticipationRequest,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a participation history entry.
    
    This endpoint allows users to update the status or notes of their
    participation history entries.
    
    Args:
        participation_id: ID of the participation entry to update
        request: Update participation request data
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        Updated participation history entry data
        
    Raises:
        HTTPException: If participation entry not found or status is invalid
    """
    participation_service = ParticipationService(db)
    
    try:
        participation = participation_service.update_participation(
            participation_id=participation_id,
            user_id=current_user_id,
            status=request.status,
            current_round=request.current_round,
            notes=request.notes
        )
        
        if not participation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participation history entry not found"
            )
        
        return ParticipationHistoryResponse(**participation)
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/participation", response_model=List[ParticipationHistoryResponse])
async def get_participation_history(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get participation history for the current user.
    
    Returns all participation history entries for the user,
    ordered by creation date (most recent first).
    
    Args:
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        List of participation history entries
    """
    participation_service = ParticipationService(db)
    
    history = participation_service.get_participation_history(current_user_id)
    
    return [ParticipationHistoryResponse(**entry) for entry in history]
