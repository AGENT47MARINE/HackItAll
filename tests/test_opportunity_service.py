"""Tests for OpportunityService."""
import pytest
from datetime import datetime, timedelta
from services.opportunity_service import OpportunityService, ValidationError


class TestOpportunityServiceCreate:
    """Tests for create_opportunity method."""
    
    def test_create_opportunity_with_required_fields(self, db_session):
        """Test creating an opportunity with all required fields."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        opportunity = service.create_opportunity(
            title="Summer Hackathon 2024",
            description="A 48-hour coding competition for students",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/apply"
        )
        
        assert opportunity["id"] is not None
        assert opportunity["title"] == "Summer Hackathon 2024"
        assert opportunity["description"] == "A 48-hour coding competition for students"
        assert opportunity["type"] == "hackathon"
        assert opportunity["application_link"] == "https://example.com/apply"
        assert opportunity["status"] == "active"
        assert opportunity["tags"] == []
        assert opportunity["required_skills"] == []
        assert opportunity["eligibility"] is None
    
    def test_create_opportunity_with_optional_fields(self, db_session):
        """Test creating an opportunity with optional fields."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        opportunity = service.create_opportunity(
            title="Tech Scholarship",
            description="Scholarship for underrepresented students",
            opportunity_type="scholarship",
            deadline=deadline,
            application_link="https://example.com/scholarship",
            tags=["technology", "diversity"],
            required_skills=["python", "javascript"],
            eligibility="undergraduate"
        )
        
        assert opportunity["tags"] == ["technology", "diversity"]
        assert opportunity["required_skills"] == ["python", "javascript"]
        assert opportunity["eligibility"] == "undergraduate"
    
    def test_create_opportunity_missing_title(self, db_session):
        """Test that creating opportunity without title raises ValidationError."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        with pytest.raises(ValidationError, match="title is required"):
            service.create_opportunity(
                title="",
                description="Description",
                opportunity_type="hackathon",
                deadline=deadline,
                application_link="https://example.com/apply"
            )
    
    def test_create_opportunity_missing_description(self, db_session):
        """Test that creating opportunity without description raises ValidationError."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        with pytest.raises(ValidationError, match="description is required"):
            service.create_opportunity(
                title="Title",
                description="",
                opportunity_type="hackathon",
                deadline=deadline,
                application_link="https://example.com/apply"
            )
    
    def test_create_opportunity_missing_application_link(self, db_session):
        """Test that creating opportunity without application_link raises ValidationError."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        with pytest.raises(ValidationError, match="application_link is required"):
            service.create_opportunity(
                title="Title",
                description="Description",
                opportunity_type="hackathon",
                deadline=deadline,
                application_link=""
            )
    
    def test_create_opportunity_invalid_url(self, db_session):
        """Test that creating opportunity with invalid URL raises ValidationError."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        with pytest.raises(ValidationError, match="must be a valid URL"):
            service.create_opportunity(
                title="Title",
                description="Description",
                opportunity_type="hackathon",
                deadline=deadline,
                application_link="not-a-url"
            )
    
    def test_create_opportunity_invalid_type(self, db_session):
        """Test that creating opportunity with invalid type raises ValidationError."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        with pytest.raises(ValidationError, match="type must be one of"):
            service.create_opportunity(
                title="Title",
                description="Description",
                opportunity_type="invalid_type",
                deadline=deadline,
                application_link="https://example.com/apply"
            )
    
    def test_create_opportunity_unique_ids(self, db_session):
        """Test that each created opportunity gets a unique ID."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        
        opp1 = service.create_opportunity(
            title="Opportunity 1",
            description="First opportunity",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/1"
        )
        
        opp2 = service.create_opportunity(
            title="Opportunity 2",
            description="Second opportunity",
            opportunity_type="scholarship",
            deadline=deadline,
            application_link="https://example.com/2"
        )
        
        assert opp1["id"] != opp2["id"]


