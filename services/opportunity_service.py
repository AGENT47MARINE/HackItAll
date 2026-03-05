"""Opportunity service for managing opportunity listings."""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from email_validator import validate_email, EmailNotValidError

from models.opportunity import Opportunity
from utils.formatters import ResponseFormatter


class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass


class OpportunityService:
    """Service for managing opportunity listings with CRUD operations."""
    
    def __init__(self, db_session: Session):
        """Initialize the opportunity service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session
    
    def _validate_opportunity_data(self, title: Optional[str] = None,
                                   description: Optional[str] = None,
                                   deadline: Optional[datetime] = None,
                                   application_link: Optional[str] = None,
                                   opportunity_type: Optional[str] = None) -> None:
        """Validate opportunity data.
        
        Args:
            title: Opportunity title
            description: Opportunity description
            deadline: Application deadline
            application_link: URL to application
            opportunity_type: Type of opportunity
            
        Raises:
            ValidationError: If validation fails
        """
        # Validate required fields
        if title is not None and not title.strip():
            raise ValidationError("title is required and cannot be empty")
        
        if description is not None and not description.strip():
            raise ValidationError("description is required and cannot be empty")
        
        if deadline is not None and not isinstance(deadline, datetime):
            raise ValidationError("deadline must be a datetime object")
        
        if application_link is not None and not application_link.strip():
            raise ValidationError("application_link is required and cannot be empty")
        
        # Validate URL format for application_link
        if application_link is not None:
            if not (application_link.startswith('http://') or application_link.startswith('https://')):
                raise ValidationError("application_link must be a valid URL starting with http:// or https://")
            
            # Additional validation for common malformed URLs that start with http:// but are otherwise invalid
            if len(application_link) < 10 or '.' not in application_link:
                raise ValidationError("application_link is too short or missing a domain dot")
        
        # Validate opportunity type
        if opportunity_type is not None:
            valid_types = ['hackathon', 'scholarship', 'internship', 'skill_program']
            if opportunity_type not in valid_types:
                raise ValidationError(f"type must be one of: {', '.join(valid_types)}")
    
    def create_opportunity(self, title: str, description: str, 
                          opportunity_type: str, deadline: datetime,
                          application_link: str,
                          tags: Optional[List[str]] = None,
                          required_skills: Optional[List[str]] = None,
                          eligibility: Optional[str] = None) -> Dict[str, Any]:
        """Create a new opportunity.
        
        Args:
            title: Opportunity title
            description: Opportunity description
            opportunity_type: Type (hackathon, scholarship, internship, skill_program)
            deadline: Application deadline
            application_link: URL to application
            tags: List of tags (optional)
            required_skills: List of required skills (optional)
            eligibility: Eligibility requirements (optional)
            
        Returns:
            Dictionary containing opportunity data
            
        Raises:
            ValidationError: If validation fails
        """
        # Set defaults
        if tags is None:
            tags = []
        if required_skills is None:
            required_skills = []
        
        # Validate all required fields
        self._validate_opportunity_data(
            title=title,
            description=description,
            deadline=deadline,
            application_link=application_link,
            opportunity_type=opportunity_type
        )
        
        # Create opportunity
        opportunity = Opportunity(
            title=title,
            description=description,
            type=opportunity_type,
            deadline=deadline,
            application_link=application_link,
            tags=json.dumps(tags),
            required_skills=json.dumps(required_skills),
            eligibility=eligibility,
            status="active"
        )
        
        try:
            self.db.add(opportunity)
            self.db.commit()
            return self._format_opportunity_response(opportunity)
        except Exception:
            self.db.rollback()
            raise
    
    def get_opportunity(self, opportunity_id: str) -> Optional[Dict[str, Any]]:
        """Get an opportunity by ID.
        
        Args:
            opportunity_id: Opportunity ID
            
        Returns:
            Dictionary containing opportunity data, or None if not found
        """
        opportunity = self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id
        ).first()
        
        if not opportunity:
            return None
        
        return self._format_opportunity_response(opportunity)
    
    def update_opportunity(self, opportunity_id: str,
                          title: Optional[str] = None,
                          description: Optional[str] = None,
                          opportunity_type: Optional[str] = None,
                          deadline: Optional[datetime] = None,
                          application_link: Optional[str] = None,
                          tags: Optional[List[str]] = None,
                          required_skills: Optional[List[str]] = None,
                          eligibility: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Update an opportunity.
        
        Args:
            opportunity_id: Opportunity ID
            title: Updated title (optional)
            description: Updated description (optional)
            opportunity_type: Updated type (optional)
            deadline: Updated deadline (optional)
            application_link: Updated application link (optional)
            tags: Updated tags (optional)
            required_skills: Updated required skills (optional)
            eligibility: Updated eligibility (optional)
            
        Returns:
            Dictionary containing updated opportunity data, or None if not found
            
        Raises:
            ValidationError: If validation fails
        """
        opportunity = self.db.query(Opportunity).filter(
            Opportunity.id == opportunity_id
        ).first()
        
        if not opportunity:
            return None
        
        # Validate updates
        self._validate_opportunity_data(
            title=title,
            description=description,
            deadline=deadline,
            application_link=application_link,
            opportunity_type=opportunity_type
        )
        
        # Update fields
        if title is not None:
            opportunity.title = title
        
        if description is not None:
            opportunity.description = description
        
        if opportunity_type is not None:
            opportunity.type = opportunity_type
        
        if deadline is not None:
            opportunity.deadline = deadline
        
        if application_link is not None:
            opportunity.application_link = application_link
        
        if tags is not None:
            opportunity.tags = json.dumps(tags)
        
        if required_skills is not None:
            opportunity.required_skills = json.dumps(required_skills)
        
        if eligibility is not None:
            opportunity.eligibility = eligibility
        
        opportunity.updated_at = datetime.utcnow()
        
        try:
            self.db.commit()
            return self._format_opportunity_response(opportunity)
        except Exception:
            self.db.rollback()
            raise
    
    def scrape_and_create_opportunity(self, url: str) -> Dict[str, Any]:
        from services.scraper.dispatcher import ScraperDispatcher
        import dateutil.parser

        dispatcher = ScraperDispatcher()
        existing = self.db.query(Opportunity).filter(Opportunity.source_url == url).first()
        if existing:
            return self._format_opportunity_response(existing)

        extracted_data = dispatcher.execute_scrape(url)
        deadline_dt = datetime.now()
        if extracted_data.get("deadline"):
            try:
                deadline_dt = dateutil.parser.parse(extracted_data["deadline"])
            except:
                pass

        try:
            opp = Opportunity(
                title=extracted_data.get("title", "Unknown Hackathon"),
                description=extracted_data.get("description", "Scraped opportunity"),
                type=extracted_data.get("type", "hackathon"),
                deadline=deadline_dt,
                application_link=extracted_data.get("application_link", url),
                image_url=extracted_data.get("image_url"),
                tags=json.dumps(extracted_data.get("tags", [])),
                required_skills=json.dumps(extracted_data.get("required_skills", [])),
                eligibility=extracted_data.get("eligibility"),
                source_url=url, # Critical for deduplication logic
                status="active"
            )
            self.db.add(opp)
            self.db.commit()
            return self._format_opportunity_response(opp)
        except Exception:
            self.db.rollback()
            raise

    def batch_scrape(self) -> Dict[str, Any]:
        from services.scraper.unstop_spider import UnstopSpider
        from services.scraper.devpost_spider import DevpostSpider

        errors = []
        all_scraped = []
        sources_used = []

        try:
            unstop = UnstopSpider()
            unstop_results = unstop.scrape(max_results=15)
            all_scraped.extend(unstop_results)
            if unstop_results:
                sources_used.append("unstop.com")
        except Exception as e:
            errors.append(f"Unstop spider failed: {str(e)}")

        try:
            devpost = DevpostSpider()
            devpost_results = devpost.scrape(max_results=15)
            all_scraped.extend(devpost_results)
            if devpost_results:
                sources_used.append("devpost.com")
        except Exception as e:
            errors.append(f"Devpost spider failed: {str(e)}")

        new_count = 0
        skipped_count = 0

        for item in all_scraped:
            source_url = item.get("source_url", "")
            if not source_url:
                skipped_count += 1
                continue

            existing = self.db.query(Opportunity).filter(
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
                    tags=json.dumps(item.get("tags", [])),
                    required_skills=json.dumps(item.get("required_skills", [])),
                    eligibility=item.get("eligibility"),
                    location=item.get("location"),
                    location_type=item.get("location_type", "Online"),
                    source_url=source_url,
                    status="active",
                )
                self.db.add(opp)
                new_count += 1
            except Exception as e:
                errors.append(f"Failed to insert '{item.get('title', '?')}': {str(e)}")

        if new_count > 0:
            self.db.commit()

        return {
            "new_count": new_count,
            "skipped_count": skipped_count,
            "sources": sources_used,
            "errors": errors
        }

    def search_opportunities(self, search_term: Optional[str] = None,
                           opportunity_types: Optional[List[str]] = None,
                           deadline_start: Optional[datetime] = None,
                           deadline_end: Optional[datetime] = None,
                           eligibility: Optional[str] = None,
                           include_archived: bool = False,
                           sort_by: Optional[str] = None,
                           user_interests: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Search and filter opportunities.
        
        Args:
            search_term: Text to search in title, description, and tags (optional)
            opportunity_types: Filter by types (optional)
            deadline_start: Filter by deadline start date (optional)
            deadline_end: Filter by deadline end date (optional)
            eligibility: Filter by eligibility requirements (optional)
            include_archived: Include archived opportunities (default: False)
            sort_by: Strategy to rank opportunities ('relevance', 'deadline', 'popularity')
            user_interests: Optional list of user interests for relevance sorting
            
        Returns:
            List of dictionaries containing opportunity data
        """
        from services.ranking_service import RankingService

        query = self.db.query(Opportunity)
        
        # Filter by status
        if not include_archived:
            query = query.filter(Opportunity.status == "active")
        
        # Search term filter
        if search_term:
            search_pattern = f"%{search_term}%"
            query = query.filter(
                or_(
                    Opportunity.title.ilike(search_pattern),
                    Opportunity.description.ilike(search_pattern),
                    Opportunity.tags.ilike(search_pattern)
                )
            )
        
        # Type filter
        if opportunity_types:
            query = query.filter(Opportunity.type.in_(opportunity_types))
        
        # Deadline range filter
        if deadline_start:
            query = query.filter(Opportunity.deadline >= deadline_start)
        
        if deadline_end:
            query = query.filter(Opportunity.deadline <= deadline_end)
        
        # Eligibility filter
        if eligibility:
            query = query.filter(Opportunity.eligibility == eligibility)
        
        opportunities = query.all()
        
        # Apply ranking logic
        ranking_service = RankingService()
        ranked_opportunities = ranking_service.rank_opportunities(
            opportunities=opportunities,
            sort_by=sort_by,
            user_interests=user_interests
        )

        return [self._format_opportunity_response(opp) for opp in ranked_opportunities]
        
    def get_trending(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get trending opportunities based on tracked count.
        
        Args:
            limit: Maximum number of opportunities to return
            
        Returns:
            List of dictionaries containing opportunity data sorted by tracked count
        """
        opportunities = self.db.query(Opportunity).filter(
            Opportunity.status == "active",
            Opportunity.tracked_count > 0
        ).order_by(
            Opportunity.tracked_count.desc()
        ).limit(limit).all()
        
        return [self._format_opportunity_response(opp) for opp in opportunities]
    
    def archive_expired_opportunities(self) -> int:
        """Archive opportunities with deadlines in the past.
        
        Returns:
            Number of opportunities archived
        """
        now = datetime.utcnow()
        
        # Find all active opportunities with past deadlines
        expired_opportunities = self.db.query(Opportunity).filter(
            and_(
                Opportunity.status == "active",
                Opportunity.deadline < now
            )
        ).all()
        
        count = len(expired_opportunities)
        
        # Archive them
        for opportunity in expired_opportunities:
            opportunity.status = "archived"
            opportunity.updated_at = now
        
        if count > 0:
            self.db.commit()
        
        return count
    
    def _format_opportunity_response(self, opportunity: Opportunity) -> Dict[str, Any]:
        """Format opportunity data for response.
        
        Args:
            opportunity: Opportunity model instance
            
        Returns:
            Dictionary containing formatted opportunity data
        """
        # Get tracked count if available
        tracked_count = getattr(opportunity, 'tracked_count', 0)
        
        # Use centralized formatter
        return ResponseFormatter.format_opportunity_response(opportunity, tracked_count)
