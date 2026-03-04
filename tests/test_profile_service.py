import uuid
"""Unit tests for ProfileService."""
import pytest
import bcrypt
from sqlalchemy.exc import IntegrityError

from services.profile_service import ProfileService, ValidationError
from models import User, Profile, Opportunity, TrackedOpportunity, ParticipationHistory, Reminder


class TestProfileServiceCreate:
    """Tests for ProfileService.create_profile()."""
    
    def test_create_profile_with_all_fields(self, db_session):
        """Test creating a profile with all fields provided."""
        service = ProfileService(db_session)
        
        result = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="student@example.com",
            education_level="undergraduate",
            interests=["AI", "Machine Learning"],
            skills=["Python", "SQL"],
            phone="+1234567890",
            notification_email=True,
            notification_sms=True,
            low_bandwidth_mode=False
        )
        
        assert result["email"] == "student@example.com"
        assert result["education_level"] == "undergraduate"
        assert result["interests"] == ["AI", "Machine Learning"]
        assert result["skills"] == ["Python", "SQL"]
        assert result["phone"] == "+1234567890"
        assert result["notification_email"] is True
        assert result["notification_sms"] is True
        assert result["low_bandwidth_mode"] is False
        assert result["participation_history"] == []
        assert "id" in result
        assert "created_at" in result
        assert "updated_at" in result
    
    def test_create_profile_with_minimal_fields(self, db_session):
        """Test creating a profile with only required fields."""
        service = ProfileService(db_session)
        
        result = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="minimal@example.com",
            education_level="graduate"
        )
        
        assert result["email"] == "minimal@example.com"
        assert result["education_level"] == "graduate"
        assert result["interests"] == []
        assert result["skills"] == []
        assert result["phone"] is None
        assert result["notification_email"] is True
        assert result["notification_sms"] is False
        assert result["low_bandwidth_mode"] is False
    

    
    def test_create_profile_empty_education_level_fails(self, db_session):
        """Test that empty education_level raises ValidationError."""
        service = ProfileService(db_session)
        
        with pytest.raises(ValidationError, match="education_level is required"):
            service.create_profile(
            user_id=str(uuid.uuid4()),
                email="test@example.com",
                education_level=""
            )
    
    def test_create_profile_whitespace_education_level_fails(self, db_session):
        """Test that whitespace-only education_level raises ValidationError."""
        service = ProfileService(db_session)
        
        with pytest.raises(ValidationError, match="education_level is required"):
            service.create_profile(
            user_id=str(uuid.uuid4()),
                email="test@example.com",
                education_level="   "
            )
    
    def test_create_profile_invalid_email_fails(self, db_session):
        """Test that invalid email format raises ValidationError."""
        service = ProfileService(db_session)
        
        with pytest.raises(ValidationError, match="Invalid email format"):
            service.create_profile(
            user_id=str(uuid.uuid4()),
                email="not_an_email",
                education_level="undergraduate"
            )
    
    def test_create_profile_duplicate_email_fails(self, db_session):
        """Test that duplicate email raises IntegrityError."""
        service = ProfileService(db_session)
        
        # Create first profile
        service.create_profile(
            user_id=str(uuid.uuid4()),
            email="duplicate@example.com",
            education_level="undergraduate"
        )
        
        # Try to create second profile with same email
        with pytest.raises(IntegrityError):
            service.create_profile(
            user_id=str(uuid.uuid4()),
                email="duplicate@example.com",
                education_level="graduate"
            )
    
    def test_create_profile_invalid_interests_type_fails(self, db_session):
        """Test that non-list interests raises ValidationError."""
        service = ProfileService(db_session)
        
        with pytest.raises(ValidationError, match="interests must be a list"):
            service.create_profile(
            user_id=str(uuid.uuid4()),
                email="test@example.com",
                education_level="undergraduate",
                interests="not a list"
            )
    
    def test_create_profile_invalid_skills_type_fails(self, db_session):
        """Test that non-list skills raises ValidationError."""
        service = ProfileService(db_session)
        
        with pytest.raises(ValidationError, match="skills must be a list"):
            service.create_profile(
            user_id=str(uuid.uuid4()),
                email="test@example.com",
                education_level="undergraduate",
                skills="not a list"
            )


