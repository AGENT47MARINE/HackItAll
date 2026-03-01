"""Opportunity management API endpoints."""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from services.opportunity_service import OpportunityService, ValidationError
from services.recommendation_service import RecommendationEngine
from api.auth import get_current_user, get_current_active_user


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
    image_url: Optional[str] = None
    tags: List[str]
    required_skills: List[str]
    eligibility: Optional[str]
    status: str
    tracked_count: int = 0
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


class SkillGapAnalysisResponse(BaseModel):
    """Response model for Am I Ready skill gap analysis."""
    is_ready: bool
    matching_skills: List[str]
    missing_skills: List[str]
    recommendation_text: str


class ProjectIdea(BaseModel):
    title: str
    description: str

class ProjectIdeasResponse(BaseModel):
    """Response model for project ideas."""
    ideas: List[ProjectIdea]


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


@router.get("/opportunities/trending", response_model=List[OpportunityResponse])
async def get_trending_opportunities(
    limit: int = Query(default=5, ge=1, le=20, description="Maximum number of trending opportunities to return"),
    db: Session = Depends(get_db)
):
    """Get trending opportunities based on tracking activity.
    
    Returns opportunities sorted by the number of users who have tracked them.
    
    Args:
        limit: Maximum number of opportunities to return
        db: Database session
        
    Returns:
        List of trending opportunities
    """
    opportunity_service = OpportunityService(db)
    trending_opportunities = opportunity_service.get_trending(limit=limit)
    
    return [OpportunityResponse(**opp) for opp in trending_opportunities]


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


@router.get("/opportunities/{opportunity_id}/analyze-fit", response_model=SkillGapAnalysisResponse)
async def analyze_opportunity_fit(
    opportunity_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Analyze the user's fit for a specific opportunity ('Am I Ready?' feature).
    
    Args:
        opportunity_id: Opportunity ID
        current_user_id: Current user ID from authentication token
        db: Database session
        
    Returns:
        Skill gap analysis response
    """
    # 1. Get User Profile
    from models.user import Profile
    profile = db.query(Profile).filter(Profile.user_id == current_user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    # 2. Get Opportunity
    from models.opportunity import Opportunity
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    # 3. Trigger AI Analysis
    engine = RecommendationEngine(db)
    analysis = engine.analyze_skill_gap(profile, opportunity)
    
    return SkillGapAnalysisResponse(**analysis)


@router.get("/opportunities/{opportunity_id}/ideas", response_model=ProjectIdeasResponse)
async def get_project_ideas(
    opportunity_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Generate dynamic AI project ideas for an opportunity."""
    from models.user import Profile
    profile = db.query(Profile).filter(Profile.user_id == current_user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    from models.opportunity import Opportunity
    opportunity = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
    if not opportunity:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Opportunity not found")

    engine = RecommendationEngine(db)
    ideas = engine.generate_project_ideas(profile, opportunity)
    
    return {"ideas": ideas}
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


class ScrapeRequest(BaseModel):
    url: str = Field(..., min_length=1, description="URL of the hackathon to scrape")

@router.post("/opportunities/scrape", response_model=OpportunityResponse)
async def scrape_opportunity(
    request: ScrapeRequest,
    current_user_id: str = Depends(get_current_user), # Allow users to submit hackathons
    db: Session = Depends(get_db)
):
    """
    Scrapes a hackathon URL dynamically and adds it to the database.
    """
    from services.scraper.dispatcher import ScraperDispatcher
    from datetime import datetime
    import dateutil.parser
    
    dispatcher = ScraperDispatcher()
    
    try:
        # Run Playwright + Ollama
        extracted_data = dispatcher.execute_scrape(request.url)
        
        # Parse the loose date string from AI into a strict datetime
        deadline_dt = datetime.now()
        if extracted_data.get("deadline"):
            try:
                 deadline_dt = dateutil.parser.parse(extracted_data["deadline"])
            except:
                 pass
                 
        # Save to DB
        opportunity_service = OpportunityService(db)
        opportunity = opportunity_service.create_opportunity(
            title=extracted_data.get("title", "Unknown Hackathon"),
            description=extracted_data.get("description", "Scraped opportunity"),
            opportunity_type=extracted_data.get("type", "hackathon"),
            deadline=deadline_dt,
            application_link=extracted_data.get("application_link", request.url),
            image_url=extracted_data.get("image_url"),
            tags=extracted_data.get("tags", []),
            required_skills=extracted_data.get("required_skills", []),
            eligibility=extracted_data.get("eligibility")
        )
        
        return OpportunityResponse(**opportunity)
        
    except Exception as e:
        print(f"Scraping API Error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to scrape URL: {str(e)}"
        )


# Admin Endpoints

@router.post("/admin/opportunities", response_model=OpportunityResponse, status_code=status.HTTP_201_CREATED)
async def create_opportunity(
    request: CreateOpportunityRequest,
    current_user_id: str = Depends(get_current_active_user),
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
    current_user_id: str = Depends(get_current_active_user),
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


class BatchScrapeResponse(BaseModel):
    """Response model for batch scrape results."""
    new_count: int
    skipped_count: int
    sources: List[str]
    errors: List[str]


@router.post("/admin/scrape-batch", response_model=BatchScrapeResponse)
async def batch_scrape(
    db: Session = Depends(get_db)
):
    """Trigger batch scraping from Unstop and Devpost.

    Runs both spiders, deduplicates by source_url, and inserts new
    opportunities into the database.

    Returns:
        Batch scrape results with counts and any errors.
    """
    from services.scraper.unstop_spider import UnstopSpider
    from services.scraper.devpost_spider import DevpostSpider
    from models.opportunity import Opportunity

    errors = []
    all_scraped = []
    sources_used = []

    # Run Unstop spider
    try:
        unstop = UnstopSpider()
        unstop_results = unstop.scrape(max_results=15)
        all_scraped.extend(unstop_results)
        if unstop_results:
            sources_used.append("unstop.com")
    except Exception as e:
        errors.append(f"Unstop spider failed: {str(e)}")

    # Run Devpost spider
    try:
        devpost = DevpostSpider()
        devpost_results = devpost.scrape(max_results=15)
        all_scraped.extend(devpost_results)
        if devpost_results:
            sources_used.append("devpost.com")
    except Exception as e:
        errors.append(f"Devpost spider failed: {str(e)}")

    # Deduplicate and insert
    new_count = 0
    skipped_count = 0

    for item in all_scraped:
        source_url = item.get("source_url", "")

        if not source_url:
            skipped_count += 1
            continue

        # Check if already exists
        existing = db.query(Opportunity).filter(
            Opportunity.source_url == source_url
        ).first()

        if existing:
            skipped_count += 1
            continue

        try:
            opp = Opportunity(
                title=item.get("title", "Unknown"),
                description=item.get("description", "Scraped opportunity"),
                type=item.get("type", "hackathon"),
                deadline=item.get("deadline", datetime.utcnow()),
                application_link=item.get("application_link", source_url),
                image_url=item.get("image_url"),
                tags=item.get("tags", "[]"),
                required_skills=item.get("required_skills", "[]"),
                eligibility=item.get("eligibility"),
                location=item.get("location"),
                location_type=item.get("location_type", "Online"),
                source_url=source_url,
                status="active",
            )
            db.add(opp)
            new_count += 1
        except Exception as e:
            errors.append(f"Failed to insert '{item.get('title', '?')}': {str(e)}")

    if new_count > 0:
        db.commit()

    return BatchScrapeResponse(
        new_count=new_count,
        skipped_count=skipped_count,
        sources=sources_used,
        errors=errors,
    )

