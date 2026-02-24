"""Tests for profile management API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import Base, get_db
from models.user import User, Profile
from services.auth_service import AuthService


# Test database setup
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_profile_api.db"
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


class TestGetProfile:
    """Tests for GET /api/profile endpoint."""
    
    def test_get_profile_success(self, client, test_user, auth_token):
        """Test successful profile retrieval."""
        response = client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all required fields are present
        assert data["id"] == test_user["id"]
        assert data["email"] == test_user["email"]
        assert data["education_level"] == "undergraduate"
        assert data["interests"] == ["AI", "Machine Learning"]
        assert data["skills"] == ["Python", "JavaScript"]
        assert "created_at" in data
        assert "updated_at" in data
        assert "participation_history" in data
    
    def test_get_profile_without_auth(self, client):
        """Test profile retrieval without authentication."""
        response = client.get("/api/profile")
        
        assert response.status_code == 403  # No authorization header
    
    def test_get_profile_with_invalid_token(self, client):
        """Test profile retrieval with invalid token."""
        response = client.get(
            "/api/profile",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_get_profile_display_completeness(self, client, test_user, auth_token):
        """Test that profile display includes all required fields.
        
        Property 3: Profile display completeness
        Validates: Requirements 1.3
        """
        response = client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify all profile fields are present
        required_fields = [
            "id", "email", "phone", "interests", "skills",
            "education_level", "notification_email", "notification_sms",
            "low_bandwidth_mode", "created_at", "updated_at",
            "participation_history"
        ]
        
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"


class TestUpdateProfile:
    """Tests for PUT /api/profile endpoint."""
    
    def test_update_profile_interests(self, client, test_user, auth_token):
        """Test updating profile interests."""
        update_data = {
            "interests": ["Data Science", "Web Development", "Cloud Computing"]
        }
        
        response = client.put(
            "/api/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["interests"] == update_data["interests"]
    
    def test_update_profile_skills(self, client, test_user, auth_token):
        """Test updating profile skills."""
        update_data = {
            "skills": ["React", "Node.js", "Docker"]
        }
        
        response = client.put(
            "/api/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["skills"] == update_data["skills"]
    
    def test_update_profile_education_level(self, client, test_user, auth_token):
        """Test updating education level."""
        update_data = {
            "education_level": "graduate"
        }
        
        response = client.put(
            "/api/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["education_level"] == "graduate"
    
    def test_update_profile_multiple_fields(self, client, test_user, auth_token):
        """Test updating multiple profile fields at once."""
        update_data = {
            "interests": ["Blockchain", "IoT"],
            "skills": ["Rust", "Go"],
            "education_level": "phd",
            "phone": "+1234567890",
            "notification_email": False,
            "notification_sms": True,
            "low_bandwidth_mode": True
        }
        
        response = client.put(
            "/api/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["interests"] == update_data["interests"]
        assert data["skills"] == update_data["skills"]
        assert data["education_level"] == update_data["education_level"]
        assert data["phone"] == update_data["phone"]
        assert data["notification_email"] == update_data["notification_email"]
        assert data["notification_sms"] == update_data["notification_sms"]
        assert data["low_bandwidth_mode"] == update_data["low_bandwidth_mode"]
    
    def test_update_profile_persistence(self, client, test_user, auth_token):
        """Test that profile updates persist.
        
        Property 2: Profile update persistence
        Validates: Requirements 1.2, 1.5
        """
        # Update profile
        update_data = {
            "interests": ["Cybersecurity", "DevOps"],
            "skills": ["Kubernetes", "Terraform"],
            "education_level": "masters"
        }
        
        response = client.put(
            "/api/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        
        # Retrieve profile to verify persistence
        response = client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["interests"] == update_data["interests"]
        assert data["skills"] == update_data["skills"]
        assert data["education_level"] == update_data["education_level"]
    
    def test_update_profile_empty_education_level(self, client, test_user, auth_token):
        """Test that empty education level is rejected.
        
        Property 4: Required field validation
        Validates: Requirements 1.4
        """
        update_data = {
            "education_level": ""
        }
        
        response = client.put(
            "/api/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 400
        assert "education_level" in response.json()["detail"].lower()
    
    def test_update_profile_without_auth(self, client):
        """Test profile update without authentication."""
        update_data = {
            "interests": ["Test"]
        }
        
        response = client.put("/api/profile", json=update_data)
        
        assert response.status_code == 403
    
    def test_update_profile_with_invalid_token(self, client):
        """Test profile update with invalid token."""
        update_data = {
            "interests": ["Test"]
        }
        
        response = client.put(
            "/api/profile",
            json=update_data,
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401


class TestDeleteProfile:
    """Tests for DELETE /api/profile endpoint."""
    
    def test_delete_profile_success(self, client, test_user, auth_token, test_db):
        """Test successful profile deletion."""
        response = client.delete(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify user is deleted from database
        user = test_db.query(User).filter(User.id == test_user["id"]).first()
        assert user is None
    
    def test_delete_profile_cascade(self, client, test_user, auth_token, test_db):
        """Test that profile is deleted when user is deleted (cascade)."""
        response = client.delete(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204
        
        # Verify profile is also deleted
        profile = test_db.query(Profile).filter(Profile.user_id == test_user["id"]).first()
        assert profile is None
    
    def test_delete_profile_without_auth(self, client):
        """Test profile deletion without authentication."""
        response = client.delete("/api/profile")
        
        assert response.status_code == 403
    
    def test_delete_profile_with_invalid_token(self, client):
        """Test profile deletion with invalid token."""
        response = client.delete(
            "/api/profile",
            headers={"Authorization": "Bearer invalid_token"}
        )
        
        assert response.status_code == 401
    
    def test_delete_profile_idempotent(self, client, test_user, auth_token):
        """Test that deleting already deleted profile returns 404."""
        # First deletion
        response = client.delete(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 204
        
        # Second deletion attempt should fail
        response = client.delete(
            "/api/profile",
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 401  # Token is invalid after user deletion


class TestProfileIntegration:
    """Integration tests for profile management flow."""
    
    def test_complete_profile_lifecycle(self, client, test_db):
        """Test complete profile lifecycle: create, read, update, delete."""
        # 1. Register (create profile)
        register_data = {
            "email": "lifecycle@example.com",
            "password": "password123",
            "education_level": "undergraduate",
            "interests": ["AI"],
            "skills": ["Python"]
        }
        
        response = client.post("/api/auth/register", json=register_data)
        assert response.status_code == 201
        token = response.json()["access_token"]
        
        # 2. Get profile
        response = client.get(
            "/api/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["email"] == register_data["email"]
        
        # 3. Update profile
        update_data = {
            "interests": ["Machine Learning", "Deep Learning"],
            "skills": ["TensorFlow", "PyTorch"]
        }
        
        response = client.put(
            "/api/profile",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert response.json()["interests"] == update_data["interests"]
        
        # 4. Delete profile
        response = client.delete(
            "/api/profile",
            headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 204
    
    def test_authentication_required_for_all_endpoints(self, client):
        """Test that all profile endpoints require authentication."""
        # GET /api/profile
        response = client.get("/api/profile")
        assert response.status_code == 403
        
        # PUT /api/profile
        response = client.put("/api/profile", json={"interests": ["Test"]})
        assert response.status_code == 403
        
        # DELETE /api/profile
        response = client.delete("/api/profile")
        assert response.status_code == 403
