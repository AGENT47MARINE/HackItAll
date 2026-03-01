"""Tests for recommendation service and scoring algorithm.

Updated to match the new point-based scoring system:
- Interest matching: +10 per match
- Online/Hybrid bonus: +5
- Urgency bonus: +5 (deadline within 14 days)
- Hard eligibility: -1000 (incompatible education level)
"""
import json
import pytest
from datetime import datetime, timedelta

from models.user import User, Profile
from models.opportunity import Opportunity
from services.recommendation_service import RecommendationEngine


class TestRecommendationScoringAlgorithm:
    """Unit tests for the point-based recommendation scoring algorithm."""

    def test_perfect_match_scenario(self, db_session):
        """Test scoring when user interests perfectly match opportunity tags."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "machine learning", "ai"]),
            skills=json.dumps(["python", "tensorflow", "pytorch"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        opportunity = Opportunity(
            title="AI Hackathon",
            description="Build AI solutions",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["python", "machine learning", "ai"]),
            required_skills=json.dumps(["python", "tensorflow"]),
            eligibility="undergraduate",
            location_type="Online",
        )
        db_session.add(opportunity)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)

        # 3 interest matches × 10 = 30, Online bonus = +5 → 35
        assert score >= 30.0

    def test_no_match_scenario(self, db_session):
        """Test scoring when user has zero overlap with opportunity tags."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["biology", "chemistry"]),
            skills=json.dumps(["lab work", "research"]),
            education_level="graduate",
        )
        db_session.add(profile)

        opportunity = Opportunity(
            title="Web Dev Internship",
            description="Build web applications",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["javascript", "react", "nodejs"]),
            required_skills=json.dumps(["javascript", "html"]),
            eligibility="undergraduate",
            location_type="In-Person",
        )
        db_session.add(opportunity)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)

        # No interest overlap, not online, no urgency → 0.0
        assert score == 0.0

    def test_partial_match_scenario(self, db_session):
        """Test scoring with partial interest matching."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "data science", "web development"]),
            skills=json.dumps(["python", "sql"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        opportunity = Opportunity(
            title="Data Science Internship",
            description="Work with data",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["python", "data science"]),
            required_skills=json.dumps(["python", "sql", "pandas"]),
            eligibility="undergraduate",
            location_type="In-Person",
        )
        db_session.add(opportunity)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)

        # 2 interest matches × 10 = 20.0
        assert score == 20.0

    def test_online_format_bonus(self, db_session):
        """Test that Online/Hybrid events get a +5 bonus."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        opp_online = Opportunity(
            title="Online Hackathon",
            description="Virtual event",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/online",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps([]),
            eligibility="undergraduate",
            location_type="Online",
        )

        opp_inperson = Opportunity(
            title="In-Person Hackathon",
            description="Physical event",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/inperson",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps([]),
            eligibility="undergraduate",
            location_type="In-Person",
        )
        db_session.add_all([opp_online, opp_inperson])
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score_online = engine.calculate_relevance_score(profile, opp_online)
        score_inperson = engine.calculate_relevance_score(profile, opp_inperson)

        # Online should get +5 bonus
        assert score_online == score_inperson + 5.0

    def test_urgency_bonus(self, db_session):
        """Test that events with deadlines within 14 days get +5."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps([]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        opp_urgent = Opportunity(
            title="Urgent Hackathon",
            description="Deadline soon",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=5),
            application_link="https://example.com/urgent",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps([]),
            location_type="In-Person",
        )

        opp_later = Opportunity(
            title="Later Hackathon",
            description="Deadline far",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/later",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps([]),
            location_type="In-Person",
        )
        db_session.add_all([opp_urgent, opp_later])
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score_urgent = engine.calculate_relevance_score(profile, opp_urgent)
        score_later = engine.calculate_relevance_score(profile, opp_later)

        # Urgent should get +5 bonus
        assert score_urgent == score_later + 5.0

    def test_expired_events_excluded(self, db_session):
        """Test that expired events return -1000."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps([]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        opp_expired = Opportunity(
            title="Expired Hackathon",
            description="Already done",
            type="hackathon",
            deadline=datetime.utcnow() - timedelta(days=5),
            application_link="https://example.com/expired",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps([]),
            location_type="Online",
        )
        db_session.add(opp_expired)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opp_expired)

        assert score == -1000.0

    def test_eligibility_hard_filter_high_school(self, db_session):
        """Test that High School-only events exclude B.Tech students."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps([]),
            education_level="B.Tech 3rd Year",
        )
        db_session.add(profile)

        opp = Opportunity(
            title="High School Hack",
            description="For high schoolers only",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/hs",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps([]),
            eligibility="High School",
            location_type="In-Person",
        )
        db_session.add(opp)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opp)

        assert score == -1000.0

    def test_eligibility_hard_filter_graduate(self, db_session):
        """Test that Graduate-only events exclude B.Tech students."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["research"]),
            skills=json.dumps([]),
            education_level="B.Tech 2nd Year",
        )
        db_session.add(profile)

        opp = Opportunity(
            title="Graduate Symposium",
            description="Graduate-level research",
            type="skill_program",
            deadline=datetime.utcnow() + timedelta(days=20),
            application_link="https://example.com/grad",
            tags=json.dumps(["research"]),
            required_skills=json.dumps([]),
            eligibility="Graduate",
            location_type="Online",
        )
        db_session.add(opp)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opp)

        assert score == -1000.0

    def test_no_eligibility_requirement(self, db_session):
        """Test that events with no eligibility requirement accept everyone."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps(["python"]),
            education_level="high_school",
        )
        db_session.add(profile)

        opportunity = Opportunity(
            title="Beginner Hackathon",
            description="Open to all",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps(["python"]),
            eligibility=None,
            location_type="In-Person",
        )
        db_session.add(opportunity)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)

        # 1 interest match × 10 = 10
        assert score >= 10.0

    def test_case_insensitive_matching(self, db_session):
        """Test that interest matching is case-insensitive."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["Python", "Machine Learning"]),
            skills=json.dumps(["PYTHON", "TensorFlow"]),
            education_level="Undergraduate",
        )
        db_session.add(profile)

        opportunity = Opportunity(
            title="AI Project",
            description="AI development",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["python", "machine learning"]),
            required_skills=json.dumps(["python", "tensorflow"]),
            location_type="In-Person",
        )
        db_session.add(opportunity)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)

        # 2 interest matches × 10 = 20 (case insensitive)
        assert score >= 20.0

    def test_empty_user_interests(self, db_session):
        """Test scoring when user has no interests."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps([]),
            skills=json.dumps(["python"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        opportunity = Opportunity(
            title="Hackathon",
            description="Coding event",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["coding", "python"]),
            required_skills=json.dumps(["python"]),
            location_type="Online",
        )
        db_session.add(opportunity)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)

        # No interest matches → 0 interest points, +5 online bonus
        assert score == 5.0

    def test_combined_scoring(self, db_session):
        """Test the full scoring formula with all bonuses active."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["ai", "web dev"]),
            skills=json.dumps([]),
            education_level="B.Tech",
        )
        db_session.add(profile)

        opportunity = Opportunity(
            title="AI+Web Hackathon",
            description="Build AI web apps",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=5),  # Urgent
            application_link="https://example.com/apply",
            tags=json.dumps(["ai", "web dev", "cloud"]),
            required_skills=json.dumps([]),
            eligibility="B.Tech",
            location_type="Online",  # Online bonus
        )
        db_session.add(opportunity)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)

        # 2 interest matches × 10 = 20, Online = +5, Urgency = +5 → 30
        assert score == 30.0


