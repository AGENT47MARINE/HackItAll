"""Tests for recommendation service and scoring algorithm."""
import json
import pytest
from datetime import datetime, timedelta
from hypothesis import given, strategies as st

from models.user import User, Profile
from models.opportunity import Opportunity
from services.recommendation_service import RecommendationEngine


class TestRecommendationScoringAlgorithm:
    """Unit tests for the recommendation scoring algorithm."""
    
    def test_perfect_match_scenario(self, db_session):
        """Test scoring when user perfectly matches opportunity."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "machine learning", "ai"]),
            skills=json.dumps(["python", "tensorflow", "pytorch"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity that matches perfectly
        opportunity = Opportunity(
            title="AI Hackathon",
            description="Build AI solutions",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["python", "machine learning", "ai"]),
            required_skills=json.dumps(["python", "tensorflow", "pytorch"]),
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)
        
        # Perfect match: all interests match (1.0), all skills match (1.0), education matches (1.0), no history (0.0)
        # Score = 0.4*1.0 + 0.3*1.0 + 0.2*1.0 + 0.1*0.0 = 0.9
        assert score == pytest.approx(0.9, abs=0.01)
    
    def test_no_match_scenario(self, db_session):
        """Test scoring when user has no match with opportunity."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["biology", "chemistry"]),
            skills=json.dumps(["lab work", "research"]),
            education_level="graduate"
        )
        db_session.add(profile)
        
        # Create opportunity with no overlap
        opportunity = Opportunity(
            title="Web Dev Internship",
            description="Build web applications",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["javascript", "react", "nodejs"]),
            required_skills=json.dumps(["javascript", "html", "css"]),
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)
        
        # No match: no interests match (0.0), no skills match (0.0), education doesn't match (0.0), no history (0.0)
        # Score = 0.4*0.0 + 0.3*0.0 + 0.2*0.0 + 0.1*0.0 = 0.0
        assert score == pytest.approx(0.0, abs=0.01)
    
    def test_partial_match_scenario(self, db_session):
        """Test scoring with partial matches."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "data science", "web development"]),
            skills=json.dumps(["python", "sql"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity with partial overlap
        opportunity = Opportunity(
            title="Data Science Internship",
            description="Work with data",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["python", "data science"]),  # 2 out of 3 interests match
            required_skills=json.dumps(["python", "sql", "pandas"]),  # 2 out of 3 skills match
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)
        
        # Partial match: 2/3 interests match (0.667), 2/3 skills match (0.667), education matches (1.0), no history (0.0)
        # Score = 0.4*0.667 + 0.3*0.667 + 0.2*1.0 + 0.1*0.0 = 0.267 + 0.200 + 0.200 = 0.667
        assert score == pytest.approx(0.667, abs=0.01)
    
    def test_no_required_skills(self, db_session):
        """Test scoring when opportunity has no required skills."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["writing", "journalism"]),
            skills=json.dumps([]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity with no required skills
        opportunity = Opportunity(
            title="Writing Scholarship",
            description="For aspiring writers",
            type="scholarship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["writing", "journalism"]),
            required_skills=json.dumps([]),  # No skills required
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)
        
        # All interests match (1.0), no skills required so full score (1.0), education matches (1.0), no history (0.0)
        # Score = 0.4*1.0 + 0.3*1.0 + 0.2*1.0 + 0.1*0.0 = 0.9
        assert score == pytest.approx(0.9, abs=0.01)
    
    def test_no_education_requirement(self, db_session):
        """Test scoring when opportunity has no education requirement."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps(["python"]),
            education_level="high_school"
        )
        db_session.add(profile)
        
        # Create opportunity with no education requirement
        opportunity = Opportunity(
            title="Beginner Hackathon",
            description="Open to all",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps(["python"]),
            eligibility=None  # No education requirement
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)
        
        # All interests match (1.0), all skills match (1.0), no education requirement so eligible (1.0), no history (0.0)
        # Score = 0.4*1.0 + 0.3*1.0 + 0.2*1.0 + 0.1*0.0 = 0.9
        assert score == pytest.approx(0.9, abs=0.01)
    
    def test_history_boost_with_successful_participation(self, db_session):
        """Test scoring with successful participation history."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity
        opportunity = Opportunity(
            title="Hackathon",
            description="Coding competition",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Participation history with successful hackathon completions
        participation_history = [
            {"opportunity_type": "hackathon", "status": "completed"},
            {"opportunity_type": "hackathon", "status": "completed"},
            {"opportunity_type": "scholarship", "status": "applied"}
        ]
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity, participation_history)
        
        # All interests match (1.0), all skills match (1.0), education matches (1.0), history boost (2/2 = 1.0)
        # Score = 0.4*1.0 + 0.3*1.0 + 0.2*1.0 + 0.1*1.0 = 1.0
        assert score == pytest.approx(1.0, abs=0.01)
    
    def test_history_boost_with_mixed_participation(self, db_session):
        """Test scoring with mixed participation history."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity
        opportunity = Opportunity(
            title="Internship",
            description="Software internship",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Participation history with mixed results
        participation_history = [
            {"opportunity_type": "internship", "status": "completed"},
            {"opportunity_type": "internship", "status": "applied"},
            {"opportunity_type": "internship", "status": "rejected"}
        ]
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity, participation_history)
        
        # All interests match (1.0), all skills match (1.0), education matches (1.0), history boost (1/3 = 0.333)
        # Score = 0.4*1.0 + 0.3*1.0 + 0.2*1.0 + 0.1*0.333 = 0.933
        assert score == pytest.approx(0.933, abs=0.01)
    
    def test_case_insensitive_matching(self, db_session):
        """Test that matching is case-insensitive."""
        # Create user profile with mixed case
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["Python", "Machine Learning"]),
            skills=json.dumps(["PYTHON", "TensorFlow"]),
            education_level="Undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity with different case
        opportunity = Opportunity(
            title="AI Project",
            description="AI development",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["python", "machine learning"]),
            required_skills=json.dumps(["python", "tensorflow"]),
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)
        
        # Should match despite case differences
        # All interests match (1.0), all skills match (1.0), education matches (1.0), no history (0.0)
        # Score = 0.4*1.0 + 0.3*1.0 + 0.2*1.0 + 0.1*0.0 = 0.9
        assert score == pytest.approx(0.9, abs=0.01)
    
    def test_empty_user_interests(self, db_session):
        """Test scoring when user has no interests."""
        # Create user profile with no interests
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps([]),
            skills=json.dumps(["python"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity
        opportunity = Opportunity(
            title="Hackathon",
            description="Coding event",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["coding", "python"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)
        
        # No interests (0.0), all skills match (1.0), education matches (1.0), no history (0.0)
        # Score = 0.4*0.0 + 0.3*1.0 + 0.2*1.0 + 0.1*0.0 = 0.5
        assert score == pytest.approx(0.5, abs=0.01)
    
    def test_empty_user_skills(self, db_session):
        """Test scoring when user has no skills but opportunity requires skills."""
        # Create user profile with no skills
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps([]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity that requires skills
        opportunity = Opportunity(
            title="Advanced Hackathon",
            description="For experienced developers",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["coding"]),
            required_skills=json.dumps(["python", "java", "c++"]),
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)
        
        # All interests match (1.0), no skills but required (0.0), education matches (1.0), no history (0.0)
        # Score = 0.4*1.0 + 0.3*0.0 + 0.2*1.0 + 0.1*0.0 = 0.6
        assert score == pytest.approx(0.6, abs=0.01)
    
    def test_scoring_formula_weights(self, db_session):
        """Test that scoring formula applies correct weights."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["test"]),
            skills=json.dumps(["test"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity
        opportunity = Opportunity(
            title="Test Opportunity",
            description="Test",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["test"]),
            required_skills=json.dumps(["test"]),
            eligibility="undergraduate"
        )
        db_session.add(opportunity)
        db_session.commit()
        
        # Calculate score
        engine = RecommendationEngine(db_session)
        score = engine.calculate_relevance_score(profile, opportunity)
        
        # Verify formula: 0.4*1.0 + 0.3*1.0 + 0.2*1.0 + 0.1*0.0 = 0.9
        expected_score = (0.4 * 1.0) + (0.3 * 1.0) + (0.2 * 1.0) + (0.1 * 0.0)
        assert score == pytest.approx(expected_score, abs=0.01)
        assert score == pytest.approx(0.9, abs=0.01)


class TestGenerateRecommendations:
    """Unit tests for the generate_recommendations method."""
    
    def test_generate_recommendations_basic(self, db_session):
        """Test basic recommendation generation."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "data science"]),
            skills=json.dumps(["python", "sql"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create multiple opportunities with different relevance
        opp1 = Opportunity(
            title="Python Data Science Internship",
            description="Work with data",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply1",
            tags=json.dumps(["python", "data science"]),
            required_skills=json.dumps(["python", "sql"]),
            eligibility="undergraduate",
            status="active"
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
            status="active"
        )
        
        opp3 = Opportunity(
            title="Python Workshop",
            description="Learn Python",
            type="skill_program",
            deadline=datetime.utcnow() + timedelta(days=15),
            application_link="https://example.com/apply3",
            tags=json.dumps(["python"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate",
            status="active"
        )
        
        db_session.add_all([opp1, opp2, opp3])
        db_session.commit()
        
        # Generate recommendations
        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)
        
        # Should return all 3 opportunities
        assert len(recommendations) == 3
        
        # Should be sorted by score descending
        scores = [score for _, score in recommendations]
        assert scores == sorted(scores, reverse=True)
        
        # First recommendation should be the best match (opp1)
        assert recommendations[0][0].id == opp1.id
    
    def test_generate_recommendations_with_limit(self, db_session):
        """Test recommendation generation with limit."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["coding"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create 5 opportunities
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
                status="active"
            )
            db_session.add(opp)
        
        db_session.commit()
        
        # Generate recommendations with limit of 3
        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=3)
        
        # Should return only 3 opportunities
        assert len(recommendations) == 3
    
    def test_generate_recommendations_excludes_archived(self, db_session):
        """Test that archived opportunities are excluded from recommendations."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create active opportunity
        opp1 = Opportunity(
            title="Active Opportunity",
            description="Active",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply1",
            tags=json.dumps(["python"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate",
            status="active"
        )
        
        # Create archived opportunity
        opp2 = Opportunity(
            title="Archived Opportunity",
            description="Archived",
            type="hackathon",
            deadline=datetime.utcnow() - timedelta(days=1),
            application_link="https://example.com/apply2",
            tags=json.dumps(["python"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate",
            status="archived"
        )
        
        db_session.add_all([opp1, opp2])
        db_session.commit()
        
        # Generate recommendations
        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)
        
        # Should return only the active opportunity
        assert len(recommendations) == 1
        assert recommendations[0][0].id == opp1.id
    
    def test_generate_recommendations_empty_profile(self, db_session):
        """Test recommendation generation for non-existent user."""
        # Generate recommendations for non-existent user
        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations("non-existent-id", limit=10)
        
        # Should return empty list
        assert recommendations == []
    
    def test_generate_recommendations_no_opportunities(self, db_session):
        """Test recommendation generation when no opportunities exist."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        db_session.commit()
        
        # Generate recommendations
        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)
        
        # Should return empty list
        assert recommendations == []
    
    def test_generate_recommendations_ranking_order(self, db_session):
        """Test that recommendations are properly ranked by relevance score."""
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "machine learning", "ai"]),
            skills=json.dumps(["python", "tensorflow"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunities with different match levels
        # High match: all interests and skills match
        opp_high = Opportunity(
            title="Perfect Match",
            description="Perfect match opportunity",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/high",
            tags=json.dumps(["python", "machine learning", "ai"]),
            required_skills=json.dumps(["python", "tensorflow"]),
            eligibility="undergraduate",
            status="active"
        )
        
        # Medium match: some interests and skills match
        opp_medium = Opportunity(
            title="Medium Match",
            description="Medium match opportunity",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=25),
            application_link="https://example.com/medium",
            tags=json.dumps(["python", "web"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate",
            status="active"
        )
        
        # Low match: minimal overlap
        opp_low = Opportunity(
            title="Low Match",
            description="Low match opportunity",
            type="scholarship",
            deadline=datetime.utcnow() + timedelta(days=20),
            application_link="https://example.com/low",
            tags=json.dumps(["biology", "chemistry"]),
            required_skills=json.dumps(["lab work"]),
            eligibility="undergraduate",
            status="active"
        )
        
        db_session.add_all([opp_low, opp_medium, opp_high])  # Add in random order
        db_session.commit()
        
        # Generate recommendations
        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)
        
        # Should return all 3 opportunities
        assert len(recommendations) == 3
        
        # Should be ranked: high, medium, low
        assert recommendations[0][0].id == opp_high.id
        assert recommendations[1][0].id == opp_medium.id
        assert recommendations[2][0].id == opp_low.id
        
        # Verify scores are in descending order
        assert recommendations[0][1] > recommendations[1][1]
        assert recommendations[1][1] > recommendations[2][1]
    
    def test_generate_recommendations_with_caching(self, db_session):
        """Test that caching works correctly."""
        # Create a mock cache client
        class MockCache:
            def __init__(self):
                self.storage = {}
            
            def get(self, key):
                return self.storage.get(key)
            
            def setex(self, key, ttl, value):
                self.storage[key] = value
        
        cache = MockCache()
        
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        
        # Create opportunity
        opp = Opportunity(
            title="Test Opportunity",
            description="Test",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/apply",
            tags=json.dumps(["python"]),
            required_skills=json.dumps(["python"]),
            eligibility="undergraduate",
            status="active"
        )
        db_session.add(opp)
        db_session.commit()
        
        # Generate recommendations (should cache)
        engine = RecommendationEngine(db_session, cache_client=cache)
        recommendations1 = engine.generate_recommendations(user.id, limit=10)
        
        # Verify cache was populated
        cache_key = f"recommendations:{user.id}:10"
        assert cache_key in cache.storage
        
        # Generate recommendations again (should use cache)
        recommendations2 = engine.generate_recommendations(user.id, limit=10)
        
        # Results should be the same
        assert len(recommendations1) == len(recommendations2)
        assert recommendations1[0][0].id == recommendations2[0][0].id
    
    def test_generate_recommendations_cache_ttl(self, db_session):
        """Test that cache TTL is set correctly."""
        # Create a mock cache client that tracks TTL
        class MockCache:
            def __init__(self):
                self.storage = {}
                self.ttls = {}
            
            def get(self, key):
                return self.storage.get(key)
            
            def setex(self, key, ttl, value):
                self.storage[key] = value
                self.ttls[key] = ttl
        
        cache = MockCache()
        
        # Create user profile
        user = User(email="test@example.com", password_hash="hashed")
        db_session.add(user)
        db_session.flush()
        
        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate"
        )
        db_session.add(profile)
        db_session.commit()
        
        # Generate recommendations
        engine = RecommendationEngine(db_session, cache_client=cache)
        engine.generate_recommendations(user.id, limit=10)
        
        # Verify TTL is 1 hour (3600 seconds)
        cache_key = f"recommendations:{user.id}:10"
        assert cache.ttls[cache_key] == 3600
