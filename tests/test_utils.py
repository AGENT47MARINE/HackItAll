"""Test utilities for mocking authentication and common test fixtures."""
from unittest.mock import Mock, patch
from typing import Optional

import contextlib

@contextlib.contextmanager
def mock_clerk_auth(user_id: str):
    """Create a mock for Clerk authentication that returns the specified user_id.
    
    Args:
        user_id: The user ID to return from the mock
        
    Returns:
        A context manager that patches get_current_user
    """
    from main import app
    from api.auth import get_current_user
    
    # Override the dependency
    app.dependency_overrides[get_current_user] = lambda: user_id
    try:
        yield
    finally:
        # Remove the override
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]


@contextlib.contextmanager
def mock_admin_auth(user_id: str):
    """Create a mock for Clerk admin authentication.
    
    Args:
        user_id: The user ID to return from the mock
    """
    from main import app
    from api.auth import get_current_user, get_current_admin_user
    import os
    
    # Save original env and set admin whitelist
    orig_admins = os.getenv("ADMIN_USER_IDS", "")
    os.environ["ADMIN_USER_IDS"] = user_id
    
    # Override both dependencies
    app.dependency_overrides[get_current_user] = lambda: user_id
    app.dependency_overrides[get_current_admin_user] = lambda: user_id
    
    try:
        yield
    finally:
        if get_current_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_user]
        if get_current_admin_user in app.dependency_overrides:
            del app.dependency_overrides[get_current_admin_user]
        os.environ["ADMIN_USER_IDS"] = orig_admins


def create_auth_header(token: str = "mock-clerk-token") -> dict:
    """Create an authorization header for testing.
    
    Args:
        token: The token to include (can be any string for mocked tests)
        
    Returns:
        Dictionary with Authorization header
    """
    return {"Authorization": f"Bearer {token}"}
