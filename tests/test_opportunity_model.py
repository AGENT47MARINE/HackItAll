"""Tests for Opportunity model."""
import pytest
from datetime import datetime, timedelta
from models.opportunity import Opportunity
from database import Base, engine


class TestOpportunityModel:
    """Test suite for Opportunity model."""
    
    def test_opportunity_creation_with_required_fields(self):
        """Test creating an opportunity with all required fields."""
        deadline = datetime.utcnow() + timedelta(days=30)
        
        opportunity = Opportunity(
            title="Summer Hackathon 2024",
            description="A 48-hour coding competition for students",
            type="hackathon",
            deadline=deadline,
            application_link="https://example.com/apply"
        )
        
        assert opportunity.id is not None
        assert opportunity.title == "Summer Hackathon 2024"
        assert opportunity.description == "A 48-hour coding competition for students"
        assert opportunity.type == "hackathon"
        assert opportunity.deadline == deadline
        assert opportunity.application_link == "https://example.com/apply"
        assert opportunity.status == "active"
        assert opportunity.tags == "[]"
        assert opportunity.required_skills == "[]"
        assert opportunity.created_at is not None
        assert opportunity.updated_at is not None
    
    def test_opportunity_creation_with_all_fields(self):
        """Test creating an opportunity with all fields including optional ones."""
        deadline = datetime.utcnow() + timedelta(days=60)
        
        opportunity = Opportunity(
            title="Tech Scholarship",
            description="Full scholarship for computer science students",
            type="scholarship",
            deadline=deadline,
            application_link="https://example.com/scholarship",
            tags='["technology", "education", "funding"]',
            required_skills='["programming", "problem-solving"]',
            eligibility="undergraduate",
            status="active"
        )
        
        assert opportunity.title == "Tech Scholarship"
        assert opportunity.type == "scholarship"
        assert opportunity.tags == '["technology", "education", "funding"]'
        assert opportunity.required_skills == '["programming", "problem-solving"]'
        assert opportunity.eligibility == "undergraduate"
        assert opportunity.status == "active"
    
    def test_opportunity_default_values(self):
        """Test that default values are set correctly."""
        opportunity = Opportunity(
            title="Test Opportunity",
            description="Test description",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com"
        )
        
        assert opportunity.status == "active"
        assert opportunity.tags == "[]"
        assert opportunity.required_skills == "[]"
        assert opportunity.created_at is not None
        assert opportunity.updated_at is not None
    
    def test_opportunity_repr(self):
        """Test the string representation of an opportunity."""
        opportunity = Opportunity(
            title="Test Opportunity",
            description="Test description",
            type="skill_program",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com"
        )
        
        repr_str = repr(opportunity)
        assert "Opportunity" in repr_str
        assert opportunity.id in repr_str
        assert "Test Opportunity" in repr_str
        assert "skill_program" in repr_str
        assert "active" in repr_str
