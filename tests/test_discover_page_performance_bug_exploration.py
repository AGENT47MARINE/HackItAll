"""Bug condition exploration test for discover page performance and match percentage issues.

**Validates: Requirements 2.1, 2.2, 2.3, 2.4, 2.5, 2.6**

This test MUST FAIL on unfixed code - failure confirms the bugs exist.
The test encodes the expected behavior that will validate the fix when it passes after implementation.

CRITICAL: This test is designed to surface counterexamples that demonstrate:
1. Performance issues with large datasets (slow loading, inefficient queries)
2. Redis cache not being utilized properly
3. Match percentages not normalized to 0-100% range
4. Negative percentages being displayed from eligibility filters

EXPECTED OUTCOME: Test FAILS (this proves the bugs exist)
"""
import pytest
import time
import json
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
from unittest.mock import patch, MagicMock

from services.recommendation_service import RecommendationEngine
from services.opportunity_service import OpportunityService
from services.profile_service import ProfileService
from models.user import User, Profile
from models.opportunity import Opportunity


class TestDiscoverPagePerformanceBugExploration:
    """Bug condition exploration tests for discover page performance and match percentage issues."""

    def test_for_you_section_performance_with_large_dataset(self, db_session):
        """Test that For You section loads efficiently with large datasets.
        
        **Property 1: Fault Condition** - Performance Issues
        **CRITICAL**: This test MUST FAIL on unfixed code
        
        Expected behavior: For You section should load in < 2 seconds with 1000+ opportunities
        Current bug: System loads ALL opportunities and scores them in memory (inefficient)
        """
        # Create user profile
        user = User(email="performance_test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "ai", "web development"]),
            skills=json.dumps(["python", "javascript", "react"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        # Create large dataset (1000+ opportunities) to simulate real-world load
        opportunities = []
        for i in range(1200):
            opp = Opportunity(
                title=f"Opportunity {i}",
                description=f"Description for opportunity {i}",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/opp{i}",
                tags=json.dumps(["python", "ai", "web development", "data science", "blockchain"]),
                required_skills=json.dumps(["python", "javascript", "sql"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active",
            )
            opportunities.append(opp)
        
        db_session.add_all(opportunities)
        db_session.commit()

        # Test performance of For You section loading
        engine = RecommendationEngine(db_session)
        
        start_time = time.time()
        recommendations = engine.generate_recommendations(user.id, limit=10)
        end_time = time.time()
        
        load_time = end_time - start_time
        
        # EXPECTED TO FAIL: Current implementation loads all 1200 opportunities and scores them
        # This will likely take > 2 seconds, demonstrating the performance bug
        assert load_time < 2.0, f"For You section took {load_time:.2f}s to load with 1200 opportunities. Expected < 2s. This demonstrates the performance bug - system loads ALL opportunities instead of efficient filtering."
        
        # Verify we got recommendations
        assert len(recommendations) > 0, "Should return recommendations"

    def test_redis_cache_utilization_bug(self, db_session):
        """Test that Redis cache is properly utilized during repeated loads.
        
        **Property 1: Fault Condition** - Caching Issues  
        **CRITICAL**: This test MUST FAIL on unfixed code
        
        Expected behavior: Second load should be much faster due to Redis cache hit
        Current bug: Cache may not be working properly (serialization issues, wrong keys, etc.)
        """
        # Create user and opportunities
        user = User(email="cache_test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "ai"]),
            skills=json.dumps(["python", "tensorflow"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        # Create moderate dataset to test caching
        for i in range(100):
            opp = Opportunity(
                title=f"Cache Test Opportunity {i}",
                description=f"Description {i}",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/cache{i}",
                tags=json.dumps(["python", "ai", "machine learning"]),
                required_skills=json.dumps(["python", "tensorflow"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active",
            )
            db_session.add(opp)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        
        # First load - should populate cache
        start_time1 = time.time()
        recommendations1 = engine.generate_recommendations(user.id, limit=10)
        end_time1 = time.time()
        first_load_time = end_time1 - start_time1
        
        # Second load - should use cache and be much faster
        start_time2 = time.time()
        recommendations2 = engine.generate_recommendations(user.id, limit=10)
        end_time2 = time.time()
        second_load_time = end_time2 - start_time2
        
        # EXPECTED TO FAIL: Cache may not be working properly
        # Second load should be at least 50% faster if cache is working
        cache_speedup_ratio = first_load_time / second_load_time if second_load_time > 0 else 1
        
        assert cache_speedup_ratio >= 2.0, f"Second load was only {cache_speedup_ratio:.2f}x faster. Expected at least 2x speedup from Redis cache. First: {first_load_time:.3f}s, Second: {second_load_time:.3f}s. This indicates Redis cache is not being utilized properly."
        
        # Verify results are consistent
        assert len(recommendations1) == len(recommendations2), "Cache should return consistent results"

    def test_match_percentage_normalization_bug(self, db_session):
        """Test that match percentages are normalized to 0-100% range.
        
        **Property 1: Fault Condition** - Match Percentage Issues
        **CRITICAL**: This test MUST FAIL on unfixed code
        
        Expected behavior: All match percentages should be in 0-100% range
        Current bug: Raw scores are returned without normalization (could be 25, 35, etc.)
        """
        # Create user profile
        user = User(email="percentage_test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "ai", "web development"]),
            skills=json.dumps(["python", "javascript"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        # Create opportunities with different match levels
        opportunities = [
            # Perfect match - should be close to 100%
            Opportunity(
                title="Perfect Match",
                description="Perfect match opportunity",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=5),  # Urgent
                application_link="https://example.com/perfect",
                tags=json.dumps(["python", "ai", "web development"]),
                required_skills=json.dumps(["python", "javascript"]),
                eligibility="undergraduate",
                location_type="Online",  # Online bonus
                status="active",
            ),
            # Partial match - should be around 50%
            Opportunity(
                title="Partial Match",
                description="Partial match opportunity",
                type="internship",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link="https://example.com/partial",
                tags=json.dumps(["python"]),  # Only 1 match
                required_skills=json.dumps(["python"]),
                eligibility="undergraduate",
                location_type="In-Person",
                status="active",
            ),
            # No match - should be close to 0%
            Opportunity(
                title="No Match",
                description="No match opportunity",
                type="scholarship",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link="https://example.com/nomatch",
                tags=json.dumps(["biology", "chemistry"]),
                required_skills=json.dumps(["lab work"]),
                eligibility="undergraduate",
                location_type="In-Person",
                status="active",
            ),
        ]
        
        db_session.add_all(opportunities)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)
        
        # EXPECTED TO FAIL: Current system returns raw scores, not normalized percentages
        for opportunity, score in recommendations:
            # Convert score to percentage (this is what the UI should display)
            percentage = score  # Current bug: raw score is used as percentage
            
            assert 0 <= percentage <= 100, f"Match percentage {percentage}% for '{opportunity.title}' is not in 0-100% range. Current system returns raw scores (like {score}) instead of normalized percentages. This demonstrates the match percentage normalization bug."

    def test_negative_percentage_bug_from_eligibility_filter(self, db_session):
        """Test that negative percentages are not displayed from eligibility filters.
        
        **Property 1: Fault Condition** - Negative Percentage Display
        **CRITICAL**: This test MUST FAIL on unfixed code
        
        Expected behavior: Ineligible opportunities should not be shown or should show 0%
        Current bug: Hard eligibility filter returns -1000 which could be displayed as negative percentage
        """
        # Create user profile
        user = User(email="eligibility_test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python", "ai"]),
            skills=json.dumps(["python", "tensorflow"]),
            education_level="B.Tech 3rd Year",  # Undergraduate level
        )
        db_session.add(profile)

        # Create opportunity that should trigger eligibility filter
        ineligible_opp = Opportunity(
            title="Graduate Only Research",
            description="Graduate-level research opportunity",
            type="skill_program",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/graduate",
            tags=json.dumps(["python", "ai", "research"]),  # Matches interests
            required_skills=json.dumps(["python", "tensorflow"]),  # Matches skills
            eligibility="Graduate",  # But user is undergraduate - should trigger -1000 score
            location_type="Online",
            status="active",
        )
        
        db_session.add(ineligible_opp)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        recommendations = engine.generate_recommendations(user.id, limit=10)
        
        # Find the ineligible opportunity in recommendations
        ineligible_score = None
        for opportunity, score in recommendations:
            if opportunity.id == ineligible_opp.id:
                ineligible_score = score
                break
        
        if ineligible_score is not None:
            # EXPECTED TO FAIL: Current system may return -1000 score for ineligible opportunities
            # This could be displayed as -1000% or some negative percentage to users
            assert ineligible_score >= 0, f"Ineligible opportunity has negative score {ineligible_score}. This could be displayed as a negative percentage to users (like {ineligible_score}%), which is confusing. The system should either filter out ineligible opportunities or show 0%."

    @given(
        num_opportunities=st.integers(min_value=500, max_value=2000),
        user_interests=st.lists(
            st.sampled_from(["python", "javascript", "ai", "web development", "data science", "blockchain", "cybersecurity"]),
            min_size=1, max_size=5, unique=True
        )
    )
    @settings(max_examples=2, deadline=5000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_performance_scales_poorly_with_dataset_size(self, db_session, num_opportunities, user_interests):
        """Property-based test showing performance degrades with dataset size.
        
        **Property 1: Fault Condition** - Performance Scalability
        **CRITICAL**: This test MUST FAIL on unfixed code
        
        Expected behavior: Performance should scale well with dataset size (sub-linear growth)
        Current bug: Performance degrades linearly/quadratically as all opportunities are loaded and scored
        """
        # Create user profile
        user = User(email=f"scale_test_{num_opportunities}@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(user_interests),
            skills=json.dumps(["python", "javascript"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        # Create opportunities
        opportunities = []
        for i in range(num_opportunities):
            opp = Opportunity(
                title=f"Scale Test Opportunity {i}",
                description=f"Description {i}",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/scale{i}",
                tags=json.dumps(user_interests + ["additional_tag"]),
                required_skills=json.dumps(["python", "javascript"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active",
            )
            opportunities.append(opp)
        
        db_session.add_all(opportunities)
        db_session.commit()

        engine = RecommendationEngine(db_session)
        
        # Measure performance
        start_time = time.time()
        recommendations = engine.generate_recommendations(user.id, limit=10)
        end_time = time.time()
        
        load_time = end_time - start_time
        
        # EXPECTED TO FAIL: Performance should degrade significantly with large datasets
        # With efficient database filtering, this should be fast regardless of dataset size
        time_per_opportunity = load_time / num_opportunities
        
        assert time_per_opportunity < 0.001, f"Time per opportunity: {time_per_opportunity:.6f}s with {num_opportunities} opportunities (total: {load_time:.2f}s). This indicates poor scalability - the system loads and scores ALL opportunities instead of efficient database filtering. Performance should be independent of total dataset size."
        
        # Verify we got results
        assert len(recommendations) > 0, "Should return recommendations"

    def test_cache_key_generation_and_invalidation_bugs(self, db_session):
        """Test Redis cache key generation and invalidation logic.
        
        **Property 1: Fault Condition** - Cache Implementation Issues
        **CRITICAL**: This test MUST FAIL on unfixed code
        
        Expected behavior: Cache keys should be unique per user and invalidate when user profile changes
        Current bug: Cache keys may be incorrectly generated or not invalidated properly
        """
        # Create two different users
        user1 = User(email="cache_user1@example.com")
        user2 = User(email="cache_user2@example.com")
        db_session.add_all([user1, user2])
        db_session.flush()

        profile1 = Profile(
            user_id=user1.id,
            interests=json.dumps(["python", "ai"]),
            skills=json.dumps(["python", "tensorflow"]),
            education_level="undergraduate",
        )
        
        profile2 = Profile(
            user_id=user2.id,
            interests=json.dumps(["javascript", "web development"]),
            skills=json.dumps(["javascript", "react"]),
            education_level="graduate",
        )
        
        db_session.add_all([profile1, profile2])

        # Create opportunities that match different users
        opp1 = Opportunity(
            title="Python AI Opportunity",
            description="Python and AI focused",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/python-ai",
            tags=json.dumps(["python", "ai"]),
            required_skills=json.dumps(["python", "tensorflow"]),
            eligibility="undergraduate",
            location_type="Online",
            status="active",
        )
        
        opp2 = Opportunity(
            title="JavaScript Web Opportunity",
            description="JavaScript and web development",
            type="internship",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/js-web",
            tags=json.dumps(["javascript", "web development"]),
            required_skills=json.dumps(["javascript", "react"]),
            eligibility="graduate",
            location_type="Online",
            status="active",
        )
        
        db_session.add_all([opp1, opp2])
        db_session.commit()

        engine = RecommendationEngine(db_session)
        
        # Get recommendations for both users
        recs1 = engine.generate_recommendations(user1.id, limit=10)
        recs2 = engine.generate_recommendations(user2.id, limit=10)
        
        # EXPECTED TO FAIL: Cache might return wrong results for different users
        # Each user should get different recommendations based on their profile
        
        # Extract opportunity IDs from recommendations
        opp_ids1 = {opp.id for opp, score in recs1}
        opp_ids2 = {opp.id for opp, score in recs2}
        
        # Users with completely different profiles should get different recommendations
        # If cache keys are wrong, user2 might get user1's cached results
        assert opp_ids1 != opp_ids2, f"Users with different profiles got identical recommendations. This suggests cache key generation bug - user2 may be getting user1's cached results. User1 IDs: {opp_ids1}, User2 IDs: {opp_ids2}"
        
        # Verify each user gets recommendations relevant to their profile
        user1_scores = {opp.id: score for opp, score in recs1}
        user2_scores = {opp.id: score for opp, score in recs2}
        
        # User1 should score Python opportunity higher
        if opp1.id in user1_scores and opp1.id in user2_scores:
            assert user1_scores[opp1.id] > user2_scores[opp1.id], "User1 should score Python opportunity higher than User2"
        
        # User2 should score JavaScript opportunity higher  
        if opp2.id in user1_scores and opp2.id in user2_scores:
            assert user2_scores[opp2.id] > user1_scores[opp2.id], "User2 should score JavaScript opportunity higher than User1"

    def test_database_query_efficiency_bug(self, db_session):
        """Test that database queries are inefficient (N+1 problem, loading all data).
        
        **Property 1: Fault Condition** - Database Query Inefficiency
        **CRITICAL**: This test MUST FAIL on unfixed code
        
        Expected behavior: Should use efficient database filtering and JOINs
        Current bug: Loads ALL opportunities then filters in Python (inefficient)
        """
        # Create user profile
        user = User(email="query_efficiency_test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["python"]),
            skills=json.dumps(["python"]),
            education_level="undergraduate",
        )
        db_session.add(profile)

        # Create many opportunities, only few should match
        matching_opportunities = []
        non_matching_opportunities = []
        
        # 10 matching opportunities
        for i in range(10):
            opp = Opportunity(
                title=f"Matching Opportunity {i}",
                description=f"Python opportunity {i}",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/match{i}",
                tags=json.dumps(["python"]),
                required_skills=json.dumps(["python"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active",
            )
            matching_opportunities.append(opp)
        
        # 1000 non-matching opportunities
        for i in range(1000):
            opp = Opportunity(
                title=f"Non-Matching Opportunity {i}",
                description=f"Biology opportunity {i}",
                type="scholarship",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/nomatch{i}",
                tags=json.dumps(["biology", "chemistry"]),
                required_skills=json.dumps(["lab work"]),
                eligibility="graduate",  # Different eligibility
                location_type="In-Person",
                status="active",
            )
            non_matching_opportunities.append(opp)
        
        db_session.add_all(matching_opportunities + non_matching_opportunities)
        db_session.commit()

        # Mock the database query to count how many opportunities are loaded
        original_query = db_session.query
        query_count = {"opportunities_loaded": 0}
        
        def mock_query(model):
            if model == Opportunity:
                query_count["opportunities_loaded"] += 1
            return original_query(model)
        
        with patch.object(db_session, 'query', side_effect=mock_query):
            engine = RecommendationEngine(db_session)
            recommendations = engine.generate_recommendations(user.id, limit=10)
        
        # EXPECTED TO FAIL: Current implementation loads ALL 1010 opportunities
        # Efficient implementation should only load matching opportunities from database
        total_opportunities = len(matching_opportunities) + len(non_matching_opportunities)
        
        # The current implementation queries all opportunities then filters in Python
        # This is inefficient - it should filter at database level
        assert query_count["opportunities_loaded"] == 0, f"Database query loaded all {total_opportunities} opportunities instead of filtering efficiently. Current implementation uses 'db.query(Opportunity).filter(status=active).all()' which loads everything into memory. This demonstrates the database query efficiency bug."
        
        # Verify we still get good results
        assert len(recommendations) > 0, "Should return recommendations"
        
        # All returned recommendations should be relevant (high scores)
        for opportunity, score in recommendations:
            assert score > 0, f"Returned opportunity '{opportunity.title}' has score {score}, indicating poor filtering"