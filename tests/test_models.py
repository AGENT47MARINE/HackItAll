"""Tests for database models."""
import pytest
import json
from datetime import datetime
from models.user import User, Profile
from database import Base, engine


class TestUserModel:
    """Tests for User model."""
    
    def test_user_creation(self):
        """Test creating a User instance."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password",
            phone="+1234567890"
        )
        
        assert user.email == "test@example.com"
        assert user.password_hash == "hashed_password"
        assert user.phone == "+1234567890"
        assert user.id is not None  # UUID should be generated
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_without_phone(self):
        """Test creating a User without phone number."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        
        assert user.email == "test@example.com"
        assert user.phone is None


class TestProfileModel:
    """Tests for Profile model."""
    
    def test_profile_creation(self):
        """Test creating a Profile instance."""
        profile = Profile(
            user_id="test-user-id",
            interests=json.dumps(["AI", "Machine Learning"]),
            skills=json.dumps(["Python", "SQL"]),
            education_level="undergraduate",
            notification_email=True,
            notification_sms=False,
            low_bandwidth_mode=False
        )
        
        assert profile.user_id == "test-user-id"
        assert json.loads(profile.interests) == ["AI", "Machine Learning"]
        assert json.loads(profile.skills) == ["Python", "SQL"]
        assert profile.education_level == "undergraduate"
        assert profile.notification_email is True
        assert profile.notification_sms is False
        assert profile.low_bandwidth_mode is False
        assert isinstance(profile.updated_at, datetime)
    
    def test_profile_defaults(self):
        """Test Profile default values."""
        profile = Profile(
            user_id="test-user-id",
            education_level="undergraduate"
        )
        
        assert profile.interests == "[]"
        assert profile.skills == "[]"
        assert profile.notification_email is True
        assert profile.notification_sms is False
        assert profile.low_bandwidth_mode is False


class TestDatabaseSchema:
    """Tests for database schema creation."""
    
    def test_tables_can_be_created(self):
        """Test that database tables can be created without errors."""
        # This will create all tables defined in Base
        Base.metadata.create_all(bind=engine)
        
        # Verify tables exist
        from sqlalchemy import inspect
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        assert "users" in table_names
        assert "profiles" in table_names
    
    def test_user_table_columns(self):
        """Test User table has all required columns."""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('users')}
        
        assert 'id' in columns
        assert 'email' in columns
        assert 'password_hash' in columns
        assert 'phone' in columns
        assert 'created_at' in columns
        assert 'updated_at' in columns
    
    def test_profile_table_columns(self):
        """Test Profile table has all required columns."""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('profiles')}
        
        assert 'user_id' in columns
        assert 'interests' in columns
        assert 'skills' in columns
        assert 'education_level' in columns
        assert 'notification_email' in columns
        assert 'notification_sms' in columns
        assert 'low_bandwidth_mode' in columns
        assert 'updated_at' in columns
    
    def test_user_email_index(self):
        """Test that email column has an index."""
        from sqlalchemy import inspect
        inspector = inspect(engine)
        indexes = inspector.get_indexes('users')
        
        # Check if there's an index on email (either explicit or from unique constraint)
        email_indexed = any(
            'email' in idx.get('column_names', []) 
            for idx in indexes
        )
        
        # Email should be indexed (either through explicit index or unique constraint)
        assert email_indexed or any(
            'email' in col['name'] 
            for col in inspector.get_columns('users') 
            if col.get('unique', False)
        )
