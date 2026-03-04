import hypothesis.strategies as st
"""Property-based tests for OpportunityService using Hypothesis.

Feature: opportunity-access-platform
"""
import pytest
from hypothesis import HealthCheck, given, strategies as st, assume, settings
from datetime import datetime, timedelta
import json

from services.opportunity_service import OpportunityService, ValidationError
from models.opportunity import Opportunity


# Custom strategies for opportunity data
@st.composite
def valid_opportunity_type(draw):
    """Generate valid opportunity types."""
    return draw(st.sampled_from([
        'hackathon', 'scholarship', 'internship', 'skill_program'
    ]))


@st.composite
def future_deadline(draw):
    """Generate future deadlines."""
    days_ahead = draw(st.integers(min_value=1, max_value=365))
    return datetime.utcnow() + timedelta(days=days_ahead)


@st.composite
def past_deadline(draw):
    """Generate past deadlines."""
    days_ago = draw(st.integers(min_value=1, max_value=365))
    return datetime.utcnow() - timedelta(days=days_ago)


@st.composite
def valid_url(draw):
    """Generate valid URLs."""
    protocol = draw(st.sampled_from(['http', 'https']))
    domain = draw(st.text(min_size=4, max_size=20, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))))
    tld = draw(st.sampled_from(['com', 'org', 'edu', 'io', 'net']))
    path = draw(st.text(min_size=0, max_size=30, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'))))
    
    url = f"{protocol}://{domain}.{tld}"
    if path:
        url += f"/{path}"
    return url


@st.composite
def valid_tags_list(draw):
    """Generate valid tags lists."""
    return draw(st.lists(
        st.text(min_size=1, max_size=30, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])),
        min_size=0,
        max_size=10
    ))


@st.composite
def valid_skills_list(draw):
    """Generate valid skills lists."""
    return draw(st.lists(
        st.text(min_size=1, max_size=30, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])),
        min_size=0,
        max_size=10
    ))


