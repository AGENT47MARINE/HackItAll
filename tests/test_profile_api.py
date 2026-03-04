import uuid
"""Tests for profile management API endpoints."""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from unittest.mock import patch

from main import app
from database import Base, get_db
from models import User, Profile, Opportunity, TrackedOpportunity, ParticipationHistory, Reminder
from tests.test_utils import mock_clerk_auth, create_auth_header


# Test database and client are now provided by conftest.py


@pytest.fixture
def test_user(db_session):
    """Create a test user with profile."""
    from services.profile_service import ProfileService
    
    profile_service = ProfileService(db_session)
    user_id = str(uuid.uuid4())
    profile_data = profile_service.create_profile(
        user_id=user_id,
        email="test@example.com",
        education_level="undergraduate",
        interests=["AI", "Machine Learning"],
        skills=["Python", "JavaScript"]
    )
    
    return profile_data


class TestGetProfile:
    """Tests for GET /api/profile endpoint."""
    
    def test_get_profile_success(self, client, test_user):
        """Test successful profile retrieval."""
        with mock_clerk_auth(test_user["id"]):
            response = client.get(
                "/api/profile",
                headers=create_auth_header()
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
        
        assert response.status_code == 401  # No authorization header
    
    def test_get_profile_with_invalid_token(self, client):
        """Test profile retrieval with invalid token."""
        # Mock Clerk to raise an exception for invalid token
        with patch('api.auth.get_current_user', side_effect=Exception("Invalid token")):
            response = client.get(
                "/api/profile",
                headers=create_auth_header("invalid_token")
            )
        
        assert response.status_code == 401
    
    def test_get_profile_display_completeness(self, client, test_user):
        """Test that profile display includes all required fields.
        
        Property 3: Profile display completeness
        Validates: Requirements 1.3
        """
        with mock_clerk_auth(test_user["id"]):
            response = client.get(
                "/api/profile",
                headers=create_auth_header()
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
    
    def test_update_profile_interests(self, client, test_user):
        """Test updating profile interests."""
        update_data = {
            "interests": ["Data Science", "Web Development", "Cloud Computing"]
        }
        
        with mock_clerk_auth(test_user["id"]):
            response = client.put(
                "/api/profile",
                json=update_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["interests"] == update_data["interests"]
    
    def test_update_profile_skills(self, client, test_user):
        """Test updating profile skills."""
        update_data = {
            "skills": ["React", "Node.js", "Docker"]
        }
        
        with mock_clerk_auth(test_user["id"]):
            response = client.put(
                "/api/profile",
                json=update_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["skills"] == update_data["skills"]
    
    def test_update_profile_education_level(self, client, test_user):
        """Test updating education level."""
        update_data = {
            "education_level": "graduate"
        }
        
        with mock_clerk_auth(test_user["id"]):
            response = client.put(
                "/api/profile",
                json=update_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["education_level"] == "graduate"
    
    def test_update_profile_multiple_fields(self, client, test_user):
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
        
        with mock_clerk_auth(test_user["id"]):
            response = client.put(
                "/api/profile",
                json=update_data,
                headers=create_auth_header()
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
    
    def test_update_profile_persistence(self, client, test_user):
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
        
        with mock_clerk_auth(test_user["id"]):
            response = client.put(
                "/api/profile",
                json=update_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 200
        
        # Retrieve profile to verify persistence
        with mock_clerk_auth(test_user["id"]):
            response = client.get(
                "/api/profile",
                headers=create_auth_header()
            )
        
        assert response.status_code == 200
        data = response.json()
        assert data["interests"] == update_data["interests"]
        assert data["skills"] == update_data["skills"]
        assert data["education_level"] == update_data["education_level"]
    
    def test_update_profile_empty_education_level(self, client, test_user):
        """Test that empty education level is rejected.
        
        Property 4: Required field validation
        Validates: Requirements 1.4
        """
        update_data = {
            "education_level": ""
        }
        
        with mock_clerk_auth(test_user["id"]):
            response = client.put(
                "/api/profile",
                json=update_data,
                headers=create_auth_header()
            )
        
        assert response.status_code == 400
        assert "education_level" in response.json()["detail"].lower()
    
    def test_update_profile_without_auth(self, client):
        """Test profile update without authentication."""
        update_data = {
            "interests": ["Test"]
        }
        
        response = client.put("/api/profile", json=update_data)
        
        assert response.status_code == 401
    
    def test_update_profile_with_invalid_token(self, client):
        """Test profile update with invalid token."""
        update_data = {
            "interests": ["Test"]
        }
        
        with patch('api.auth.get_current_user', side_effect=Exception("Invalid token")):
            response = client.put(
                "/api/profile",
                json=update_data,
                headers=create_auth_header("invalid_token")
            )
        
        assert response.status_code == 401


class TestDeleteProfile:
    """Tests for DELETE /api/profile endpoint."""
    
    def test_delete_profile_success(self, client, test_user, db_session):
        """Test successful profile deletion."""
        with mock_clerk_auth(test_user["id"]):
            response = client.delete(
                "/api/profile",
                headers=create_auth_header()
            )
        
        assert response.status_code == 204
        
        # Verify user is deleted from database
        user = db_session.query(User).filter(User.id == test_user["id"]).first()
        assert user is None
    
    def test_delete_profile_cascade(self, client, test_user, db_session):
        """Test that profile is deleted when user is deleted (cascade)."""
        with mock_clerk_auth(test_user["id"]):
            response = client.delete(
                "/api/profile",
                headers=create_auth_header()
            )
        
        assert response.status_code == 204
        
        # Verify profile is also deleted
        profile = db_session.query(Profile).filter(Profile.user_id == test_user["id"]).first()
        assert profile is None
    
    def test_delete_profile_without_auth(self, client):
        """Test profile deletion without authentication."""
        response = client.delete("/api/profile")
        
        assert response.status_code == 401
    
    def test_delete_profile_with_invalid_token(self, client):
        """Test profile deletion with invalid token."""
        with patch('api.auth.get_current_user', side_effect=Exception("Invalid token")):
            response = client.delete(
                "/api/profile",
                headers=create_auth_header("invalid_token")
            )
        
        assert response.status_code == 401
    
    def test_delete_profile_idempotent(self, client, test_user):
        """Test that deleting already deleted profile returns 404."""
        # First deletion
        with mock_clerk_auth(test_user["id"]):
            response = client.delete(
                "/api/profile",
                headers=create_auth_header()
            )
        
        assert response.status_code == 204
        
        # Second deletion attempt should fail (user no longer exists)
        with mock_clerk_auth(test_user["id"]):
            response = client.delete(
                "/api/profile",
                headers=create_auth_header()
            )
        
        assert response.status_code == 404


class TestProfileIntegration:
    """Integration tests for profile management flow."""
    
    def test_authentication_required_for_all_endpoints(self, client):
        """Test that all profile endpoints require authentication."""
        # GET /api/profile
        response = client.get("/api/profile")
        assert response.status_code == 401
        
        # PUT /api/profile
        response = client.put("/api/profile", json={"interests": ["Test"]})
        assert response.status_code == 401
        
        # DELETE /api/profile
        response = client.delete("/api/profile")
        assert response.status_code == 401
