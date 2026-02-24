"""Integration tests for User and Profile models with database."""
import pytest
import json
from sqlalchemy.orm import Session
from models.user import User, Profile
from database import SessionLocal, init_db, engine, Base


@pytest.fixture(scope="function")
def db_session():
    """Create a fresh database session for each test."""
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Create session
    session = SessionLocal()
    
    yield session
    
    # Cleanup
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestUserProfileIntegration:
    """Integration tests for User and Profile models."""
    
    def test_create_user_with_profile(self, db_session: Session):
        """Test creating a user with an associated profile."""
        # Create user
        user = User(
            email="student@example.com",
            password_hash="hashed_password_123",
            phone="+1234567890"
        )
        db_session.add(user)
        db_session.flush()  # Get the user ID
        
        # Create profile
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["AI", "Web Development"]),
            skills=json.dumps(["Python", "JavaScript"]),
            education_level="undergraduate",
            notification_email=True,
            notification_sms=True,
            low_bandwidth_mode=False
        )
        db_session.add(profile)
        db_session.commit()
        
        # Verify user and profile are saved
        saved_user = db_session.query(User).filter_by(email="student@example.com").first()
        assert saved_user is not None
        assert saved_user.email == "student@example.com"
        assert saved_user.profile is not None
        assert saved_user.profile.education_level == "undergraduate"
        assert json.loads(saved_user.profile.interests) == ["AI", "Web Development"]
    
    def test_user_profile_relationship(self, db_session: Session):
        """Test bidirectional relationship between User and Profile."""
        # Create user with profile
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["Data Science"]),
            skills=json.dumps(["R", "Statistics"]),
            education_level="graduate"
        )
        db_session.add(profile)
        db_session.commit()
        
        # Access profile from user
        assert user.profile.education_level == "graduate"
        
        # Access user from profile
        assert profile.user.email == "test@example.com"
    
    def test_cascade_delete(self, db_session: Session):
        """Test that deleting a user cascades to delete the profile."""
        # Create user with profile
        user = User(
            email="delete@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["Testing"]),
            skills=json.dumps(["QA"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        db_session.commit()
        
        user_id = user.id
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Verify profile is also deleted
        remaining_profile = db_session.query(Profile).filter_by(user_id=user_id).first()
        assert remaining_profile is None
    
    def test_unique_email_constraint(self, db_session: Session):
        """Test that email must be unique."""
        # Create first user
        user1 = User(
            email="unique@example.com",
            password_hash="password1"
        )
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            email="unique@example.com",
            password_hash="password2"
        )
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise IntegrityError
            db_session.commit()
    
    def test_profile_requires_user(self, db_session: Session):
        """Test that profile is associated with a user_id."""
        # Note: SQLite doesn't enforce foreign key constraints by default
        # This test verifies the relationship structure exists
        user = User(
            email="fk@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.flush()
        
        # Create profile with valid user_id
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["Test"]),
            skills=json.dumps(["Test"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        db_session.commit()
        
        # Verify profile is associated with user
        saved_profile = db_session.query(Profile).filter_by(user_id=user.id).first()
        assert saved_profile is not None
        assert saved_profile.user_id == user.id
    
    def test_profile_notification_preferences(self, db_session: Session):
        """Test that notification preferences are stored correctly."""
        user = User(
            email="notify@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.flush()
        
        # Test with email only
        profile = Profile(
            user_id=user.id,
            interests=json.dumps([]),
            skills=json.dumps([]),
            education_level="undergraduate",
            notification_email=True,
            notification_sms=False
        )
        db_session.add(profile)
        db_session.commit()
        
        saved_profile = db_session.query(Profile).filter_by(user_id=user.id).first()
        assert saved_profile.notification_email is True
        assert saved_profile.notification_sms is False
    
    def test_low_bandwidth_mode_preference(self, db_session: Session):
        """Test that low bandwidth mode preference is stored correctly."""
        user = User(
            email="bandwidth@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps([]),
            skills=json.dumps([]),
            education_level="undergraduate",
            low_bandwidth_mode=True
        )
        db_session.add(profile)
        db_session.commit()
        
        saved_profile = db_session.query(Profile).filter_by(user_id=user.id).first()
        assert saved_profile.low_bandwidth_mode is True