class TestOpportunityServiceRead:
    """Tests for get_opportunity method."""
    
    def test_get_existing_opportunity(self, db_session):
        """Test retrieving an existing opportunity."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        created = service.create_opportunity(
            title="Test Opportunity",
            description="Test description",
            opportunity_type="internship",
            deadline=deadline,
            application_link="https://example.com/apply"
        )
        
        retrieved = service.get_opportunity(created["id"])
        
        assert retrieved is not None
        assert retrieved["id"] == created["id"]
        assert retrieved["title"] == "Test Opportunity"
        assert retrieved["type"] == "internship"
    
    def test_get_nonexistent_opportunity(self, db_session):
        """Test retrieving a non-existent opportunity returns None."""
        service = OpportunityService(db_session)
        
        result = service.get_opportunity("nonexistent-id")
        
        assert result is None


class TestOpportunityServiceUpdate:
    """Tests for update_opportunity method."""
    
    def test_update_opportunity_title(self, db_session):
        """Test updating opportunity title."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        created = service.create_opportunity(
            title="Original Title",
            description="Description",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/apply"
        )
        
        updated = service.update_opportunity(
            created["id"],
            title="Updated Title"
        )
        
        assert updated["title"] == "Updated Title"
        assert updated["description"] == "Description"  # Unchanged
    
    def test_update_opportunity_multiple_fields(self, db_session):
        """Test updating multiple opportunity fields."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        created = service.create_opportunity(
            title="Original",
            description="Original description",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/apply"
        )
        
        new_deadline = datetime.utcnow() + timedelta(days=60)
        updated = service.update_opportunity(
            created["id"],
            title="Updated",
            description="Updated description",
            deadline=new_deadline,
            tags=["new", "tags"]
        )
        
        assert updated["title"] == "Updated"
        assert updated["description"] == "Updated description"
        assert updated["tags"] == ["new", "tags"]
    
    def test_update_nonexistent_opportunity(self, db_session):
        """Test updating a non-existent opportunity returns None."""
        service = OpportunityService(db_session)
        
        result = service.update_opportunity(
            "nonexistent-id",
            title="New Title"
        )
        
        assert result is None
    
    def test_update_opportunity_invalid_data(self, db_session):
        """Test updating with invalid data raises ValidationError."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        created = service.create_opportunity(
            title="Original",
            description="Description",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/apply"
        )
        
        with pytest.raises(ValidationError, match="title is required"):
            service.update_opportunity(
                created["id"],
                title=""
            )


