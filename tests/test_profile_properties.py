import hypothesis.strategies as st
"""Property-based tests for ProfileService using Hypothesis.

Feature: opportunity-access-platform
"""
import pytest
from hypothesis import HealthCheck, given, strategies as st, assume, settings
from hypothesis.stateful import RuleBasedStateMachine, rule, invariant
import json

from services.profile_service import ProfileService, ValidationError
from models.user import User, Profile
import uuid


# Custom strategies for profile data
@st.composite
def valid_email(draw):
    """Generate valid email addresses using ASCII characters."""
    username = draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Ll', 'Nd'), min_codepoint=97, max_codepoint=122) | st.sampled_from('0123456789')))
    domain = draw(st.text(min_size=1, max_size=15, alphabet=st.characters(whitelist_categories=('Ll',), min_codepoint=97, max_codepoint=122)))
    tld = draw(st.sampled_from(['com', 'org', 'edu', 'net', 'io']))
    return f"{username}@{domain}.{tld}".lower()


@st.composite
def valid_education_level(draw):
    """Generate valid education levels."""
    return draw(st.sampled_from([
        'high_school', 'associate', 'bachelor', 'master', 'doctorate', 'other'
    ]))


@st.composite
def valid_interests_list(draw):
    """Generate valid interests lists."""
    return draw(st.lists(
        st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""),
        min_size=0,
        max_size=20
    ))


@st.composite
def valid_skills_list(draw):
    """Generate valid skills lists."""
    return draw(st.lists(
        st.text(min_size=1, max_size=50, alphabet=st.characters(blacklist_categories=('Cs',), blacklist_characters=['\x00'])).filter(lambda x: x.strip() != ""),
        min_size=0,
        max_size=20
    ))


@st.composite
def valid_phone(draw):
    """Generate valid phone numbers."""
    country_code = draw(st.sampled_from(['+1', '+44', '+91', '+86', '+81']))
    number = draw(st.integers(min_value=1000000000, max_value=9999999999))
    return f"{country_code}{number}"