class TestOpportunityValidation:
    """Property 21: Opportunity validation.
    
    Feature: opportunity-access-platform, Property 21: Opportunity validation
    
    Tests that opportunity data is properly validated.
    """
    
    @given(
        title=st.text(min_size=1, max_size=200, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""),
        description=st.text(min_size=1, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""),
        opportunity_type=valid_opportunity_type(),
        deadline=future_deadline(),
        application_link=valid_url(),
        tags=valid_tags_list(),
        required_skills=valid_skills_list()
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_valid_opportunity_accepted(
        self, db_session, title, description, opportunity_type,
        deadline, application_link, tags, required_skills
    ):
        """Property 21: Valid opportunity data must be accepted.
        
        Feature: opportunity-access-platform, Property 21: Opportunity validation
        """
        service = OpportunityService(db_session)
        
        # Property: Valid data must create opportunity successfully
        result = service.create_opportunity(
            title=title,
            description=description,
            opportunity_type=opportunity_type,
            deadline=deadline,
            application_link=application_link,
            tags=tags,
            required_skills=required_skills
        )
        
        # Property: All fields must be present in result
        assert result is not None
        assert result["title"] == title
        assert result["description"] == description
        assert result["type"] == opportunity_type
        assert result["application_link"] == application_link
        assert result["tags"] == tags
        assert result["required_skills"] == required_skills
        assert result["status"] == "active"
    
    @given(
        title=st.one_of(st.just(""), st.just("   "), st.none()),
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_empty_title_rejected(self, db_session, title):
        """Property 21: Empty title must be rejected.
        
        Feature: opportunity-access-platform, Property 21: Opportunity validation
        """
        service = OpportunityService(db_session)
        
        # Property: Empty title must raise ValidationError
        with pytest.raises(ValidationError):
            service.create_opportunity(
                title=title if title else "",
                description="Test description",
                opportunity_type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link="https://example.com"
            )
    
    @given(
        description=st.one_of(st.just(""), st.just("   "), st.none()),
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_empty_description_rejected(self, db_session, description):
        """Property 21: Empty description must be rejected.
        
        Feature: opportunity-access-platform, Property 21: Opportunity validation
        """
        service = OpportunityService(db_session)
        
        # Property: Empty description must raise ValidationError
        with pytest.raises(ValidationError):
            service.create_opportunity(
                title="Test Opportunity",
                description=description if description else "",
                opportunity_type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link="https://example.com"
            )
    
    @given(
        application_link=st.one_of(st.just(""), st.just("   "), st.none()),
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_empty_application_link_rejected(self, db_session, application_link):
        """Property 21: Empty application link must be rejected.
        
        Feature: opportunity-access-platform, Property 21: Opportunity validation
        """
        service = OpportunityService(db_session)
        
        # Property: Empty application link must raise ValidationError
        with pytest.raises(ValidationError):
            service.create_opportunity(
                title="Test Opportunity",
                description="Test description",
                opportunity_type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=application_link if application_link else ""
            )


class TestOpportunityIdentifierUniqueness:
    """Property 22: Opportunity identifier uniqueness.
    
    Feature: opportunity-access-platform, Property 22: Opportunity identifier uniqueness
    
    Tests that opportunity IDs are unique.
    """
    
    @given(
        title1=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""),
        title2=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != "")
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_opportunity_ids_are_unique(self, db_session, title1, title2):
        """Property 22: Each opportunity must have a unique ID.
        
        Feature: opportunity-access-platform, Property 22: Opportunity identifier uniqueness
        """
        service = OpportunityService(db_session)
        
        # Create two opportunities
        opp1 = service.create_opportunity(
            title=title1,
            description="Description 1",
            opportunity_type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example1.com"
        )
        
        opp2 = service.create_opportunity(
            title=title2,
            description="Description 2",
            opportunity_type="scholarship",
            deadline=datetime.utcnow() + timedelta(days=60),
            application_link="https://example2.com"
        )
        
        # Property: IDs must be unique
        assert opp1["id"] != opp2["id"]
        
        # Property: IDs must be non-empty strings
        assert isinstance(opp1["id"], str)
        assert isinstance(opp2["id"], str)
        assert len(opp1["id"]) > 0
        assert len(opp2["id"]) > 0


class TestOpportunityUpdatePersistence:
    """Property 24: Opportunity update persistence.
    
    Feature: opportunity-access-platform, Property 24: Opportunity update persistence
    
    Tests that opportunity updates persist to database.
    """
    
    @given(
        initial_title=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""),
        updated_title=st.text(min_size=1, max_size=100, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""),
        initial_tags=valid_tags_list(),
        updated_tags=valid_tags_list()
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_opportunity_updates_persist(
        self, db_session, initial_title, updated_title,
        initial_tags, updated_tags
    ):
        """Property 24: Opportunity updates must persist to database.
        
        Feature: opportunity-access-platform, Property 24: Opportunity update persistence
        """
        service = OpportunityService(db_session)
        
        # Create opportunity
        created = service.create_opportunity(
            title=initial_title,
            description="Initial description",
            opportunity_type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com",
            tags=initial_tags
        )
        
        opportunity_id = created["id"]
        
        # Update opportunity
        updated = service.update_opportunity(
            opportunity_id=opportunity_id,
            title=updated_title,
            tags=updated_tags
        )
        
        # Property: Updated values must be returned
        assert updated is not None
        assert updated["title"] == updated_title
        assert updated["tags"] == updated_tags
        
        # Property: Updates must persist (retrieve again)
        retrieved = service.get_opportunity(opportunity_id)
        assert retrieved is not None
        assert retrieved["title"] == updated_title
        assert retrieved["tags"] == updated_tags


class TestOpportunitySearchFiltering:
    """Property 26: Search term matching.
    
    Feature: opportunity-access-platform, Property 26: Search term matching
    
    Tests that search correctly matches opportunities.
    """
    
    @given(
        search_term=st.text(min_size=3, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_search_finds_matching_opportunities(self, db_session, search_term):
        """Property 26: Search must find opportunities containing the search term.
        
        Feature: opportunity-access-platform, Property 26: Search term matching
        """
        service = OpportunityService(db_session)
        
        # Create opportunity with search term in title
        created = service.create_opportunity(
            title=f"Test {search_term} Opportunity",
            description="Test description",
            opportunity_type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com"
        )
        
        # Search for the term
        results = service.search_opportunities(search_term=search_term)
        
        # Property: Search results must include the created opportunity
        result_ids = [r["id"] for r in results]
        assert created["id"] in result_ids


class TestOpportunityEdgeCases:
    """Edge case tests for OpportunityService."""
    
    @given(
        deadline=past_deadline()
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_past_deadline_creates_active_opportunity(self, db_session, deadline):
        """Test that opportunities with past deadlines can be created (for historical data).
        
        Feature: opportunity-access-platform
        """
        service = OpportunityService(db_session)
        
        # Create opportunity with past deadline
        result = service.create_opportunity(
            title="Past Opportunity",
            description="Historical opportunity",
            opportunity_type="hackathon",
            deadline=deadline,
            application_link="https://example.com"
        )
        
        # Opportunity should be created (archival happens via scheduled job)
        assert result is not None
        assert result["status"] == "active"
    
    @given(
        tags=st.lists(st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""), min_size=0, max_size=50)
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_large_tags_list_handled(self, db_session, tags):
        """Test handling of large tags lists.
        
        Feature: opportunity-access-platform
        """
        service = OpportunityService(db_session)
        
        result = service.create_opportunity(
            title="Test Opportunity",
            description="Test description",
            opportunity_type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com",
            tags=tags
        )
        
        assert result["tags"] == tags
    
    @given(
        title=st.text(min_size=1, max_size=500, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""),
        description=st.text(min_size=1, max_size=5000, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""))
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_long_text_fields_handled(self, db_session, title, description):
        """Test handling of long text fields.
        
        Feature: opportunity-access-platform
        """
        service = OpportunityService(db_session)
        
        result = service.create_opportunity(
            title=title,
            description=description,
            opportunity_type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com"
        )
        
        assert result["title"] == title
        assert result["description"] == description
