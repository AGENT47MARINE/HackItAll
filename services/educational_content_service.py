"""Educational content service for glossary terms and guides."""
import json
import os
from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from models.user import ContentView


class EducationalContentService:
    """Service for managing educational content."""
    
    def __init__(self, db: Session):
        self.db = db
        self._load_content()
    
    def _load_content(self):
        """Load educational content from JSON files."""
        content_dir = os.path.join(os.path.dirname(__file__), '..', 'content')
        
        # Load glossary
        glossary_path = os.path.join(content_dir, 'glossary.json')
        if os.path.exists(glossary_path):
            with open(glossary_path, 'r') as f:
                self.glossary = json.load(f)
        else:
            self.glossary = self._default_glossary()
        
        # Load guides
        guides_path = os.path.join(content_dir, 'guides.json')
        if os.path.exists(guides_path):
            with open(guides_path, 'r') as f:
                self.guides = json.load(f)
        else:
            self.guides = self._default_guides()
    
    def _default_glossary(self) -> Dict[str, str]:
        """Default glossary terms."""
        return {
            "hackathon": "A hackathon is an event where programmers, designers, and other tech enthusiasts collaborate intensively on software projects over a short period, typically 24-48 hours.",
            "scholarship": "Financial aid awarded to students to help pay for their education, typically based on academic merit, financial need, or other criteria.",
            "internship": "A temporary work experience opportunity that allows students or recent graduates to gain practical skills in their field of study.",
            "fellowship": "A merit-based scholarship or grant that provides financial support for advanced study, research, or professional development.",
            "grant": "Financial assistance that doesn't need to be repaid, typically awarded for specific projects or research.",
            "residency": "An intensive training program in a specific field, often used in medicine, arts, or technology.",
            "bootcamp": "An intensive, short-term training program designed to teach specific technical skills quickly.",
            "mentorship": "A relationship where an experienced person guides and supports someone less experienced in their professional development."
        }
    
    def _default_guides(self) -> Dict[str, Dict[str, Any]]:
        """Default application guides."""
        return {
            "hackathon": {
                "title": "How to Apply to Hackathons",
                "steps": [
                    "Find a hackathon that interests you and check eligibility requirements",
                    "Form a team or register as an individual (check event rules)",
                    "Register on the hackathon platform before the deadline",
                    "Prepare your development environment and tools",
                    "Review the themes and challenges beforehand",
                    "Bring necessary items: laptop, chargers, ID, and enthusiasm!"
                ],
                "tips": [
                    "Start with beginner-friendly hackathons if you're new",
                    "Network with other participants and mentors",
                    "Focus on completing a working prototype rather than perfection",
                    "Document your project well for the presentation"
                ]
            },
            "scholarship": {
                "title": "How to Apply for Scholarships",
                "steps": [
                    "Research scholarships that match your profile and goals",
                    "Check eligibility criteria carefully (GPA, field of study, demographics)",
                    "Gather required documents: transcripts, recommendation letters, essays",
                    "Write a compelling personal statement highlighting your achievements",
                    "Submit your application before the deadline",
                    "Follow up if required and prepare for interviews if applicable"
                ],
                "tips": [
                    "Apply to multiple scholarships to increase your chances",
                    "Tailor each application to the specific scholarship",
                    "Proofread all materials carefully",
                    "Request recommendation letters well in advance"
                ]
            },
            "internship": {
                "title": "How to Apply for Internships",
                "steps": [
                    "Update your resume with relevant skills and experiences",
                    "Write a tailored cover letter for each application",
                    "Submit your application through the company's portal or email",
                    "Prepare for technical interviews and coding challenges",
                    "Follow up after 1-2 weeks if you haven't heard back",
                    "Send thank-you notes after interviews"
                ],
                "tips": [
                    "Start applying 3-6 months before your desired start date",
                    "Build a portfolio or GitHub profile to showcase your work",
                    "Practice common interview questions",
                    "Network through LinkedIn and career fairs"
                ]
            },
            "fellowship": {
                "title": "How to Apply for Fellowships",
                "steps": [
                    "Identify fellowships aligned with your research or career goals",
                    "Review requirements: research proposals, publications, recommendations",
                    "Develop a detailed research or project proposal",
                    "Secure strong letters of recommendation from mentors",
                    "Submit all materials before the deadline",
                    "Prepare for interviews or presentations if selected"
                ],
                "tips": [
                    "Start preparing 6-12 months in advance",
                    "Clearly articulate your research goals and impact",
                    "Demonstrate how the fellowship aligns with your career trajectory",
                    "Seek feedback on your proposal from advisors"
                ]
            }
        }
    
    def get_glossary_term(self, term: str) -> Optional[Dict[str, str]]:
        """Get definition for a glossary term."""
        term_lower = term.lower()
        if term_lower in self.glossary:
            return {
                "term": term,
                "definition": self.glossary[term_lower]
            }
        return None
    
    def get_all_glossary_terms(self) -> Dict[str, str]:
        """Get all glossary terms."""
        return self.glossary
    
    def get_opportunity_type_explanation(self, opportunity_type: str) -> Optional[Dict[str, str]]:
        """Get explanation for an opportunity type."""
        return self.get_glossary_term(opportunity_type)
    
    def get_application_guide(self, guide_type: str) -> Optional[Dict[str, Any]]:
        """Get application guide for a specific opportunity type."""
        guide_type_lower = guide_type.lower()
        if guide_type_lower in self.guides:
            return {
                "type": guide_type,
                **self.guides[guide_type_lower]
            }
        return None
    
    def get_all_guides(self) -> Dict[str, Dict[str, Any]]:
        """Get all application guides."""
        return self.guides
    
    def mark_content_viewed(self, user_id: str, content_id: str) -> ContentView:
        """Mark content as viewed by user."""
        # Check if already viewed
        existing = self.db.query(ContentView).filter(
            ContentView.user_id == user_id,
            ContentView.content_id == content_id
        ).first()
        
        if existing:
            return existing
        
        # Create new view record
        content_view = ContentView(
            user_id=user_id,
            content_id=content_id,
            viewed_at=datetime.utcnow()
        )
        self.db.add(content_view)
        self.db.commit()
        self.db.refresh(content_view)
        return content_view
    
    def has_viewed_content(self, user_id: str, content_id: str) -> bool:
        """Check if user has viewed specific content."""
        view = self.db.query(ContentView).filter(
            ContentView.user_id == user_id,
            ContentView.content_id == content_id
        ).first()
        return view is not None
