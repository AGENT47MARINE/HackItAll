import sys
try:
    import pydantic
    print(f"DEBUG TEST: pydantic file = {pydantic.__file__}")
    print(f"DEBUG TEST: pydantic version = {pydantic.__version__}")
except ImportError as e:
    print(f"DEBUG TEST: pydantic import failed: {e}")
print(f"DEBUG TEST: sys.path = {sys.path}")

import pytest
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker
from database import Base
import models
from main import app
from database import get_db

@pytest.fixture(scope="function")
def db_session():
    """Create a fresh test database for every test function."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    session = SessionLocal()
    
    # Override get_db dependency
    app.dependency_overrides[get_db] = lambda: session
    
    try:
        yield session
    finally:
        session.close()
        app.dependency_overrides.pop(get_db, None)
        engine.dispose()

@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client with a fresh database session."""
    from fastapi.testclient import TestClient
    with TestClient(app) as c:
        yield c

@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user and profile."""
    from models.user import User, Profile
    import json
    
    user = User(id="test-user-id", email="test@example.com")
    db_session.add(user)
    db_session.flush()
    
    profile = Profile(
        user_id=user.id,
        education_level="Bachelor's",
        interests=json.dumps(["AI", "Web Development"]),
        skills=json.dumps(["Python", "JavaScript"])
    )
    db_session.add(profile)
    db_session.commit()
    
    return {"id": user.id, "email": user.email, "profile": profile}

@pytest.fixture(scope="function")
def auth_token():
    """Return a dummy auth token for testing."""
    return "test-mock-token-123"