class TestOpportunityServiceSearch:
    """Tests for search_opportunities method."""
    
    def test_search_all_opportunities(self, db_session):
        """Test searching without filters returns all active opportunities."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        
        service.create_opportunity(
            title="Hackathon 1",
            description="First hackathon",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/1"
        )
        
        service.create_opportunity(
            title="Scholarship 1",
            description="First scholarship",
            opportunity_type="scholarship",
            deadline=deadline,
            application_link="https://example.com/2"
        )
        
        results = service.search_opportunities()
        
        assert len(results) == 2
    
    def test_search_by_term_in_title(self, db_session):
        """Test searching by term in title."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        
        service.create_opportunity(
            title="Python Hackathon",
            description="Coding competition",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/1"
        )
        
        service.create_opportunity(
            title="Java Workshop",
            description="Learning event",
            opportunity_type="skill_program",
            deadline=deadline,
            application_link="https://example.com/2"
        )
        
        results = service.search_opportunities(search_term="Python")
        
        assert len(results) == 1
        assert results[0]["title"] == "Python Hackathon"
    
    def test_search_by_term_in_description(self, db_session):
        """Test searching by term in description."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        
        service.create_opportunity(
            title="Event 1",
            description="Machine learning competition",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/1"
        )
        
        service.create_opportunity(
            title="Event 2",
            description="Web development workshop",
            opportunity_type="skill_program",
            deadline=deadline,
            application_link="https://example.com/2"
        )
        
        results = service.search_opportunities(search_term="machine learning")
        
        assert len(results) == 1
        assert results[0]["title"] == "Event 1"
    
    def test_search_by_type(self, db_session):
        """Test filtering by opportunity type."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        
        service.create_opportunity(
            title="Hackathon 1",
            description="Description",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/1"
        )
        
        service.create_opportunity(
            title="Scholarship 1",
            description="Description",
            opportunity_type="scholarship",
            deadline=deadline,
            application_link="https://example.com/2"
        )
        
        service.create_opportunity(
            title="Internship 1",
            description="Description",
            opportunity_type="internship",
            deadline=deadline,
            application_link="https://example.com/3"
        )
        
        results = service.search_opportunities(opportunity_types=["hackathon", "scholarship"])
        
        assert len(results) == 2
        assert all(r["type"] in ["hackathon", "scholarship"] for r in results)
    
    def test_search_by_deadline_range(self, db_session):
        """Test filtering by deadline range."""
        service = OpportunityService(db_session)
        
        now = datetime.utcnow()
        
        service.create_opportunity(
            title="Soon",
            description="Description",
            opportunity_type="hackathon",
            deadline=now + timedelta(days=5),
            application_link="https://example.com/1"
        )
        
        service.create_opportunity(
            title="Later",
            description="Description",
            opportunity_type="hackathon",
            deadline=now + timedelta(days=60),
            application_link="https://example.com/2"
        )
        
        results = service.search_opportunities(
            deadline_start=now,
            deadline_end=now + timedelta(days=30)
        )
        
        assert len(results) == 1
        assert results[0]["title"] == "Soon"
    
    def test_search_excludes_archived(self, db_session):
        """Test that search excludes archived opportunities by default."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        
        # Create active opportunity
        service.create_opportunity(
            title="Active",
            description="Description",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/1"
        )
        
        # Create and archive opportunity
        archived = service.create_opportunity(
            title="Archived",
            description="Description",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/2"
        )
        service.update_opportunity(archived["id"], title="Archived")
        # Manually archive it
        from models import User, Profile, Opportunity, TrackedOpportunity, ParticipationHistory, Reminder


class TestOpportunityServiceArchival:
    """Tests for archive_expired_opportunities method."""
    
    def test_archive_expired_opportunities(self, db_session):
        """Test archiving opportunities with past deadlines."""
        service = OpportunityService(db_session)
        
        now = datetime.utcnow()
        
        # Create expired opportunity
        service.create_opportunity(
            title="Expired",
            description="Description",
            opportunity_type="hackathon",
            deadline=now - timedelta(days=1),
            application_link="https://example.com/1"
        )
        
        # Create active opportunity
        service.create_opportunity(
            title="Active",
            description="Description",
            opportunity_type="hackathon",
            deadline=now + timedelta(days=30),
            application_link="https://example.com/2"
        )
        
        count = service.archive_expired_opportunities()
        
        assert count == 1
        
        # Verify expired is archived
        results = service.search_opportunities()
        assert len(results) == 1
        assert results[0]["title"] == "Active"
    
    def test_archive_no_expired_opportunities(self, db_session):
        """Test archiving when no opportunities are expired."""
        service = OpportunityService(db_session)
        
        deadline = datetime.utcnow() + timedelta(days=30)
        
        service.create_opportunity(
            title="Active",
            description="Description",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com/1"
        )
        
        count = service.archive_expired_opportunities()
        
        assert count == 0
    
    def test_archive_multiple_expired_opportunities(self, db_session):
        """Test archiving multiple expired opportunities."""
        service = OpportunityService(db_session)
        
        now = datetime.utcnow()
        
        for i in range(3):
            service.create_opportunity(
                title=f"Expired {i}",
                description="Description",
                opportunity_type="hackathon",
                deadline=now - timedelta(days=i+1),
                application_link=f"https://example.com/{i}"
            )
        
        count = service.archive_expired_opportunities()
        
        assert count == 3
