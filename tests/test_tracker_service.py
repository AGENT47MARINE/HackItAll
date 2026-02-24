"""Unit tests for ApplicationTrackerService."""
import pytest
from datetime import datetime, timedelta
from sqlalchemy.exc import IntegrityError

from services.tracker_service import TrackerService
from models.tracking import TrackedOpportunity
from models.opportunity import Opportunity
from models.user import User, Profile


class TestTrackerService:
    """Tests for TrackerService functionality."""
    
    @pytest.fixture
    def tracker_service(self, db_session):
        """Create a TrackerService instance."""
        return TrackerService(db_session)
    
    @pytest.fixture
    def sample_user(self, db_session):
        """Create a sample user for testing."""
        user = User(
            email="test@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        
        profile = Profile(
            user_id=user.id,
            interests='["coding", "hackathons"]',
            skills='["python", "javascript"]',
            education_level="undergraduate"
        )
        db_session.add(profile)
        db_session.commit()
        
        return user
    
    @pytest.fixture
    def sample_opportunity(self, db_session):
        """Create a sample opportunity for testing."""
        opportunity = Opportunity(
            title="Test Hackathon",
            description="A test hackathon event",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags='["coding", "tech"]',
            status="active"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        return opportunity
    
    @pytest.fixture
    def expired_opportunity(self, db_session):
        """Create an expired opportunity for testing."""
        opportunity = Opportunity(
            title="Expired Scholarship",
            description="A scholarship with past deadline",
            type="scholarship",
            deadline=datetime.utcnow() - timedelta(days=5),
            application_link="https://example.com/expired",
            tags='["scholarship"]',
            status="active"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        return opportunity
    
    def test_save_opportunity_success(self, tracker_service, sample_user, sample_opportunity):
        """Test successfully saving an opportunity."""
        result = tracker_service.save_opportunity(
            user_id=sample_user.id,
            opportunity_id=sample_opportunity.id
        )
        
        assert result["user_id"] == sample_user.id
        assert result["opportunity_id"] == sample_opportunity.id
        assert result["is_expired"] == False
        assert "saved_at" in result
        assert result["opportunity"]["title"] == "Test Hackathon"
        assert result["opportunity"]["deadline"] == sample_opportunity.deadline.isoformat()
    
    def test_save_expired_opportunity(self, tracker_service, sample_user, expired_opportunity):
        """Test saving an opportunity that has already expired."""
        result = tracker_service.save_opportunity(
            user_id=sample_user.id,
            opportunity_id=expired_opportunity.id
        )
        
        # Should be marked as expired immediately
        assert result["is_expired"] == True
        assert result["opportunity"]["title"] == "Expired Scholarship"
    
    def test_save_opportunity_nonexistent(self, tracker_service, sample_user):
        """Test saving a non-existent opportunity raises ValueError."""
        with pytest.raises(ValueError, match="not found"):
            tracker_service.save_opportunity(
                user_id=sample_user.id,
                opportunity_id="nonexistent-id"
            )
    
    def test_save_opportunity_duplicate(self, tracker_service, sample_user, sample_opportunity):
        """Test saving the same opportunity twice raises IntegrityError."""
        # Save once
        tracker_service.save_opportunity(
            user_id=sample_user.id,
            opportunity_id=sample_opportunity.id
        )
        
        # Try to save again
        with pytest.raises(IntegrityError, match="already tracked"):
            tracker_service.save_opportunity(
                user_id=sample_user.id,
                opportunity_id=sample_opportunity.id
            )
    
    def test_get_tracked_opportunities_empty(self, tracker_service, sample_user):
        """Test getting tracked opportunities when none exist."""
        result = tracker_service.get_tracked_opportunities(sample_user.id)
        
        assert result == []
    
    def test_get_tracked_opportunities_single(self, tracker_service, sample_user, sample_opportunity):
        """Test getting a single tracked opportunity."""
        tracker_service.save_opportunity(sample_user.id, sample_opportunity.id)
        
        result = tracker_service.get_tracked_opportunities(sample_user.id)
        
        assert len(result) == 1
        assert result[0]["opportunity_id"] == sample_opportunity.id
        assert result[0]["opportunity"]["title"] == "Test Hackathon"
    
    def test_get_tracked_opportunities_sorted_by_deadline(self, tracker_service, sample_user, db_session):
        """Test that tracked opportunities are sorted by deadline (ascending)."""
        # Create opportunities with different deadlines
        opp1 = Opportunity(
            title="Far Future Event",
            description="Event in 60 days",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=60),
            application_link="https://example.com/1",
            tags='[]'
        )
        opp2 = Opportunity(
            title="Near Future Event",
            description="Event in 10 days",
            type="scholarship",
            deadline=datetime.utcnow() + timedelta(days=10),
            application_link="https://example.com/2",
            tags='[]'
        )
        opp3 = Opportunity(
            title="Mid Future Event",
            description="Event in 30 days",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/3",
            tags='[]'
        )
        
        db_session.add_all([opp1, opp2, opp3])
        db_session.commit()
        
        # Save in random order
        tracker_service.save_opportunity(sample_user.id, opp1.id)
        tracker_service.save_opportunity(sample_user.id, opp3.id)
        tracker_service.save_opportunity(sample_user.id, opp2.id)
        
        # Get tracked opportunities
        result = tracker_service.get_tracked_opportunities(sample_user.id)
        
        # Should be sorted by deadline (earliest first)
        assert len(result) == 3
        assert result[0]["opportunity"]["title"] == "Near Future Event"  # 10 days
        assert result[1]["opportunity"]["title"] == "Mid Future Event"   # 30 days
        assert result[2]["opportunity"]["title"] == "Far Future Event"   # 60 days
    
    def test_remove_tracked_opportunity_success(self, tracker_service, sample_user, sample_opportunity):
        """Test successfully removing a tracked opportunity."""
        # Save first
        tracker_service.save_opportunity(sample_user.id, sample_opportunity.id)
        
        # Remove
        result = tracker_service.remove_tracked_opportunity(
            sample_user.id,
            sample_opportunity.id
        )
        
        assert result == True
        
        # Verify it's gone
        tracked = tracker_service.get_tracked_opportunities(sample_user.id)
        assert len(tracked) == 0
    
    def test_remove_tracked_opportunity_not_found(self, tracker_service, sample_user):
        """Test removing a non-existent tracked opportunity returns False."""
        result = tracker_service.remove_tracked_opportunity(
            sample_user.id,
            "nonexistent-id"
        )
        
        assert result == False
    
    def test_mark_as_expired_single(self, tracker_service, sample_user, sample_opportunity):
        """Test marking a single tracked opportunity as expired."""
        # Save opportunity
        tracker_service.save_opportunity(sample_user.id, sample_opportunity.id)
        
        # Mark as expired
        count = tracker_service.mark_as_expired(sample_opportunity.id)
        
        assert count == 1
        
        # Verify it's marked as expired
        tracked = tracker_service.get_tracked_opportunities(sample_user.id)
        assert len(tracked) == 1
        assert tracked[0]["is_expired"] == True
    
    def test_mark_as_expired_multiple_users(self, tracker_service, sample_opportunity, db_session):
        """Test marking an opportunity as expired affects all users tracking it."""
        # Create multiple users
        user1 = User(email="user1@example.com", password_hash="hash1")
        user2 = User(email="user2@example.com", password_hash="hash2")
        db_session.add_all([user1, user2])
        db_session.commit()
        
        # Both users track the same opportunity
        tracker_service.save_opportunity(user1.id, sample_opportunity.id)
        tracker_service.save_opportunity(user2.id, sample_opportunity.id)
        
        # Mark as expired
        count = tracker_service.mark_as_expired(sample_opportunity.id)
        
        assert count == 2
        
        # Verify both are marked as expired
        tracked1 = tracker_service.get_tracked_opportunities(user1.id)
        tracked2 = tracker_service.get_tracked_opportunities(user2.id)
        
        assert tracked1[0]["is_expired"] == True
        assert tracked2[0]["is_expired"] == True
    
    def test_mark_as_expired_already_expired(self, tracker_service, sample_user, sample_opportunity):
        """Test marking an already expired opportunity doesn't double-count."""
        # Save and mark as expired
        tracker_service.save_opportunity(sample_user.id, sample_opportunity.id)
        tracker_service.mark_as_expired(sample_opportunity.id)
        
        # Try to mark as expired again
        count = tracker_service.mark_as_expired(sample_opportunity.id)
        
        assert count == 0  # No updates made
    
    def test_mark_as_expired_nonexistent(self, tracker_service):
        """Test marking a non-existent opportunity as expired."""
        count = tracker_service.mark_as_expired("nonexistent-id")
        
        assert count == 0
    
    def test_format_tracked_opportunity_includes_all_fields(self, tracker_service, sample_user, sample_opportunity):
        """Test that formatted response includes all required fields."""
        result = tracker_service.save_opportunity(sample_user.id, sample_opportunity.id)
        
        # Check top-level fields
        assert "user_id" in result
        assert "opportunity_id" in result
        assert "saved_at" in result
        assert "is_expired" in result
        assert "opportunity" in result
        
        # Check nested opportunity fields
        opp = result["opportunity"]
        assert "id" in opp
        assert "title" in opp
        assert "description" in opp
        assert "type" in opp
        assert "deadline" in opp
        assert "application_link" in opp
        assert "status" in opp
    
    def test_get_tracked_opportunities_with_mixed_expiry(self, tracker_service, sample_user, sample_opportunity, expired_opportunity):
        """Test getting tracked opportunities with both expired and active ones."""
        # Track both opportunities
        tracker_service.save_opportunity(sample_user.id, sample_opportunity.id)
        tracker_service.save_opportunity(sample_user.id, expired_opportunity.id)
        
        result = tracker_service.get_tracked_opportunities(sample_user.id)
        
        # Should get both, sorted by deadline
        assert len(result) == 2
        
        # Expired one should come first (earlier deadline)
        assert result[0]["opportunity_id"] == expired_opportunity.id
        assert result[0]["is_expired"] == True
        
        assert result[1]["opportunity_id"] == sample_opportunity.id
        assert result[1]["is_expired"] == False