class TestProfileServiceGet:
    """Tests for ProfileService.get_profile()."""
    
    def test_get_existing_profile(self, db_session):
        """Test retrieving an existing profile."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="get@example.com",
            education_level="undergraduate",
            interests=["Data Science"],
            skills=["R"]
        )
        
        # Retrieve profile
        result = service.get_profile(created["id"])
        
        assert result is not None
        assert result["id"] == created["id"]
        assert result["email"] == "get@example.com"
        assert result["education_level"] == "undergraduate"
        assert result["interests"] == ["Data Science"]
        assert result["skills"] == ["R"]
    
    def test_get_nonexistent_profile(self, db_session):
        """Test retrieving a non-existent profile returns None."""
        service = ProfileService(db_session)
        
        result = service.get_profile("nonexistent-id")
        
        assert result is None


class TestProfileServiceUpdate:
    """Tests for ProfileService.update_profile()."""
    
    def test_update_interests(self, db_session):
        """Test updating interests."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="update@example.com",
            education_level="undergraduate",
            interests=["AI"]
        )
        
        # Update interests
        updated = service.update_profile(
            user_id=created["id"],
            interests=["AI", "Blockchain", "IoT"]
        )
        
        assert updated["interests"] == ["AI", "Blockchain", "IoT"]
        assert updated["education_level"] == "undergraduate"  # Unchanged
    
    def test_update_skills(self, db_session):
        """Test updating skills."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="skills@example.com",
            education_level="graduate",
            skills=["Python"]
        )
        
        # Update skills
        updated = service.update_profile(
            user_id=created["id"],
            skills=["Python", "Java", "C++"]
        )
        
        assert updated["skills"] == ["Python", "Java", "C++"]
    
    def test_update_education_level(self, db_session):
        """Test updating education level."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="edu@example.com",
            education_level="undergraduate"
        )
        
        # Update education level
        updated = service.update_profile(
            user_id=created["id"],
            education_level="graduate"
        )
        
        assert updated["education_level"] == "graduate"
    
    def test_update_phone(self, db_session):
        """Test updating phone number."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="phone@example.com",
            education_level="undergraduate"
        )
        
        # Update phone
        updated = service.update_profile(
            user_id=created["id"],
            phone="+9876543210"
        )
        
        assert updated["phone"] == "+9876543210"
    
    def test_update_notification_preferences(self, db_session):
        """Test updating notification preferences."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="notify@example.com",
            education_level="undergraduate",
            notification_email=True,
            notification_sms=False
        )
        
        # Update notification preferences
        updated = service.update_profile(
            user_id=created["id"],
            notification_email=False,
            notification_sms=True
        )
        
        assert updated["notification_email"] is False
        assert updated["notification_sms"] is True
    
    def test_update_low_bandwidth_mode(self, db_session):
        """Test updating low bandwidth mode."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="bandwidth@example.com",
            education_level="undergraduate",
            low_bandwidth_mode=False
        )
        
        # Update low bandwidth mode
        updated = service.update_profile(
            user_id=created["id"],
            low_bandwidth_mode=True
        )
        
        assert updated["low_bandwidth_mode"] is True
    
    def test_update_multiple_fields(self, db_session):
        """Test updating multiple fields at once."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="multi@example.com",
            education_level="undergraduate",
            interests=["AI"],
            skills=["Python"]
        )
        
        # Update multiple fields
        updated = service.update_profile(
            user_id=created["id"],
            interests=["AI", "ML"],
            skills=["Python", "TensorFlow"],
            education_level="graduate",
            phone="+1111111111"
        )
        
        assert updated["interests"] == ["AI", "ML"]
        assert updated["skills"] == ["Python", "TensorFlow"]
        assert updated["education_level"] == "graduate"
        assert updated["phone"] == "+1111111111"
    
    def test_update_nonexistent_profile(self, db_session):
        """Test updating a non-existent profile returns None."""
        service = ProfileService(db_session)
        
        result = service.update_profile(
            user_id="nonexistent-id",
            interests=["Test"]
        )
        
        assert result is None
    
    def test_update_empty_education_level_fails(self, db_session):
        """Test that updating to empty education_level raises ValidationError."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="empty@example.com",
            education_level="undergraduate"
        )
        
        # Try to update to empty education level
        with pytest.raises(ValidationError, match="education_level is required"):
            service.update_profile(
                user_id=created["id"],
                education_level=""
            )
    
    def test_update_persistence(self, db_session):
        """Test that updates are persisted to database."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="persist@example.com",
            education_level="undergraduate",
            interests=["Original"]
        )
        
        # Update profile
        service.update_profile(
            user_id=created["id"],
            interests=["Updated"]
        )
        
        # Retrieve profile again
        retrieved = service.get_profile(created["id"])
        
        assert retrieved["interests"] == ["Updated"]


