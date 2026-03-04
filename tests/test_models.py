"""Tests for database models."""
import pytest
import json
from datetime import datetime
from models.user import User, Profile
from models.opportunity import Opportunity
from models.tracking import TrackedOpportunity, ParticipationHistory
from models.reminder import Reminder
from database import Base, engine


class TestUserModel:
    """Tests for User model."""
    
    def test_user_creation(self):
        """Test creating a User instance."""
        user = User(
            email="test@example.com",
            phone="+1234567890"
        )
        
        assert user.email == "test@example.com"
        assert user.phone == "+1234567890"
        assert user.id is not None  # UUID should be generated
        assert isinstance(user.created_at, datetime)
        assert isinstance(user.updated_at, datetime)
    
    def test_user_without_phone(self):
        """Test creating a User without phone number."""
        user = User(
            email="test@example.com"
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



class TestTrackedOpportunityModel:
    """Tests for TrackedOpportunity model."""
    
    def test_tracked_opportunity_creation(self):
        """Test creating a TrackedOpportunity instance."""
        from models.tracking import TrackedOpportunity
        
        tracked = TrackedOpportunity(
            user_id="test-user-id",
            opportunity_id="test-opportunity-id"
        )
        
        assert tracked.user_id == "test-user-id"
        assert tracked.opportunity_id == "test-opportunity-id"
        assert isinstance(tracked.saved_at, datetime)
        assert tracked.is_expired is False
    
    def test_tracked_opportunity_with_expired(self):
        """Test creating a TrackedOpportunity with is_expired flag."""
        from models.tracking import TrackedOpportunity
        
        tracked = TrackedOpportunity(
            user_id="test-user-id",
            opportunity_id="test-opportunity-id",
            is_expired=True
        )
        
        assert tracked.is_expired is True


class TestParticipationHistoryModel:
    """Tests for ParticipationHistory model."""
    
    def test_participation_history_creation(self):
        """Test creating a ParticipationHistory instance."""
        from models.tracking import ParticipationHistory
        
        participation = ParticipationHistory(
            user_id="test-user-id",
            opportunity_id="test-opportunity-id",
            status="applied",
            notes="Submitted application on time"
        )
        
        assert participation.user_id == "test-user-id"
        assert participation.opportunity_id == "test-opportunity-id"
        assert participation.status == "applied"
        assert participation.notes == "Submitted application on time"
        assert participation.id is not None  # UUID should be generated
        assert isinstance(participation.created_at, datetime)
    
    def test_participation_history_without_notes(self):
        """Test creating a ParticipationHistory without notes."""
        from models.tracking import ParticipationHistory
        
        participation = ParticipationHistory(
            user_id="test-user-id",
            opportunity_id="test-opportunity-id",
            status="completed"
        )
        
        assert participation.status == "completed"
        assert participation.notes is None
    
    def test_participation_history_statuses(self):
        """Test different participation statuses."""
        from models.tracking import ParticipationHistory
        
        statuses = ["applied", "accepted", "rejected", "completed"]
        
        for status in statuses:
            participation = ParticipationHistory(
                user_id="test-user-id",
                opportunity_id="test-opportunity-id",
                status=status
            )
            assert participation.status == status


class TestTrackingDatabaseSchema:
    """Tests for tracking tables schema."""
    
    def test_tracking_tables_can_be_created(self):
        """Test that tracking tables can be created without errors."""
        Base.metadata.create_all(bind=engine)
        
        from sqlalchemy import inspect
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        assert "tracked_opportunities" in table_names
        assert "participation_history" in table_names
    
    def test_tracked_opportunities_table_columns(self):
        """Test TrackedOpportunity table has all required columns."""
        Base.metadata.create_all(bind=engine)
        
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('tracked_opportunities')}
        
        assert 'user_id' in columns
        assert 'opportunity_id' in columns
        assert 'saved_at' in columns
        assert 'is_expired' in columns
    
    def test_participation_history_table_columns(self):
        """Test ParticipationHistory table has all required columns."""
        Base.metadata.create_all(bind=engine)
        
        from sqlalchemy import inspect
        inspector = inspect(engine)
        columns = {col['name']: col for col in inspector.get_columns('participation_history')}
        
        assert 'id' in columns
        assert 'user_id' in columns
        assert 'opportunity_id' in columns
        assert 'status' in columns
        assert 'notes' in columns
        assert 'created_at' in columns
    
    def test_tracked_opportunities_indexes(self):
        """Test TrackedOpportunity table has required indexes."""
        Base.metadata.create_all(bind=engine)
        
        from sqlalchemy import inspect
        inspector = inspect(engine)
        indexes = inspector.get_indexes('tracked_opportunities')
        
        # Check for composite index on user_id and is_expired
        index_found = any(
            set(['user_id', 'is_expired']).issubset(set(idx.get('column_names', [])))
            for idx in indexes
        )
        
        assert index_found, "Expected index on (user_id, is_expired) not found"
    
    def test_participation_history_indexes(self):
        """Test ParticipationHistory table has required indexes."""
        Base.metadata.create_all(bind=engine)
        
        from sqlalchemy import inspect
        inspector = inspect(engine)
        indexes = inspector.get_indexes('participation_history')
        
        # Check for index on user_id
        index_found = any(
            'user_id' in idx.get('column_names', [])
            for idx in indexes
        )
        
        assert index_found, "Expected index on user_id not found"