class TestGenerateRecommendations:
    """Unit tests for the generate_recommendations method."""

    def test_generate_recommendations_basic(self, db_session):
        """Test basic recommendation generation returns sorted results."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "data science"]),
            skills=json.dumps(["python", "sql"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        opp1 = Opportunity(
            title="Python Data Science Internship",
            description="Work with data",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply1",
            tags=json.dumps(["python", "data science"]),
            required_skills=json.dumps(["python", "sql"]),
            eligibility="undergraduate",
            location_type="Online",
            status="active",
        )

        opp2 = Opportunity(
            title="Web Development Hackathon",
            description="Build web apps",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=20),
            application_link="https://example.com/apply2",
            tags=json.dumps(["javascript", "web"]),
            required_skills=json.dumps(["javascript", "html"]),
            eligibility="undergraduate",
            location_type="In-Person",
            status="active",
        )

        opp3 = Opportunity(
            title="Python Workshop",
            description="Learn Python",
            type="skill_program",
            deadline=datetime.utcnow() + timedelta(days=5),  # Urgent
            application_link="https://example.com/apply3",
            tags=json.dumps(["python"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate",
            location_type="In-Person",
            status="active",
        )

        db_session.add_all([opp1, opp2, opp3])
        db_session.commit()

        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)

        # Should return all 3
        assert len(recommendations) == 3

        # Should be sorted by score descending
        scores = [score for _, score in recommendations]
        assert scores == sorted(scores, reverse=True)

        # opp1 should be first: 2 matches × 10 = 20 + Online 5 = 25
        # opp3 should be second: 1 match × 10 = 10 + Urgency 5 = 15
        # opp2 should be last: 0 matches = 0
        assert recommendations[0][0].id == opp1.id
        assert recommendations[2][0].id == opp2.id

    def test_generate_recommendations_with_limit(self, db_session):
        """Test recommendation generation respects limit."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        for i in range(5):
            opp = Opportunity(
                title=f"Opportunity {i}",
                description="Test opportunity",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/apply{i}",
                tags=json.dumps(["coding"]),
                required_skills=json.dumps(["python"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active",
            )
            db_session.add(opp)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=3)

        assert len(recommendations) == 3

    def test_generate_recommendations_excludes_archived(self, db_session):
        """Test that archived opportunities are not returned."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        opp1 = Opportunity(
            title="Active Opportunity",
            description="Active",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply1",
            tags=json.dumps(["python"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate",
            location_type="Online",
            status="active",
        )

        opp2 = Opportunity(
            title="Archived Opportunity",
            description="Archived",
            type="hackathon",
            deadline=datetime.utcnow() - timedelta(days=1),
            application_link="https://example.com/apply2",
            tags=json.dumps(["python"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate",
            location_type="Online",
            status="archived",
        )

        db_session.add_all([opp1, opp2])
        db_session.commit()

        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)

        assert len(recommendations) == 1
        assert recommendations[0][0].id == opp1.id

    def test_generate_recommendations_empty_profile(self, db_session):
        """Test that non-existent user returns empty list."""
        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations("non-existent-id", limit=10)
        assert recommendations == []

    def test_generate_recommendations_no_opportunities(self, db_session):
        """Test that empty DB returns empty list."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate",
        )
        db_session.add(profile)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)
        assert recommendations == []

    def test_generate_recommendations_ranking_order(self, db_session):
        """Test that recommendations are ranked high → medium → low."""
        user = User(email="test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "machine learning", "ai"]),
            skills=json.dumps(["python", "tensorflow"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        opp_high = Opportunity(
            title="Perfect Match",
            description="Perfect match opportunity",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=5),  # Urgent
            application_link="https://example.com/high",
            tags=json.dumps(["python", "machine learning", "ai"]),
            required_skills=json.dumps(["python", "tensorflow"]),
            eligibility="undergraduate",
            location_type="Online",
            status="active",
        )

        opp_medium = Opportunity(
            title="Medium Match",
            description="Medium match opportunity",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=25),
            application_link="https://example.com/medium",
            tags=json.dumps(["python", "web"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate",
            location_type="In-Person",
            status="active",
        )

        opp_low = Opportunity(
            title="Low Match",
            description="Low match opportunity",
            type="scholarship",
            deadline=datetime.utcnow() + timedelta(days=20),
            application_link="https://example.com/low",
            tags=json.dumps(["biology", "chemistry"]),
            required_skills=json.dumps(["lab work"]),
            eligibility="undergraduate",
            location_type="In-Person",
            status="active",
        )

        db_session.add_all([opp_low, opp_medium, opp_high])
        db_session.commit()

        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)

        assert len(recommendations) == 3

        # High: 3×10 + Online(5) + Urgency(5) = 40
        # Medium: 1×10 = 10
        # Low: 0×10 = 0
        assert recommendations[0][0].id == opp_high.id
        assert recommendations[1][0].id == opp_medium.id
        assert recommendations[2][0].id == opp_low.id

        assert recommendations[0][1] > recommendations[1][1]
        assert recommendations[1][1] > recommendations[2][1]
