"""Tests for tracking and participation history API endpoints."""
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
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tracking_api.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def test_db():
    """Create test database for each test."""
    Base.metadata.create_all(bind=engine)
    yield TestingSessionLocal()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


@pytest.fixture
def test_user(test_db):
    """Create a test user with profile."""
    from services.profile_service import ProfileService
    
    profile_service = ProfileService(test_db)
    profile_data = profile_service.create_profile(
        email="test@example.com",
        password="testpassword123",
        education_level="undergraduate",
        interests=["AI", "Machine Learning"],
        skills=["Python", "JavaScript"]
    )
    
    return profile_data


@pytest.fixture
def auth_token(test_db, test_user):
    """Create authentication token for test user."""
    auth_service = AuthService(test_db)
    token = auth_service.create_access_token(
        user_id=test_user["id"],
        email=test_user["email"]
    )
    return token


@pytest.fixture
def test_opportunity(test_db):
    """Create a test opportunity."""
    from services.opportunity_service import OpportunityService
    
    opportunity_service = OpportunityService(test_db)
    opportunity = opportunity_service.create_opportunity(
        title="Test Hackathon",
        description="A test hackathon for students",
        opportunity_type="hackathon",
        deadline=datetime.utcnow() + timedelta(days=30),
        application_link="https://example.com/apply",
        tags=["AI", "Machine Learning"],
        required_skills=["Python"],
        eligibility="undergraduate"
    )
    
    return opportunity


@pytest.fixture
def expired_opportunity(test_db):
    """Create an expired opportunity."""
    from services.opportunity_service import OpportunityService
    
    opportunity_service = OpportunityService(test_db)
    opportunity = opportunity_service.create_opportunity(
        title="Expired Hackathon",
        description="An expired hackathon",
        opportunity_type="hackathon",
        deadline=datetime.utcnow() - timedelta(days=1),
        application_link="https://example.com/expired",
        tags=["Web Development"],
        required_skills=["JavaScript"],
        eligibility="undergraduate"
    )
    
    return opportunity


