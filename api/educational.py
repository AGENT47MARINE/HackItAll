"""Educational content API endpoints."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Dict, Any

from database import get_db
from services.educational_content_service import EducationalContentService
from api.auth import get_current_user


router = APIRouter(prefix="/api", tags=["educational"])


@router.get("/glossary/{term}")
async def get_glossary_term(
    term: str,
    db: Session = Depends(get_db)
):
    """Get glossary definition for a term."""
    service = EducationalContentService(db)
    result = service.get_glossary_term(term)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Glossary term '{term}' not found"
        )
    
    return result


@router.get("/glossary")
async def get_all_glossary_terms(
    db: Session = Depends(get_db)
):
    """Get all glossary terms."""
    service = EducationalContentService(db)
    return service.get_all_glossary_terms()


@router.get("/guides/{guide_type}")
async def get_application_guide(
    guide_type: str,
    db: Session = Depends(get_db)
):
    """Get application guide for a specific opportunity type."""
    service = EducationalContentService(db)
    result = service.get_application_guide(guide_type)
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Guide for '{guide_type}' not found"
        )
    
    return result


@router.get("/guides")
async def get_all_guides(
    db: Session = Depends(get_db)
):
    """Get all application guides."""
    service = EducationalContentService(db)
    return service.get_all_guides()


@router.post("/content/viewed")
async def mark_content_viewed(
    content_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Mark content as viewed by the current user."""
    service = EducationalContentService(db)
    
    try:
        view = service.mark_content_viewed(current_user_id, content_id)
        return {
            "message": "Content marked as viewed",
            "content_id": content_id,
            "viewed_at": view.viewed_at.isoformat()
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark content as viewed: {str(e)}"
        )


@router.get("/content/viewed/{content_id}")
async def check_content_viewed(
    content_id: str,
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Check if user has viewed specific content."""
    service = EducationalContentService(db)
    has_viewed = service.has_viewed_content(current_user_id, content_id)
    
    return {
        "content_id": content_id,
        "has_viewed": has_viewed
    }