class TestProfileCreationCompleteness:
    """Property 1: Profile creation completeness.
    
    Feature: opportunity-access-platform, Property 1: Profile creation completeness
    
    Tests that all required fields are present in created profiles.
    """
    
    @given(
        email=valid_email(),
        education_level=valid_education_level(),
        interests=valid_interests_list(),
        skills=valid_skills_list(),
        phone=st.one_of(st.none(), valid_phone()),
        notification_email=st.booleans(),
        notification_sms=st.booleans(),
        low_bandwidth_mode=st.booleans()
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_profile_creation_includes_all_fields(
        self, db_session, email, education_level, interests, skills,
        phone, notification_email, notification_sms, low_bandwidth_mode
    ):
        """Property 1: All created profiles must include all required fields.
        
        Feature: opportunity-access-platform, Property 1: Profile creation completeness
        """
        service = ProfileService(db_session)
        
        # Create profile with generated data
        user_id = str(uuid.uuid4())
        unique_email = f"{user_id}_{email}"
        result = service.create_profile(
            user_id=user_id,
            email=unique_email,
            education_level=education_level,
            interests=interests,
            skills=skills,
            phone=phone,
            notification_email=notification_email,
            notification_sms=notification_sms,
            low_bandwidth_mode=low_bandwidth_mode
        )
        
        # Property: All required fields must be present
        assert "id" in result
        assert "email" in result
        assert "phone" in result
        assert "interests" in result
        assert "skills" in result
        assert "education_level" in result
        assert "notification_email" in result
        assert "notification_sms" in result
        assert "low_bandwidth_mode" in result
        assert "created_at" in result
        assert "updated_at" in result
        assert "participation_history" in result
        assert "activity_streak" in result
        
        # Property: Field values must match input
        assert result["email"] == unique_email
        assert result["education_level"] == education_level
        assert result["interests"] == interests
        assert result["skills"] == skills
        assert result["phone"] == phone
        assert result["notification_email"] == notification_email
        assert result["notification_sms"] == notification_sms
        assert result["low_bandwidth_mode"] == low_bandwidth_mode


class TestProfileUpdatePersistence:
    """Property 2: Profile update persistence.
    
    Feature: opportunity-access-platform, Property 2: Profile update persistence
    
    Tests that profile updates are correctly persisted to the database.
    """
    
    @given(
        email=valid_email(),
        initial_interests=valid_interests_list(),
        updated_interests=valid_interests_list(),
        initial_skills=valid_skills_list(),
        updated_skills=valid_skills_list()
    )
    @settings(max_examples=100, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_profile_updates_persist(
        self, db_session, email, initial_interests, updated_interests,
        initial_skills, updated_skills
    ):
        """Property 2: Profile updates must persist to database.
        
        Feature: opportunity-access-platform, Property 2: Profile update persistence
        """
        service = ProfileService(db_session)
        
        # Create initial profile
        user_id = str(uuid.uuid4())
        unique_email = f"{user_id}_{email}"
        created = service.create_profile(
            user_id=user_id,
            email=unique_email,
            education_level="bachelor",
            interests=initial_interests,
            skills=initial_skills
        )
        
        user_id = created["id"]
        
        # Update profile
        updated = service.update_profile(
            user_id=user_id,
            interests=updated_interests,
            skills=updated_skills
        )
        
        # Property: Updated values must be returned
        assert updated["interests"] == updated_interests
        assert updated["skills"] == updated_skills
        
        # Property: Updates must persist (retrieve again)
        retrieved = service.get_profile(user_id)
        assert retrieved is not None
        assert retrieved["interests"] == updated_interests
        assert retrieved["skills"] == updated_skills


class TestRequiredFieldValidation:
    """Property 4: Required field validation.
    
    Feature: opportunity-access-platform, Property 4: Required field validation
    
    Tests that required fields are properly validated.
    """
    
    @given(
        email=valid_email(),
        education_level=st.one_of(st.just(""), st.just("   "), st.none())
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_empty_education_level_rejected(self, db_session, email, education_level):
        """Property 4: Empty or whitespace education_level must be rejected.
        
        Feature: opportunity-access-platform, Property 4: Required field validation
        """
        service = ProfileService(db_session)
        
        # Property: Empty/whitespace education_level must raise ValidationError
        user_id = str(uuid.uuid4())
        unique_email = f"{user_id}_{email}"
        with pytest.raises(ValidationError):
            service.create_profile(
                user_id=user_id,
                email=unique_email,
                education_level=education_level if education_level else ""
            )
    
    @given(
        invalid_email=st.one_of(
            st.just("not-an-email"),
            st.just("missing-at-sign.com"),
            st.just("@no-username.com"),
            st.just("no-domain@"),
            st.just("spaces in@email.com")
        )
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_email_rejected(self, db_session, invalid_email):
        """Property 4: Invalid email formats must be rejected.
        
        Feature: opportunity-access-platform, Property 4: Required field validation
        """
        service = ProfileService(db_session)
        
        # Property: Invalid email must raise ValidationError
        user_id = str(uuid.uuid4())
        with pytest.raises(ValidationError):
            service.create_profile(
                user_id=user_id,
                email=invalid_email,
                education_level="bachelor"
            )


class TestProfileDataTypes:
    """Tests for proper data type handling in profiles."""
    
    @given(
        interests=st.one_of(st.just("not a list"), st.integers(), st.floats()),
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_interests_type_rejected(self, db_session, interests):
        """Property: Non-list interests must be rejected.
        
        Feature: opportunity-access-platform, Property 4: Required field validation
        """
        service = ProfileService(db_session)
        
        # Property: Non-list interests must raise ValidationError
        with pytest.raises(ValidationError):
            service.create_profile(
                user_id="test-user",
                email="test@example.com",
                education_level="bachelor",
                interests=interests
            )
    
    @given(
        skills=st.one_of(st.just("not a list"), st.integers(), st.floats()),
    )
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_invalid_skills_type_rejected(self, db_session, skills):
        """Property: Non-list skills must be rejected.
        
        Feature: opportunity-access-platform, Property 4: Required field validation
        """
        service = ProfileService(db_session)
        
        # Property: Non-list skills must raise ValidationError
        with pytest.raises(ValidationError):
            service.create_profile(
                user_id="test-user",
                email="test@example.com",
                education_level="bachelor",
                skills=skills
            )


class ProfileStateMachine(RuleBasedStateMachine):
    """Stateful property testing for ProfileService.
    
    Feature: opportunity-access-platform
    
    Tests that profile operations maintain consistency across multiple operations.
    """
    
    def __init__(self):
        super().__init__()
        from sqlalchemy import create_engine
        from database import Base
        
        # Use a fresh in-memory database for each state machine execution
        engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
        Base.metadata.create_all(bind=engine)
        
        from sqlalchemy.orm import sessionmaker
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        self.db_session = SessionLocal()
        self.service = ProfileService(self.db_session)
        self.profiles = {}  # Track created profiles
    
    @rule(email=valid_email(), education_level=valid_education_level(),
          interests=valid_interests_list(), skills=valid_skills_list())
    def create_profile(self, email, education_level, interests, skills):
        """Create a new profile."""
        user_id = str(uuid.uuid4())
        unique_email = f"{user_id}_{email}"
        
        profile = self.service.create_profile(
            user_id=user_id,
            email=unique_email,
            education_level=education_level,
            interests=interests,
            skills=skills
        )
        self.profiles[user_id] = profile
    
    @rule(data=st.data(),
          new_interests=valid_interests_list(),
          new_skills=valid_skills_list())
    def update_profile(self, data, new_interests, new_skills):
        """Update an existing profile."""
        assume(len(self.profiles) > 0)
        user_id = data.draw(st.sampled_from(list(self.profiles.keys())))
        
        result = self.service.update_profile(
            user_id=user_id,
            interests=new_interests,
            skills=new_skills
        )
        
        if result:
            self.profiles[user_id] = result
    
    @invariant()
    def all_profiles_have_required_fields(self):
        """Invariant: All tracked profiles must have required fields."""
        for user_id, profile in self.profiles.items():
            assert "id" in profile
            assert "email" in profile
            assert "education_level" in profile
            assert "interests" in profile
            assert isinstance(profile["interests"], list)


# Run the state machine test
TestProfileState = ProfileStateMachine.TestCase
