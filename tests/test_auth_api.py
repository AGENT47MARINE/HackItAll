"""Integration tests for authentication API endpoints."""
import pytest
from fastapi.testclient import TestClient

from main import app
from database import get_db, Base, engine
from services.profile_service import ProfileService


@pytest.fixture
def client():
    """Create test client."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    client = TestClient(app)
    yield client
    
    # Clean up
    Base.metadata.drop_all(bind=engine)


def test_register_success(client):
    """Test successful user registration."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "newuser@example.com",
            "password": "securepassword123",
            "education_level": "undergraduate",
            "interests": ["technology", "science"],
            "skills": ["python", "javascript"]
        }
    )
    
    assert response.status_code == 201
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == "newuser@example.com"
    assert "user_id" in data


def test_register_duplicate_email(client):
    """Test registration with duplicate email."""
    # Register first user
    client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "password123",
            "education_level": "graduate"
        }
    )
    
    # Try to register with same email
    response = client.post(
        "/api/auth/register",
        json={
            "email": "duplicate@example.com",
            "password": "differentpassword",
            "education_level": "undergraduate"
        }
    )
    
    assert response.status_code == 409
    assert "already registered" in response.json()["detail"].lower()


def test_register_invalid_email(client):
    """Test registration with invalid email."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "not-an-email",
            "password": "password123",
            "education_level": "undergraduate"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_register_short_password(client):
    """Test registration with password too short."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "shortpass@example.com",
            "password": "short",
            "education_level": "undergraduate"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_register_missing_education_level(client):
    """Test registration without education level."""
    response = client.post(
        "/api/auth/register",
        json={
            "email": "noedu@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 422  # Validation error


def test_login_success(client):
    """Test successful login."""
    # Register user first
    email = "loginuser@example.com"
    password = "loginpassword123"
    
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": password,
            "education_level": "graduate"
        }
    )
    
    # Login
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["email"] == email


def test_login_wrong_password(client):
    """Test login with wrong password."""
    # Register user
    email = "wrongpass@example.com"
    
    client.post(
        "/api/auth/register",
        json={
            "email": email,
            "password": "correctpassword",
            "education_level": "undergraduate"
        }
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/auth/login",
        json={
            "email": email,
            "password": "wrongpassword"
        }
    )
    
    assert response.status_code == 401
    assert "invalid" in response.json()["detail"].lower()


def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    response = client.post(
        "/api/auth/login",
        json={
            "email": "nonexistent@example.com",
            "password": "password123"
        }
    )
    
    assert response.status_code == 401


def test_get_current_user_authenticated(client):
    """Test getting current user info with valid token."""
    # Register user
    register_response = client.post(
        "/api/auth/register",
        json={
            "email": "currentuser@example.com",
            "password": "password123",
            "education_level": "graduate",
            "interests": ["ai", "ml"],
            "skills": ["python"]
        }
    )
    
    token = register_response.json()["access_token"]
    
    # Get current user info
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 200
    data = response.json()
    
    assert data["email"] == "currentuser@example.com"
    assert data["education_level"] == "graduate"
    assert data["interests"] == ["ai", "ml"]
    assert data["skills"] == ["python"]


def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get("/api/auth/me")
    
    assert response.status_code == 403  # Forbidden (no credentials)


def test_get_current_user_invalid_token(client):
    """Test getting current user with invalid token."""
    response = client.get(
        "/api/auth/me",
        headers={"Authorization": "Bearer invalid.token.here"}
    )
    
    assert response.status_code == 401


def test_password_is_hashed(client):
    """Test that passwords are hashed in database."""
    from database import SessionLocal
    from models.user import User
    
    # Register user
    password = "plaintextpassword"
    response = client.post(
        "/api/auth/register",
        json={
            "email": "hashtest@example.com",
            "password": password,
            "education_level": "undergraduate"
        }
    )
    
    user_id = response.json()["user_id"]
    
    # Check database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
        
        # Password should be hashed (not equal to plaintext)
        assert user.password_hash != password
        # Hashed password should be longer
        assert len(user.password_hash) > len(password)
    finally:
        db.close()
