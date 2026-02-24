"""Opportunity service for managing opportunity listings."""
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from models.opportunity import Opportunity


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
        
        self.db.add(opportunity)
        self.db.commit()
        
        return self._format_opportunity_response(opportunity)
    
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
        
        self.db.commit()
        
        return self._format_opportunity_response(opportunity)
    
    def search_opportunities(self, search_term: Optional[str] = None,
                           opportunity_types: Optional[List[str]] = None,
                           deadline_start: Optional[datetime] = None,
                           deadline_end: Optional[datetime] = None,
                           eligibility: Optional[str] = None,
                           include_archived: bool = False) -> List[Dict[str, Any]]:
        """Search and filter opportunities.
        
        Args:
            search_term: Text to search in title, description, and tags (optional)
            opportunity_types: Filter by types (optional)
            deadline_start: Filter by deadline start date (optional)
            deadline_end: Filter by deadline end date (optional)
            eligibility: Filter by eligibility requirements (optional)
            include_archived: Include archived opportunities (default: False)
            
        Returns:
            List of dictionaries containing opportunity data
        """
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
        return {
            "id": opportunity.id,
            "title": opportunity.title,
            "description": opportunity.description,
            "type": opportunity.type,
            "deadline": opportunity.deadline.isoformat(),
            "application_link": opportunity.application_link,
            "tags": json.loads(opportunity.tags),
            "required_skills": json.loads(opportunity.required_skills),
            "eligibility": opportunity.eligibility,
            "status": opportunity.status,
            "created_at": opportunity.created_at.isoformat(),
            "updated_at": opportunity.updated_at.isoformat()
        }
