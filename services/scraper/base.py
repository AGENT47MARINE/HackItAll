from pydantic import BaseModel, Field
from typing import List, Optional

class OpportunityExtraction(BaseModel):
    """The structured data we expect our Local AI model to return."""
    title: str = Field(description="The name of the hackathon or event.")
    description: str = Field(description="A short 1-2 sentence summary of the event.")
    type: str = Field(description="One of: hackathon, scholarship, internship, skill_program.", default="hackathon")
    deadline: str = Field(description="The application deadline in ISO-8601 format (YYYY-MM-DDTHH:MM:SSZ). Return empty string if not found.")
    application_link: str = Field(description="The URL where users can apply or register.")
    tags: List[str] = Field(description="A list of 3-5 tags categorizing the tech stack (e.g., AI, Web3, React, Hardware).", default_factory=list)
    eligibility: str = Field(description="Who is eligible? (e.g., 'Undergraduate Students', 'Open to all', 'Women only')", default="Open to all")
    required_skills: List[str] = Field(description="Specific technical skills required.", default_factory=list)
    timeline: List[dict] = Field(description="A list of objects with 'label' and 'date'. (e.g., [{'label': 'Registration Ends', 'date': '2025-03-01'}, {'label': 'Result', 'date': '2025-04-15'}])", default_factory=list)
    prizes: List[dict] = Field(description="A list of objects with 'label' and 'value'. (e.g., [{'label': '1st Prize', 'value': '$5,000'}, {'label': '2nd Prize', 'value': '$2,000'}])", default_factory=list)

class BatchOpportunityExtraction(BaseModel):
    """A list of opportunities extracted from a single page."""
    opportunities: List[OpportunityExtraction]

class BaseScraper:
    """Interface for all scrapers."""
    
    def extract(self, url: str) -> Optional[OpportunityExtraction]:
        """Extracts data from the given URL and returns it as a structured Pydantic object."""
        raise NotImplementedError("Subclasses must implement extract()")
