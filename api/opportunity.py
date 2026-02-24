"""Opportunity management API endpoints."""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from services.opportunity_service import OpportunityService, ValidationError
from services.recommendation_service import RecommendationEngine
from api.auth import get_current_user, require_admin


# Router
router = APIRouter(prefix="/api", tags=["opportunities"])


# Request/Response Models
class OpportunityResponse(BaseModel):
    """Response model for opportunity data."""
    id: str
    title: str
    description: str
    type: str
    deadline: str
    application_link: str
    tags: List[str]
    required_skills: List[str]
    eligibility: Optional[str]
    status: str
    created_at: str
    updated_at: str


class CreateOpportunityRequest(BaseModel):
    """Request model for creating an opportunity."""
    title: str = Field(..., min_length=1, description="Opportunity title")
    description: str = Field(..., min_length=1, description="Opportunity description")
    type: str = Field(..., description="Type: hackathon, scholarship, internship, or skill_program")
    deadline: datetime = Field(..., description="Application deadline")
    application_link: str = Field(..., min_length=1, description="URL to application")
    tags: Optional[List[str]] = Field(default=[], description="List of tags")
    required_skills: Optional[List[str]] = Field(default=[], description="List of required skills")
    eligibility: Optional[str] = Field(default=None, description="Eligibility requirements")


class UpdateOpportunityRequest(BaseModel):
    """Request model for updating an opportunity."""
    title: Optional[str] = Field(default=None, min_length=1)
    description: Optional[str] = Field(default=None, min_length=1)
    type: Optional[str] = None
    deadline: Optional[datetime] = None
    application_link: Optional[str] = Field(default=None, min_length=1)
    tags: Optional[List[str]] = None
    required_skills: Optional[List[str]] = None
    eligibility: Optional[str] = None


class RecommendationResponse(BaseModel):
    """Response model for recommendations."""
    opportunity: OpportunityResponse
    relevance_score: float


# Public Endpoints

@router.get("/opportunities", response_model=List[OpportunityResponse])
async def search_opportunities(
    search: Optional[str] = Query(default=None, description="Search term for title, description, or tags"),
    type: Optional[List[str]] = Query(default=None, description="Filter by opportunity types"),
    deadline_start: Optional[datetime] = Query(default=None, description="Filter by deadline start date"),
    deadline_end: Optional[datetime] = Query(default=None, description="Filter by deadline end date"),
    eligibility: Optional[str] = Query(default=None, description="Filter by eligibility requirements"),
    db: Session = Depends(get_db)
):
    """Search and filter opportunities.
    
    This endpoint allows searching for opportunities using various filters:
    - search: Text search in title, description, and tags
    - type: Filter by opportunity types (can specify multiple)
    - deadline_start/deadline_end: Filter by deadline range
    - eligibility: Filter by eligibility requirements
    
    All filters are combined with AND logic.
    
    Args:
        search: Search term (optional)
        type: List of opportunity types to filter by (optional)
        deadline_start: Start of deadline range (optional)
        deadline_end: End of deadline range (optional)
        eligibility: Eligibility requirement filter (optional)
        db: Database session
        
    Returns:
        List of opportunities matching the search criteria
    """
    opportunity_service = OpportunityService(db)
    
    opportunities = opportunity_service.search_opportunities(
        search_term=search,
        opportunity_types=type,
        deadline_start=deadline_start,
        deadline_end=deadline_end,
        eligibility=eligibility,
        include_archived=False
    )
    
    return [OpportunityResponse(**opp) for opp in opportunities]


@router.get("/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def get_opportunity(
    opportunity_id: str,
    db: Session = Depends(get_db)
):
    """Get opportunity details by ID.
    
    Args:
        opportunity_id: Opportunity ID
        db: Database session
        
    Returns:
        Opportunity details
        
    Raises:
        HTTPException: If opportunity not found
    """
    opportunity_service = OpportunityService(db)
    
    opportunity = opportunity_service.get_opportunity(opportunity_id)
    
    if not opportunity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Opportunity not found"
        )
    
    return OpportunityResponse(**opportunity)


@router.get("/recommendations", response_model=List[RecommendationResponse])
async def get_recommendations(
    limit: int = Query(default=10, ge=1, le=50, description="Maximum number of recommendations"),
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get personalized opportunity recommendations.
    
    This endpoint generates personalized recommendations based on the user's profile,
    including their interests, skills, education level, and participation history.
    
    Recommendations are ranked by relevance score in descending order.
    
    Args:
        limit: Maximum number of recommendations to return (1-50, default: 10)
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        List of recommended opportunities with relevance scores
    """
    recommendation_engine = RecommendationEngine(db)
    
    # Generate recommendations
    scored_opportunities = recommendation_engine.generate_recommendations(
        user_id=current_user_id,
        limit=limit
    )
    
    # Format response
    recommendations = []
    for opportunity, score in scored_opportunities:
        opportunity_service = OpportunityService(db)
        opportunity_data = opportunity_service._format_opportunity_response(opportunity)
        
        recommendations.append(
            RecommendationResponse(
                opportunity=OpportunityResponse(**opportunity_data),
                relevance_score=round(score, 3)
            )
        )
    
    return recommendations


# Admin Endpoints

@router.post("/admin/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    request: CreateOpportunityRequest,
    current_user_id: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Create a new opportunity (admin only).
    
    This endpoint allows administrators to create new opportunity listings.
    All required fields must be provided and will be validated.
    
    Args:
        request: Opportunity creation data
        current_user_id: Current admin user ID from authentication token
        db: Database session
        
    Returns:
        Created opportunity data
        
    Raises:
        HTTPException: If validation fails or user is not admin
    """
    opportunity_service = OpportunityService(db)
    
    try:
        opportunity = opportunity_service.create_opportunity(
            title=request.title,
            description=request.description,
            opportunity_type=request.type,
            deadline=request.deadline,
            application_link=request.application_link,
            tags=request.tags,
            required_skills=request.required_skills,
            eligibility=request.eligibility
        )
        
        return OpportunityResponse(**opportunity)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/admin/opportunities/{opportunity_id}", response_model=OpportunityResponse)
async def update_opportunity(
    opportunity_id: str,
    request: UpdateOpportunityRequest,
    current_user_id: str = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """Update an opportunity (admin only).
    
    This endpoint allows administrators to update existing opportunity listings.
    Only provided fields will be updated; others remain unchanged.
    
    Args:
        opportunity_id: Opportunity ID to update
        request: Opportunity update data
        current_user_id: Current admin user ID from authentication token
        db: Database session
        
    Returns:
        Updated opportunity data
        
    Raises:
        HTTPException: If validation fails, opportunity not found, or user is not admin
    """
    opportunity_service = OpportunityService(db)
    
    try:
        opportunity = opportunity_service.update_opportunity(
            opportunity_id=opportunity_id,
            title=request.title,
            description=request.description,
            opportunity_type=request.type,
            deadline=request.deadline,
            application_link=request.application_link,
            tags=request.tags,
            required_skills=request.required_skills,
            eligibility=request.eligibility
        )
        
        if not opportunity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Opportunity not found"
            )
        
        return OpportunityResponse(**opportunity)
        
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