class TestProfileServiceDelete:
    """Tests for ProfileService.delete_profile()."""
    
    def test_delete_existing_profile(self, db_session):
        """Test deleting an existing profile."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="delete@example.com",
            education_level="undergraduate"
        )
        
        # Delete profile
        result = service.delete_profile(created["id"])
        
        assert result is True
        
        # Verify profile is deleted
        retrieved = service.get_profile(created["id"])
        assert retrieved is None
    
    def test_delete_nonexistent_profile(self, db_session):
        """Test deleting a non-existent profile returns False."""
        service = ProfileService(db_session)
        
        result = service.delete_profile("nonexistent-id")
        
        assert result is False
    
    def test_delete_cascades_to_profile(self, db_session):
        """Test that deleting user also deletes associated profile."""
        service = ProfileService(db_session)
        
        # Create profile
        created = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="cascade@example.com",
            education_level="undergraduate"
        )
        
        user_id = created["id"]
        
        # Verify profile exists
        profile = db_session.query(Profile).filter(Profile.user_id == user_id).first()
        assert profile is not None
        
        # Delete user
        service.delete_profile(user_id)
        
        # Verify profile is also deleted
        profile = db_session.query(Profile).filter(Profile.user_id == user_id).first()
        assert profile is None





class TestProfileServiceEdgeCases:
    """Edge case tests for ProfileService."""
    
    def test_empty_interests_list(self, db_session):
        """Test creating profile with empty interests list."""
        service = ProfileService(db_session)
        
        result = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="empty_interests@example.com",
            education_level="undergraduate",
            interests=[]
        )
        
        assert result["interests"] == []
    
    def test_empty_skills_list(self, db_session):
        """Test creating profile with empty skills list."""
        service = ProfileService(db_session)
        
        result = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="empty_skills@example.com",
            education_level="undergraduate",
            skills=[]
        )
        
        assert result["skills"] == []
    
    def test_special_characters_in_interests(self, db_session):
        """Test interests with special characters."""
        service = ProfileService(db_session)
        
        result = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="special@example.com",
            education_level="undergraduate",
            interests=["AI/ML", "Web Dev (Frontend)", "Data Science & Analytics"]
        )
        
        assert result["interests"] == ["AI/ML", "Web Dev (Frontend)", "Data Science & Analytics"]
    
    def test_unicode_in_profile_data(self, db_session):
        """Test profile data with unicode characters."""
        service = ProfileService(db_session)
        
        result = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="unicode@example.com",
            education_level="undergraduate",
            interests=["机器学习", "データサイエンス", "Künstliche Intelligenz"]
        )
        
        assert result["interests"] == ["机器学习", "データサイエンス", "Künstliche Intelligenz"]
    
    def test_very_long_lists(self, db_session):
        """Test profile with very long interests and skills lists."""
        service = ProfileService(db_session)
        
        long_interests = [f"Interest {i}" for i in range(100)]
        long_skills = [f"Skill {i}" for i in range(100)]
        
        result = service.create_profile(
            user_id=str(uuid.uuid4()),
            email="long@example.com",
            education_level="undergraduate",
            interests=long_interests,
            skills=long_skills
        )
        
        assert len(result["interests"]) == 100
        assert len(result["skills"]) == 100
