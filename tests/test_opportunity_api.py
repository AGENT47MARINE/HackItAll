import uuid
"""Tests for opportunity API endpoints."""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from main import app
from database import Base, get_db
from models import User, Profile, Opportunity, TrackedOpportunity, ParticipationHistory, Reminder
from tests.test_utils import mock_clerk_auth, mock_admin_auth, create_auth_header


# Test database and client are now provided by conftest.py


@pytest.fixture
def auth_token():
    """Return a dummy auth token."""
    return "test_mock_token_123"


@pytest.fixture
def test_user(db_session):
    """Create a test user and return profile data."""
    from services.profile_service import ProfileService
    
    profile_service = ProfileService(db_session)
    user_id = str(uuid.uuid4())
    profile_data = profile_service.create_profile(
        user_id=user_id,
        email="testuser@example.com",
        education_level="undergraduate",
        interests=["technology", "hackathons"],
        skills=["python", "javascript"]
    )
    return profile_data


@pytest.fixture
def test_admin_user(db_session):
    """Create a test admin user."""
    from services.profile_service import ProfileService
    
    profile_service = ProfileService(db_session)
    user_id = str(uuid.uuid4())
    profile_data = profile_service.create_profile(
        user_id=user_id,
        email="admin@example.com",
        education_level="graduate",
        interests=["administration"],
        skills=["management"]
    )
    return profile_data


@pytest.fixture
def sample_opportunity(db_session):
    """Create a sample opportunity in the database."""
    opportunity = Opportunity(
        title="Test Hackathon",
        description="A test hackathon for students",
        type="hackathon",
        deadline=datetime.utcnow() + timedelta(days=30),
        application_link="https://example.com/apply",
        tags='["technology", "coding"]',
        required_skills='["python"]',
        eligibility="undergraduate",
        status="active"
    )
    
    db_session.add(opportunity)
    db_session.commit()
    db_session.refresh(opportunity)
    
    return opportunity.id


class TestSearchOpportunities:
    """Tests for GET /api/opportunities endpoint."""
    
    def test_search_all_opportunities(self, client, sample_opportunity):
        """Test searching for all opportunities."""
        response = client.get("/api/opportunities")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert data[0]["title"] == "Test Hackathon"
    
    def test_search_with_text_query(self, client, sample_opportunity):
        """Test searching with text query."""
        response = client.get("/api/opportunities?search=hackathon")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert "hackathon" in data[0]["title"].lower()
    
    def test_search_by_type(self, client, sample_opportunity):
        """Test filtering by opportunity type."""
        response = client.get("/api/opportunities?type=hackathon")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1
        assert data[0]["type"] == "hackathon"
    
    def test_search_no_results(self, client):
        """Test search with no matching results."""
        response = client.get("/api/opportunities?search=nonexistent")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0


class TestGetOpportunity:
    """Tests for GET /api/opportunities/:id endpoint."""
    
    def test_get_existing_opportunity(self, client, sample_opportunity):
        """Test getting an existing opportunity by ID."""
        response = client.get(f"/api/opportunities/{sample_opportunity}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == sample_opportunity
        assert data["title"] == "Test Hackathon"
        assert "description" in data
        assert "deadline" in data
        assert "application_link" in data
    
    def test_get_nonexistent_opportunity(self, client):
        """Test getting a nonexistent opportunity."""
        response = client.get("/api/opportunities/nonexistent-id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestGetRecommendations:
    """Tests for GET /api/recommendations endpoint."""
    
    def test_get_recommendations_authenticated(self, client, test_user, sample_opportunity):
        """Test getting recommendations with authentication."""
        with mock_clerk_auth(test_user["id"]):
            response = client.get(
                "/api/recommendations",
                headers=create_auth_header()
            )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check recommendation structure
        if len(data) > 0:
            assert "opportunity" in data[0]
            assert "relevance_score" in data[0]
            assert isinstance(data[0]["relevance_score"], (int, float))
    
    def test_get_recommendations_with_limit(self, client, test_user):
        """Test getting recommendations with limit parameter."""
        with mock_clerk_auth(test_user["id"]):
            response = client.get(
                "/api/recommendations?limit=5",
                headers=create_auth_header()
            )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_get_recommendations_without_auth(self, client):
        """Test getting recommendations without authentication."""
        response = client.get("/api/recommendations")
        
        assert response.status_code == 401


class TestCreateOpportunity:
    """Tests for POST /api/admin/opportunities endpoint."""
    
    def test_create_opportunity_as_admin(self, client, test_admin_user):
        """Test creating an opportunity as admin."""
        opportunity_data = {
            "title": "New Scholarship",
            "description": "A scholarship for students",
            "type": "scholarship",
            "deadline": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "application_link": "https://example.com/scholarship",
            "tags": ["education", "funding"],
            "required_skills": [],
            "eligibility": "undergraduate"
        }
        
        with mock_admin_auth(test_admin_user["id"]):
            response = client.post(
                "/api/admin/opportunities",
                json=opportunity_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Scholarship"
        assert data["type"] == "scholarship"
        assert "id" in data
    
    def test_create_opportunity_without_admin(self, client, test_user):
        """Test creating an opportunity without admin privileges."""
        opportunity_data = {
            "title": "New Scholarship",
            "description": "A scholarship for students",
            "type": "scholarship",
            "deadline": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "application_link": "https://example.com/scholarship"
        }
        
        with mock_clerk_auth(test_user["id"]):
            response = client.post(
                "/api/admin/opportunities",
                json=opportunity_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 403
    
    def test_create_opportunity_invalid_data(self, client, test_admin_user):
        """Test creating an opportunity with invalid data."""
        opportunity_data = {
            "title": "",  # Empty title
            "description": "A scholarship for students",
            "type": "scholarship",
            "deadline": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "application_link": "https://example.com/scholarship"
        }
        
        with mock_admin_auth(test_admin_user["id"]):
            response = client.post(
                "/api/admin/opportunities",
                json=opportunity_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 422  # Validation error


class TestUpdateOpportunity:
    """Tests for PUT /api/admin/opportunities/:id endpoint."""
    
    def test_update_opportunity_as_admin(self, client, test_admin_user, sample_opportunity):
        """Test updating an opportunity as admin."""
        update_data = {
            "title": "Updated Hackathon Title"
        }
        
        with mock_admin_auth(test_admin_user["id"]):
            response = client.put(
                f"/api/admin/opportunities/{sample_opportunity}",
                json=update_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Hackathon Title"
    
    def test_update_opportunity_without_admin(self, client, test_user, sample_opportunity):
        """Test updating an opportunity without admin privileges."""
        update_data = {
            "title": "Updated Title"
        }
        
        with mock_clerk_auth(test_user["id"]):
            response = client.put(
                f"/api/admin/opportunities/{sample_opportunity}",
                json=update_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 403
    
    def test_update_nonexistent_opportunity(self, client, test_admin_user):
        """Test updating a nonexistent opportunity."""
        update_data = {
            "title": "Updated Title"
        }
        
        from tests.test_utils import mock_admin_auth
        with mock_admin_auth(test_admin_user["id"]):
            response = client.put(
                "/api/admin/opportunities/nonexistent-id",
                json=update_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 404
