"""Tests for opportunity API endpoints."""
import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models.user import User, Profile
from models.opportunity import Opportunity
from services.auth_service import AuthService


# Test database setup
TEST_DATABASE_URL = "sqlite:///./test_opportunity_api.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function", autouse=True)
def setup_database():
    """Create and drop tables for each test."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_user_token(client):
    """Create a test user and return authentication token."""
    # Register a user
    response = client.post(
        "/api/auth/register",
        json={
            "email": "testuser@example.com",
            "password": "testpassword123",
            "education_level": "undergraduate",
            "interests": ["technology", "hackathons"],
            "skills": ["python", "javascript"]
        }
    )
    
    if response.status_code == 201:
        return response.json()["access_token"]
    
    # If registration fails, try to login
    response = client.post(
        "/api/auth/login",
        json={
            "email": "testuser@example.com",
            "password": "testpassword123"
        }
    )
    return response.json()["access_token"]


@pytest.fixture
def test_admin_token():
    """Create a test admin token."""
    db = TestingSessionLocal()
    auth_service = AuthService(db)
    
    # Create admin user
    user = User(
        email="admin@example.com",
        password_hash="hashed_password"
    )
    db.add(user)
    db.commit()
    
    # Create admin token with is_admin flag
    token = auth_service.create_access_token(
        user_id=user.id,
        email=user.email,
        extra_claims={"is_admin": True}
    )
    
    db.close()
    return token


@pytest.fixture
def sample_opportunity():
    """Create a sample opportunity in the database."""
    db = TestingSessionLocal()
    
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
    
    db.add(opportunity)
    db.commit()
    db.refresh(opportunity)
    
    opportunity_id = opportunity.id
    db.close()
    
    return opportunity_id


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
    
    def test_get_recommendations_authenticated(self, client, test_user_token, sample_opportunity):
        """Test getting recommendations with authentication."""
        response = client.get(
            "/api/recommendations",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        
        # Check recommendation structure
        if len(data) > 0:
            assert "opportunity" in data[0]
            assert "relevance_score" in data[0]
            assert isinstance(data[0]["relevance_score"], (int, float))
    
    def test_get_recommendations_with_limit(self, client, test_user_token):
        """Test getting recommendations with limit parameter."""
        response = client.get(
            "/api/recommendations?limit=5",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 5
    
    def test_get_recommendations_without_auth(self, client):
        """Test getting recommendations without authentication."""
        response = client.get("/api/recommendations")
        
        assert response.status_code == 403


class TestCreateOpportunity:
    """Tests for POST /api/admin/opportunities endpoint."""
    
    def test_create_opportunity_as_admin(self, client, test_admin_token):
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
        
        response = client.post(
            "/api/admin/opportunities",
            json=opportunity_data,
            headers={"Authorization": f"Bearer {test_admin_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "New Scholarship"
        assert data["type"] == "scholarship"
        assert "id" in data
    
    def test_create_opportunity_without_admin(self, client, test_user_token):
        """Test creating an opportunity without admin privileges."""
        opportunity_data = {
            "title": "New Scholarship",
            "description": "A scholarship for students",
            "type": "scholarship",
            "deadline": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "application_link": "https://example.com/scholarship"
        }
        
        response = client.post(
            "/api/admin/opportunities",
            json=opportunity_data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 403
    
    def test_create_opportunity_invalid_data(self, client, test_admin_token):
        """Test creating an opportunity with invalid data."""
        opportunity_data = {
            "title": "",  # Empty title
            "description": "A scholarship for students",
            "type": "scholarship",
            "deadline": (datetime.utcnow() + timedelta(days=60)).isoformat(),
            "application_link": "https://example.com/scholarship"
        }
        
        response = client.post(
            "/api/admin/opportunities",
            json=opportunity_data,
            headers={"Authorization": f"Bearer {test_admin_token}"}
        )
        
        assert response.status_code == 422  # Validation error


class TestUpdateOpportunity:
    """Tests for PUT /api/admin/opportunities/:id endpoint."""
    
    def test_update_opportunity_as_admin(self, client, test_admin_token, sample_opportunity):
        """Test updating an opportunity as admin."""
        update_data = {
            "title": "Updated Hackathon Title"
        }
        
        response = client.put(
            f"/api/admin/opportunities/{sample_opportunity}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_admin_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Updated Hackathon Title"
    
    def test_update_opportunity_without_admin(self, client, test_user_token, sample_opportunity):
        """Test updating an opportunity without admin privileges."""
        update_data = {
            "title": "Updated Title"
        }
        
        response = client.put(
            f"/api/admin/opportunities/{sample_opportunity}",
            json=update_data,
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 403
    
    def test_update_nonexistent_opportunity(self, client, test_admin_token):
        """Test updating a nonexistent opportunity."""
        update_data = {
            "title": "Updated Title"
        }
        
        response = client.put(
            "/api/admin/opportunities/nonexistent-id",
            json=update_data,
            headers={"Authorization": f"Bearer {test_admin_token}"}
        )
        
        assert response.status_code == 404