class TestSaveOpportunity:
    """Tests for POST /api/tracked endpoint."""
    
    def test_save_opportunity_success(self, client, test_user, test_opportunity, auth_token):
        """Test successfully saving an opportunity."""
        request_data = {
            "opportunity_id": test_opportunity["id"]
        }
        
        response = client.post(
            "/api/tracked",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["user_id"] == test_user["id"]
        assert data["opportunity_id"] == test_opportunity["id"]
        assert data["is_expired"] == False
        assert "saved_at" in data
        assert "opportunity" in data
    
    def test_save_expired_opportunity(self, client, test_user, expired_opportunity, auth_token):
        """Test saving an expired opportunity marks it as expired."""
        request_data = {
            "opportunity_id": expired_opportunity["id"]
        }
        
        response = client.post(
            "/api/tracked",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["is_expired"] == True
    
    def test_save_opportunity_duplicate(self, client, test_user, test_opportunity, auth_token):
        """Test that saving the same opportunity twice returns conflict."""
        request_data = {
            "opportunity_id": test_opportunity["id"]
        }
        
        # First save
        response = client.post(
            "/api/tracked",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        
        # Second save (duplicate)
        response = client.post(
            "/api/tracked",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 409
        assert "already tracked" in response.json()["detail"].lower()
    
    def test_save_nonexistent_opportunity(self, client, test_user, auth_token):
        """Test saving a non-existent opportunity returns 404."""
        request_data = {
            "opportunity_id": "nonexistent-id"
        }
        
        response = client.post(
            "/api/tracked",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_save_opportunity_without_auth(self, client, test_opportunity):
        """Test saving opportunity without authentication."""
        request_data = {
            "opportunity_id": test_opportunity["id"]
        }
        
        response = client.post("/api/tracked", json=request_data)
        assert response.status_code == 403


class TestGetTrackedOpportunities:
    """Tests for GET /api/tracked endpoint."""
    
    def test_get_tracked_opportunities_empty(self, client, test_user, auth_token):
        """Test getting tracked opportunities when none are saved."""
        response = client.get(
            "/api/tracked",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_get_tracked_opportunities_single(self, client, test_user, test_opportunity, auth_token):
        """Test getting tracked opportunities with one saved."""
        # Save opportunity
        client.post(
            "/api/tracked",
            json={"opportunity_id": test_opportunity["id"]},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get tracked opportunities
        response = client.get(
            "/api/tracked",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["opportunity_id"] == test_opportunity["id"]
    
    def test_get_tracked_opportunities_sorted_by_deadline(self, client, test_user, auth_token, test_db):
        """Test that tracked opportunities are sorted by deadline (earliest first).
        
        Property 10: Tracked opportunities ordering
        Validates: Requirements 3.4
        """
        from services.opportunity_service import OpportunityService
        
        opportunity_service = OpportunityService(test_db)
        
        # Create opportunities with different deadlines
        opp1 = opportunity_service.create_opportunity(
            title="Far Future",
            description="Deadline in 60 days",
            opportunity_type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=60),
            application_link="https://example.com/far",
            tags=["AI"],
            required_skills=["Python"]
        )
        
        opp2 = opportunity_service.create_opportunity(
            title="Near Future",
            description="Deadline in 10 days",
            opportunity_type="scholarship",
            deadline=datetime.utcnow() + timedelta(days=10),
            application_link="https://example.com/near",
            tags=["Education"],
            required_skills=[]
        )
        
        opp3 = opportunity_service.create_opportunity(
            title="Mid Future",
            description="Deadline in 30 days",
            opportunity_type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/mid",
            tags=["Career"],
            required_skills=["JavaScript"]
        )
        
        # Save in random order
        client.post("/api/tracked", json={"opportunity_id": opp1["id"]}, 
                   headers={"Authorization": f"Bearer {auth_token}"})
        client.post("/api/tracked", json={"opportunity_id": opp3["id"]}, 
                   headers={"Authorization": f"Bearer {auth_token}"})
        client.post("/api/tracked", json={"opportunity_id": opp2["id"]}, 
                   headers={"Authorization": f"Bearer {auth_token}"})
        
        # Get tracked opportunities
        response = client.get(
            "/api/tracked",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
        
        # Verify sorted by deadline (earliest first)
        assert data[0]["opportunity_id"] == opp2["id"]  # 10 days
        assert data[1]["opportunity_id"] == opp3["id"]  # 30 days
        assert data[2]["opportunity_id"] == opp1["id"]  # 60 days
    
    def test_get_tracked_opportunities_without_auth(self, client):
        """Test getting tracked opportunities without authentication."""
        response = client.get("/api/tracked")
        assert response.status_code == 403


class TestRemoveTrackedOpportunity:
    """Tests for DELETE /api/tracked/:id endpoint."""
    
    def test_remove_tracked_opportunity_success(self, client, test_user, test_opportunity, auth_token):
        """Test successfully removing a tracked opportunity."""
        # Save opportunity
        client.post(
            "/api/tracked",
            json={"opportunity_id": test_opportunity["id"]},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Remove opportunity
        response = client.delete(
            f"/api/tracked/{test_opportunity['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify it's removed
        response = client.get(
            "/api/tracked",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert len(response.json()) == 0
    
    def test_remove_nonexistent_tracked_opportunity(self, client, test_user, auth_token):
        """Test removing a non-existent tracked opportunity returns 404."""
        response = client.delete(
            "/api/tracked/nonexistent-id",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_remove_tracked_opportunity_without_auth(self, client, test_opportunity):
        """Test removing tracked opportunity without authentication."""
        response = client.delete(f"/api/tracked/{test_opportunity['id']}")
        assert response.status_code == 403


class TestAddParticipation:
    """Tests for POST /api/participation endpoint."""
    
    def test_add_participation_applied(self, client, test_user, test_opportunity, auth_token):
        """Test adding participation with 'applied' status."""
        request_data = {
            "opportunity_id": test_opportunity["id"],
            "status": "applied",
            "notes": "Submitted application on time"
        }
        
        response = client.post(
            "/api/participation",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        
        assert data["user_id"] == test_user["id"]
        assert data["opportunity_id"] == test_opportunity["id"]
        assert data["status"] == "applied"
        assert data["notes"] == "Submitted application on time"
        assert "id" in data
        assert "created_at" in data
    
    def test_add_participation_all_statuses(self, client, test_user, auth_token, test_db):
        """Test adding participation with all valid statuses."""
        from services.opportunity_service import OpportunityService
        
        opportunity_service = OpportunityService(test_db)
        statuses = ["applied", "accepted", "rejected", "completed"]
        
        for status in statuses:
            # Create a unique opportunity for each status
            opp = opportunity_service.create_opportunity(
                title=f"Test {status}",
                description=f"Test opportunity for {status}",
                opportunity_type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/{status}",
                tags=["Test"],
                required_skills=[]
            )
            
            request_data = {
                "opportunity_id": opp["id"],
                "status": status
            }
            
            response = client.post(
                "/api/participation",
                json=request_data,
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == 201
            assert response.json()["status"] == status
    
    def test_add_participation_without_notes(self, client, test_user, test_opportunity, auth_token):
        """Test adding participation without notes."""
        request_data = {
            "opportunity_id": test_opportunity["id"],
            "status": "applied"
        }
        
        response = client.post(
            "/api/participation",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["notes"] is None
    
    def test_add_participation_invalid_status(self, client, test_user, test_opportunity, auth_token):
        """Test adding participation with invalid status."""
        request_data = {
            "opportunity_id": test_opportunity["id"],
            "status": "invalid_status"
        }
        
        response = client.post(
            "/api/participation",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "invalid status" in response.json()["detail"].lower()
    
    def test_add_participation_nonexistent_opportunity(self, client, test_user, auth_token):
        """Test adding participation for non-existent opportunity."""
        request_data = {
            "opportunity_id": "nonexistent-id",
            "status": "applied"
        }
        
        response = client.post(
            "/api/participation",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
    
    def test_add_participation_without_auth(self, client, test_opportunity):
        """Test adding participation without authentication."""
        request_data = {
            "opportunity_id": test_opportunity["id"],
            "status": "applied"
        }
        
        response = client.post("/api/participation", json=request_data)
        assert response.status_code == 403


class TestUpdateParticipation:
    """Tests for PUT /api/participation/:id endpoint."""
    
    def test_update_participation_status(self, client, test_user, test_opportunity, auth_token):
        """Test updating participation status."""
        # Add participation
        add_response = client.post(
            "/api/participation",
            json={
                "opportunity_id": test_opportunity["id"],
                "status": "applied"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        participation_id = add_response.json()["id"]
        
        # Update status
        update_data = {
            "status": "accepted"
        }
        
        response = client.put(
            f"/api/participation/{participation_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "accepted"
    
    def test_update_participation_notes(self, client, test_user, test_opportunity, auth_token):
        """Test updating participation notes."""
        # Add participation
        add_response = client.post(
            "/api/participation",
            json={
                "opportunity_id": test_opportunity["id"],
                "status": "applied",
                "notes": "Initial notes"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        participation_id = add_response.json()["id"]
        
        # Update notes
        update_data = {
            "notes": "Updated notes with more details"
        }
        
        response = client.put(
            f"/api/participation/{participation_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == "Updated notes with more details"
    
    def test_update_participation_both_fields(self, client, test_user, test_opportunity, auth_token):
        """Test updating both status and notes."""
        # Add participation
        add_response = client.post(
            "/api/participation",
            json={
                "opportunity_id": test_opportunity["id"],
                "status": "applied"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        participation_id = add_response.json()["id"]
        
        # Update both fields
        update_data = {
            "status": "completed",
            "notes": "Successfully completed the hackathon"
        }
        
        response = client.put(
            f"/api/participation/{participation_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["notes"] == "Successfully completed the hackathon"
    
    def test_update_participation_invalid_status(self, client, test_user, test_opportunity, auth_token):
        """Test updating participation with invalid status."""
        # Add participation
        add_response = client.post(
            "/api/participation",
            json={
                "opportunity_id": test_opportunity["id"],
                "status": "applied"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        participation_id = add_response.json()["id"]
        
        # Update with invalid status
        update_data = {
            "status": "invalid_status"
        }
        
        response = client.put(
            f"/api/participation/{participation_id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
    
    def test_update_nonexistent_participation(self, client, test_user, auth_token):
        """Test updating non-existent participation entry."""
        update_data = {
            "status": "accepted"
        }
        
        response = client.put(
            "/api/participation/nonexistent-id",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 404
    
    def test_update_participation_without_auth(self, client):
        """Test updating participation without authentication."""
        update_data = {
            "status": "accepted"
        }
        
        response = client.put("/api/participation/some-id", json=update_data)
        assert response.status_code == 403


class TestGetParticipationHistory:
    """Tests for GET /api/participation endpoint."""
    
    def test_get_participation_history_empty(self, client, test_user, auth_token):
        """Test getting participation history when none exists."""
        response = client.get(
            "/api/participation",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data == []
    
    def test_get_participation_history_single(self, client, test_user, test_opportunity, auth_token):
        """Test getting participation history with one entry."""
        # Add participation
        client.post(
            "/api/participation",
            json={
                "opportunity_id": test_opportunity["id"],
                "status": "applied",
                "notes": "Test notes"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        # Get history
        response = client.get(
            "/api/participation",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["opportunity_id"] == test_opportunity["id"]
        assert data[0]["status"] == "applied"
        assert data[0]["notes"] == "Test notes"
    
    def test_get_participation_history_multiple(self, client, test_user, auth_token, test_db):
        """Test getting participation history with multiple entries."""
        from services.opportunity_service import OpportunityService
        
        opportunity_service = OpportunityService(test_db)
        
        # Create multiple opportunities
        opportunities = []
        for i in range(3):
            opp = opportunity_service.create_opportunity(
                title=f"Opportunity {i}",
                description=f"Description {i}",
                opportunity_type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/{i}",
                tags=["Test"],
                required_skills=[]
            )
            opportunities.append(opp)
        
        # Add participation for each
        for opp in opportunities:
            client.post(
                "/api/participation",
                json={
                    "opportunity_id": opp["id"],
                    "status": "applied"
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
        
        # Get history
        response = client.get(
            "/api/participation",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3
    
    def test_get_participation_history_without_auth(self, client):
        """Test getting participation history without authentication."""
        response = client.get("/api/participation")
        assert response.status_code == 403


class TestTrackingIntegration:
    """Integration tests for tracking and participation flow."""
    
    def test_complete_tracking_flow(self, client, test_user, test_opportunity, auth_token):
        """Test complete flow: save opportunity, add participation, update status."""
        # 1. Save opportunity to tracker
        response = client.post(
            "/api/tracked",
            json={"opportunity_id": test_opportunity["id"]},
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        
        # 2. Add participation (applied)
        response = client.post(
            "/api/participation",
            json={
                "opportunity_id": test_opportunity["id"],
                "status": "applied",
                "notes": "Submitted application"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 201
        participation_id = response.json()["id"]
        
        # 3. Update participation (accepted)
        response = client.put(
            f"/api/participation/{participation_id}",
            json={
                "status": "accepted",
                "notes": "Got accepted!"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        # 4. Update participation (completed)
        response = client.put(
            f"/api/participation/{participation_id}",
            json={
                "status": "completed",
                "notes": "Successfully completed the hackathon"
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        
        # 5. Verify participation history
        response = client.get(
            "/api/participation",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 200
        history = response.json()
        assert len(history) == 1
        assert history[0]["status"] == "completed"
        
        # 6. Remove from tracker
        response = client.delete(
            f"/api/tracked/{test_opportunity['id']}",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        assert response.status_code == 204
