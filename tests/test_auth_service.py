"""Tests for authentication service."""
import pytest
from jose import jwt

from services.auth_service import AuthService, AuthenticationError
from services.profile_service import ProfileService
from config import config


def test_create_access_token(db_session):
    """Test JWT token creation."""
    auth_service = AuthService(db_session)
    
    user_id = "test-user-123"
    email = "test@example.com"
    
    token = auth_service.create_access_token(user_id, email)
    
    # Verify token is a string
    assert isinstance(token, str)
    assert len(token) > 0
    
    # Decode and verify payload
    payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    assert payload["sub"] == user_id
    assert payload["email"] == email
    assert "exp" in payload


def test_verify_token_valid(db_session):
    """Test token verification with valid token."""
    auth_service = AuthService(db_session)
    
    user_id = "test-user-456"
    email = "verify@example.com"
    
    # Create token
    token = auth_service.create_access_token(user_id, email)
    
    # Verify token
    payload = auth_service.verify_token(token)
    
    assert payload["user_id"] == user_id
    assert payload["email"] == email


def test_verify_token_invalid(db_session):
    """Test token verification with invalid token."""
    auth_service = AuthService(db_session)
    
    invalid_token = "invalid.token.here"
    
    with pytest.raises(AuthenticationError):
        auth_service.verify_token(invalid_token)


def test_authenticate_user_success(db_session):
    """Test successful user authentication."""
    profile_service = ProfileService(db_session)
    auth_service = AuthService(db_session)
    
    # Create a user
    email = "auth@example.com"
    password = "testpassword123"
    profile_service.create_profile(
        email=email,
        password=password,
        education_level="undergraduate"
    )
    
    # Authenticate
    user = auth_service.authenticate_user(email, password)
    
    assert user is not None
    assert user.email == email


def test_authenticate_user_wrong_password(db_session):
    """Test authentication with wrong password."""
    profile_service = ProfileService(db_session)
    auth_service = AuthService(db_session)
    
    # Create a user
    email = "wrongpass@example.com"
    password = "correctpassword"
    profile_service.create_profile(
        email=email,
        password=password,
        education_level="undergraduate"
    )
    
    # Try to authenticate with wrong password
    user = auth_service.authenticate_user(email, "wrongpassword")
    
    assert user is None


def test_authenticate_user_nonexistent(db_session):
    """Test authentication with non-existent user."""
    auth_service = AuthService(db_session)
    
    user = auth_service.authenticate_user("nonexistent@example.com", "password")
    
    assert user is None


def test_get_user_by_id(db_session):
    """Test getting user by ID."""
    profile_service = ProfileService(db_session)
    auth_service = AuthService(db_session)
    
    # Create a user
    profile_data = profile_service.create_profile(
        email="getuser@example.com",
        password="password123",
        education_level="graduate"
    )
    
    user_id = profile_data["id"]
    
    # Get user by ID
    user = auth_service.get_user_by_id(user_id)
    
    assert user is not None
    assert user.id == user_id
    assert user.email == "getuser@example.com"


def test_get_user_by_id_nonexistent(db_session):
    """Test getting non-existent user by ID."""
    auth_service = AuthService(db_session)
    
    user = auth_service.get_user_by_id("nonexistent-id")
    
    assert user is None
