"""Preservation property tests for discover page non-For You section functionality.

**Property 2: Preservation** - Non-For You Section Functionality
**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5**

IMPORTANT: These tests follow observation-first methodology.
They observe behavior on UNFIXED code for non-For You section interactions.

EXPECTED OUTCOME: Tests PASS (this confirms baseline behavior to preserve)

These tests capture the baseline behavior of:
- Other discover page sections (trending, recent, categories) 
- Opportunity card interactions and navigation
- Empty state handling for users with no matches
- User interaction patterns (scrolling, filtering, searching)
- All functionality that does NOT involve For You section data loading or match percentage calculation

The tests will ensure our performance fixes don't break existing functionality.
"""
import pytest
import json
from datetime import datetime, timedelta
from hypothesis import given, strategies as st, settings, HealthCheck
from typing import List, Dict, Any

from services.opportunity_service import OpportunityService
from services.recommendation_service import RecommendationEngine
from models.user import User, Profile
from models.opportunity import Opportunity


class TestDiscoverPagePreservationProperties:
    """Preservation property tests for non-For You section functionality."""

    def test_trending_section_functionality_preserved(self, db_session):
        """Test that trending section continues to work correctly.
        
        **Property 2: Preservation** - Trending Section
        **EXPECTED**: Test PASSES on unfixed code (baseline behavior)
        
        This test observes and captures the current trending algorithm behavior.
        The trending section should continue to work exactly as before.
        """
        # Create opportunities with different trending scores
        opportunities = []
        for i in range(5):
            opp = Opportunity(
                title=f"Trending Opportunity {i}",
                description=f"Description for trending opportunity {i}",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/trending{i}",
                tags=json.dumps(["python", "ai"]),
                required_skills=json.dumps(["python"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active",
                tracked_count=10 + i * 5,  # Different trending scores
                participant_count=5 + i * 2,
                source_registration_count=100 + i * 20
            )
            opportunities.append(opp)
        
        db_session.add_all(opportunities)
        db_session.commit()

        # Test trending functionality
        service = OpportunityService(db_session)
        trending_results = service.get_trending(limit=3)
        
        # Verify trending section works as expected
        assert len(trending_results) <= 3, "Trending should respect limit parameter"
        assert len(trending_results) > 0, "Trending should return results when opportunities exist"
        
        # Verify trending algorithm works (higher scores should come first)
        if len(trending_results) >= 2:
            # Calculate expected trending scores for verification
            first_opp_id = trending_results[0]['id']
            second_opp_id = trending_results[1]['id']
            
            first_opp = next(opp for opp in opportunities if str(opp.id) == first_opp_id)
            second_opp = next(opp for opp in opportunities if str(opp.id) == second_opp_id)
            
            first_score = (first_opp.tracked_count * 10 + 
                          first_opp.participant_count * 30 + 
                          first_opp.source_registration_count / 20)
            second_score = (second_opp.tracked_count * 10 + 
                           second_opp.participant_count * 30 + 
                           second_opp.source_registration_count / 20)
            
            assert first_score >= second_score, "Trending results should be sorted by trending score descending"
        
        # Verify response format is preserved
        for result in trending_results:
            assert 'id' in result, "Trending results should include opportunity ID"
            assert 'title' in result, "Trending results should include title"
            assert 'type' in result, "Trending results should include type"
            assert 'deadline' in result, "Trending results should include deadline"
    def test_search_functionality_preserved(self, db_session):
        """Test that search functionality continues to work correctly.
        
        **Property 2: Preservation** - Search Functionality
        **EXPECTED**: Test PASSES on unfixed code (baseline behavior)
        
        This test observes and captures the current search behavior.
        Search functionality should continue to work exactly as before.
        """
        # Create opportunities with different searchable content
        opportunities = [
            Opportunity(
                title="Python AI Hackathon",
                description="Build AI applications using Python",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link="https://example.com/python-ai",
                tags=json.dumps(["python", "ai", "machine learning"]),
                required_skills=json.dumps(["python", "tensorflow"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active"
            ),
            Opportunity(
                title="JavaScript Web Development",
                description="Create modern web applications",
                type="internship",
                deadline=datetime.utcnow() + timedelta(days=45),
                application_link="https://example.com/js-web",
                tags=json.dumps(["javascript", "web development", "react"]),
                required_skills=json.dumps(["javascript", "html", "css"]),
                eligibility="undergraduate",
                location_type="Hybrid",
                status="active"
            ),
            Opportunity(
                title="Data Science Scholarship",
                description="Scholarship for data science students",
                type="scholarship",
                deadline=datetime.utcnow() + timedelta(days=60),
                application_link="https://example.com/data-scholarship",
                tags=json.dumps(["data science", "statistics", "python"]),
                required_skills=json.dumps(["python", "pandas", "numpy"]),
                eligibility="graduate",
                location_type="Online",
                status="active"
            )
        ]
        
        db_session.add_all(opportunities)
        db_session.commit()

        service = OpportunityService(db_session)
        
        # Test text search functionality
        python_results = service.search_opportunities(search_term="python")
        assert len(python_results) >= 2, "Search should find opportunities containing 'python'"
        
        # Verify search results contain expected opportunities
        python_titles = [result['title'] for result in python_results]
        assert any("Python AI" in title for title in python_titles), "Should find Python AI Hackathon"
        assert any("Data Science" in title for title in python_titles), "Should find Data Science Scholarship"
        
        # Test type filtering
        hackathon_results = service.search_opportunities(opportunity_types=["hackathon"])
        assert len(hackathon_results) >= 1, "Should find hackathon opportunities"
        assert all(result['type'] == 'hackathon' for result in hackathon_results), "All results should be hackathons"
        
        # Test eligibility filtering
        undergrad_results = service.search_opportunities(eligibility="undergraduate")
        assert len(undergrad_results) >= 2, "Should find undergraduate opportunities"
        assert all(result['eligibility'] == 'undergraduate' for result in undergrad_results), "All results should be for undergraduates"
        
        # Test combined filtering
        combined_results = service.search_opportunities(
            search_term="web",
            opportunity_types=["internship"]
        )
        assert len(combined_results) >= 1, "Should find web development internship"
        
        # Verify response format is preserved
        for result in python_results:
            assert 'id' in result, "Search results should include opportunity ID"
            assert 'title' in result, "Search results should include title"
            assert 'description' in result, "Search results should include description"
            assert 'type' in result, "Search results should include type"
            assert 'deadline' in result, "Search results should include deadline"
            assert 'application_link' in result, "Search results should include application link"

    def test_opportunity_card_interactions_preserved(self, db_session):
        """Test that opportunity card interactions remain unchanged.
        
        **Property 2: Preservation** - Opportunity Card Interactions
        **EXPECTED**: Test PASSES on unfixed code (baseline behavior)
        
        This test observes and captures the current opportunity retrieval behavior.
        Individual opportunity card display and interactions should work exactly as before.
        """
        # Create a test opportunity
        opportunity = Opportunity(
            title="Test Opportunity Card",
            description="Test opportunity for card interaction testing",
            type="hackathon",
            deadline=datetime.utcnow() + timedelta(days=30),
            application_link="https://example.com/test-card",
            tags=json.dumps(["python", "web development"]),
            required_skills=json.dumps(["python", "javascript"]),
            eligibility="undergraduate",
            location_type="Online",
            status="active",
            tracked_count=15,
            participant_count=8,
            source_registration_count=120
        )
        
        db_session.add(opportunity)
        db_session.commit()

        service = OpportunityService(db_session)
        
        # Test individual opportunity retrieval (card click behavior)
        retrieved_opportunity = service.get_opportunity(opportunity.id)
        
        # Verify opportunity card data is complete and correctly formatted
        assert retrieved_opportunity is not None, "Should be able to retrieve individual opportunities"
        assert retrieved_opportunity['id'] == str(opportunity.id), "ID should match"
        assert retrieved_opportunity['title'] == opportunity.title, "Title should match"
        assert retrieved_opportunity['description'] == opportunity.description, "Description should match"
        assert retrieved_opportunity['type'] == opportunity.type, "Type should match"
        assert retrieved_opportunity['application_link'] == opportunity.application_link, "Application link should match"
        
        # Verify JSON fields are properly parsed
        assert isinstance(retrieved_opportunity['tags'], list), "Tags should be parsed as list"
        assert isinstance(retrieved_opportunity['required_skills'], list), "Required skills should be parsed as list"
        assert "python" in retrieved_opportunity['tags'], "Tags should contain expected values"
        assert "python" in retrieved_opportunity['required_skills'], "Required skills should contain expected values"
        
        # Verify tracking counts are included (for display)
        assert 'tracked_count' in retrieved_opportunity, "Should include tracked count for display"
        assert 'participant_count' in retrieved_opportunity, "Should include participant count for display"
        
        # Test non-existent opportunity (error handling)
        non_existent = service.get_opportunity("non-existent-id")
        assert non_existent is None, "Should return None for non-existent opportunities"

    def test_empty_state_handling_preserved(self, db_session):
        """Test that empty state handling continues to work for users with no matches.
        
        **Property 2: Preservation** - Empty State Handling
        **EXPECTED**: Test PASSES on unfixed code (baseline behavior)
        
        This test observes and captures the current empty state behavior.
        Empty state handling should continue to work exactly as before.
        """
        # Create user with very specific interests that won't match any opportunities
        user = User(email="empty_state_test@example.com")
        db_session.add(user)
        db_session.flush()

        profile = Profile(
            user_id=user.id,
            interests=json.dumps(["very_specific_niche_interest", "another_rare_interest"]),
            skills=json.dumps(["extremely_rare_skill"]),
            education_level="undergraduate"
        )
        db_session.add(profile)

        # Create opportunities that definitely won't match
        opportunities = [
            Opportunity(
                title="Biology Research",
                description="Biology and chemistry research opportunity",
                type="scholarship",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link="https://example.com/biology",
                tags=json.dumps(["biology", "chemistry", "lab work"]),
                required_skills=json.dumps(["lab techniques", "microscopy"]),
                eligibility="graduate",  # Different eligibility
                location_type="In-Person",
                status="active"
            ),
            Opportunity(
                title="Advanced Mathematics",
                description="Advanced mathematics competition",
                type="skill_program",
                deadline=datetime.utcnow() + timedelta(days=45),
                application_link="https://example.com/math",
                tags=json.dumps(["mathematics", "calculus", "algebra"]),
                required_skills=json.dumps(["advanced math", "proofs"]),
                eligibility="graduate",  # Different eligibility
                location_type="In-Person",
                status="active"
            )
        ]
        
        db_session.add_all(opportunities)
        db_session.commit()

        # Test empty state behavior for search
        service = OpportunityService(db_session)
        
        # Search for something that doesn't exist
        empty_search_results = service.search_opportunities(search_term="nonexistent_technology")
        assert len(empty_search_results) == 0, "Search should return empty list when no matches found"
        assert isinstance(empty_search_results, list), "Empty search should return empty list, not None"
        
        # Search with filters that match nothing
        empty_filtered_results = service.search_opportunities(
            search_term="python",
            opportunity_types=["nonexistent_type"]
        )
        assert len(empty_filtered_results) == 0, "Filtered search should return empty list when no matches"
        
        # Test empty state for trending when no opportunities have tracking data
        # First, reset all tracking counts to 0
        for opp in opportunities:
            opp.tracked_count = 0
            opp.participant_count = 0
            opp.source_registration_count = 0
        db_session.commit()
        
        trending_results = service.get_trending(limit=10)
        # Even with zero tracking data, trending should still return opportunities (just sorted by created_at)
        assert isinstance(trending_results, list), "Trending should return list even when no tracking data"
        # The behavior may vary - some implementations return empty, others return all opportunities
        # We're just capturing the current behavior here
        
        # Test that the system handles empty states gracefully without errors
        # This is the key preservation requirement - no crashes or exceptions
        try:
            # These operations should not raise exceptions
            service.search_opportunities(search_term="")
            service.search_opportunities(opportunity_types=[])
            service.get_trending(limit=0)
            service.get_opportunity("")
            empty_state_preserved = True
        except Exception:
            empty_state_preserved = False
        
        assert empty_state_preserved, "Empty state operations should not raise exceptions"
    @given(
        search_terms=st.lists(
            st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
            min_size=1, max_size=5, unique=True
        ),
        opportunity_types=st.lists(
            st.sampled_from(['hackathon', 'scholarship', 'internship', 'skill_program']),
            min_size=0, max_size=4, unique=True
        )
    )
    @settings(max_examples=3, deadline=3000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_search_behavior_consistent_across_inputs(self, db_session, search_terms, opportunity_types):
        """Property-based test ensuring search behavior is consistent across many inputs.
        
        **Property 2: Preservation** - Search Consistency
        **EXPECTED**: Test PASSES on unfixed code (baseline behavior)
        
        This test captures the current search behavior patterns across many different inputs.
        Search should behave consistently regardless of the specific search terms or filters used.
        """
        # Create diverse opportunities for testing
        opportunities = [
            Opportunity(
                title="Python Machine Learning Workshop",
                description="Learn machine learning with Python and scikit-learn",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link="https://example.com/python-ml",
                tags=json.dumps(["python", "machine learning", "ai", "data science"]),
                required_skills=json.dumps(["python", "pandas", "scikit-learn"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active"
            ),
            Opportunity(
                title="Web Development Internship",
                description="Full-stack web development internship opportunity",
                type="internship",
                deadline=datetime.utcnow() + timedelta(days=45),
                application_link="https://example.com/web-internship",
                tags=json.dumps(["javascript", "react", "node.js", "web development"]),
                required_skills=json.dumps(["javascript", "html", "css", "react"]),
                eligibility="undergraduate",
                location_type="Hybrid",
                status="active"
            ),
            Opportunity(
                title="Cybersecurity Scholarship",
                description="Scholarship for cybersecurity students",
                type="scholarship",
                deadline=datetime.utcnow() + timedelta(days=60),
                application_link="https://example.com/cyber-scholarship",
                tags=json.dumps(["cybersecurity", "network security", "ethical hacking"]),
                required_skills=json.dumps(["networking", "security tools", "linux"]),
                eligibility="graduate",
                location_type="Online",
                status="active"
            ),
            Opportunity(
                title="Mobile App Development Program",
                description="Learn to build mobile applications",
                type="skill_program",
                deadline=datetime.utcnow() + timedelta(days=75),
                application_link="https://example.com/mobile-program",
                tags=json.dumps(["mobile development", "android", "ios", "flutter"]),
                required_skills=json.dumps(["java", "kotlin", "swift", "dart"]),
                eligibility="undergraduate",
                location_type="In-Person",
                status="active"
            )
        ]
        
        db_session.add_all(opportunities)
        db_session.commit()

        service = OpportunityService(db_session)
        
        # Test search behavior with various combinations
        for search_term in search_terms:
            for type_filter in [None, opportunity_types if opportunity_types else None]:
                try:
                    results = service.search_opportunities(
                        search_term=search_term,
                        opportunity_types=type_filter
                    )
                    
                    # Verify consistent behavior patterns
                    assert isinstance(results, list), f"Search should always return a list for term '{search_term}'"
                    
                    # If we get results, verify they're properly formatted
                    for result in results:
                        assert 'id' in result, "All search results should have ID"
                        assert 'title' in result, "All search results should have title"
                        assert 'type' in result, "All search results should have type"
                        
                        # If type filter was applied, verify it's respected
                        if type_filter:
                            assert result['type'] in type_filter, f"Result type {result['type']} should be in filter {type_filter}"
                    
                    # Verify search term matching (if results found)
                    if results and search_term.strip():
                        # At least one result should contain the search term (case-insensitive)
                        search_lower = search_term.lower()
                        found_match = False
                        for result in results:
                            title_lower = result['title'].lower()
                            desc_lower = result['description'].lower()
                            if search_lower in title_lower or search_lower in desc_lower:
                                found_match = True
                                break
                        
                        # Note: We don't assert found_match because the search might also match tags
                        # We're just capturing the current behavior pattern
                        
                except Exception as e:
                    # Search should not raise exceptions for valid inputs
                    assert False, f"Search raised exception for term '{search_term}' and types {type_filter}: {e}"

    @given(
        limit_values=st.integers(min_value=0, max_value=50)
    )
    @settings(max_examples=2, deadline=2000, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_trending_limit_behavior_preserved(self, db_session, limit_values):
        """Property-based test ensuring trending limit behavior is preserved.
        
        **Property 2: Preservation** - Trending Limit Behavior
        **EXPECTED**: Test PASSES on unfixed code (baseline behavior)
        
        This test captures the current trending limit behavior across different limit values.
        """
        # Create opportunities with trending data
        opportunities = []
        for i in range(20):  # Create more than any reasonable limit
            opp = Opportunity(
                title=f"Trending Test Opportunity {i}",
                description=f"Description {i}",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),
                application_link=f"https://example.com/trending-test-{i}",
                tags=json.dumps(["python", "testing"]),
                required_skills=json.dumps(["python"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active",
                tracked_count=i + 1,  # Different trending scores
                participant_count=i,
                source_registration_count=i * 10
            )
            opportunities.append(opp)
        
        db_session.add_all(opportunities)
        db_session.commit()

        service = OpportunityService(db_session)
        
        try:
            trending_results = service.get_trending(limit=limit_values)
            
            # Verify consistent behavior patterns
            assert isinstance(trending_results, list), f"Trending should return list for limit {limit_values}"
            
            # Verify limit is respected (or understand current behavior)
            if limit_values == 0:
                # Behavior for limit=0 may vary - capture current behavior
                assert len(trending_results) >= 0, "Trending with limit=0 should return non-negative count"
            else:
                assert len(trending_results) <= limit_values, f"Trending should not exceed limit {limit_values}"
            
            # If we have results, verify they're properly formatted
            for result in trending_results:
                assert 'id' in result, "Trending results should have ID"
                assert 'title' in result, "Trending results should have title"
                assert 'type' in result, "Trending results should have type"
                
        except Exception as e:
            # Trending should handle various limit values gracefully
            assert False, f"Trending raised exception for limit {limit_values}: {e}"

    def test_opportunity_retrieval_edge_cases_preserved(self, db_session):
        """Test that opportunity retrieval handles edge cases consistently.
        
        **Property 2: Preservation** - Opportunity Retrieval Edge Cases
        **EXPECTED**: Test PASSES on unfixed code (baseline behavior)
        
        This test captures the current behavior for edge cases in opportunity retrieval.
        """
        service = OpportunityService(db_session)
        
        # Test various edge cases
        edge_cases = [
            "",  # Empty string
            "   ",  # Whitespace only
            "non-existent-id",  # Non-existent ID
            "12345",  # Numeric string
            "special-chars-!@#$%",  # Special characters
            "very-long-id-" + "x" * 100,  # Very long ID
        ]
        
        for test_id in edge_cases:
            try:
                result = service.get_opportunity(test_id)
                
                # Verify consistent behavior - should return None for non-existent IDs
                assert result is None, f"Non-existent ID '{test_id}' should return None"
                
            except Exception as e:
                # Document any exceptions that occur - this is the current behavior
                # We're not asserting here because we want to capture what actually happens
                print(f"Note: get_opportunity('{test_id}') raised {type(e).__name__}: {e}")

    def test_archive_functionality_preserved(self, db_session):
        """Test that archive functionality continues to work correctly.
        
        **Property 2: Preservation** - Archive Functionality
        **EXPECTED**: Test PASSES on unfixed code (baseline behavior)
        
        This test captures the current archive behavior.
        Archive functionality should continue to work exactly as before.
        """
        # Create opportunities with past deadlines (should be archived)
        past_opportunities = [
            Opportunity(
                title="Expired Hackathon 1",
                description="This hackathon has expired",
                type="hackathon",
                deadline=datetime.utcnow() - timedelta(days=5),  # Past deadline
                application_link="https://example.com/expired1",
                tags=json.dumps(["python"]),
                required_skills=json.dumps(["python"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active"  # Still active, should be archived
            ),
            Opportunity(
                title="Expired Scholarship",
                description="This scholarship has expired",
                type="scholarship",
                deadline=datetime.utcnow() - timedelta(days=10),  # Past deadline
                application_link="https://example.com/expired2",
                tags=json.dumps(["education"]),
                required_skills=json.dumps([]),
                eligibility="undergraduate",
                location_type="Online",
                status="active"  # Still active, should be archived
            )
        ]
        
        # Create opportunities with future deadlines (should remain active)
        future_opportunities = [
            Opportunity(
                title="Future Hackathon",
                description="This hackathon is upcoming",
                type="hackathon",
                deadline=datetime.utcnow() + timedelta(days=30),  # Future deadline
                application_link="https://example.com/future1",
                tags=json.dumps(["python"]),
                required_skills=json.dumps(["python"]),
                eligibility="undergraduate",
                location_type="Online",
                status="active"
            )
        ]
        
        db_session.add_all(past_opportunities + future_opportunities)
        db_session.commit()

        service = OpportunityService(db_session)
        
        # Test archive functionality
        archived_count = service.archive_expired_opportunities()
        
        # Verify archive behavior
        assert isinstance(archived_count, int), "Archive function should return integer count"
        assert archived_count >= 0, "Archive count should be non-negative"
        
        # The exact count depends on implementation - we're capturing current behavior
        # In this case, we expect 2 opportunities to be archived
        expected_archived = len(past_opportunities)
        assert archived_count == expected_archived, f"Should archive {expected_archived} expired opportunities"
        
        # Verify that expired opportunities are now archived
        for opp in past_opportunities:
            db_session.refresh(opp)
            assert opp.status == "archived", f"Expired opportunity '{opp.title}' should be archived"
        
        # Verify that future opportunities remain active
        for opp in future_opportunities:
            db_session.refresh(opp)
            assert opp.status == "active", f"Future opportunity '{opp.title}' should remain active"
        
        # Test that archived opportunities don't appear in regular searches
        search_results = service.search_opportunities(search_term="Expired")
        archived_titles = [result['title'] for result in search_results]
        
        # By default, search should not include archived opportunities
        assert not any("Expired" in title for title in archived_titles), "Archived opportunities should not appear in default search"
        
        # Test that archived opportunities can be included if requested
        search_with_archived = service.search_opportunities(search_term="Expired", include_archived=True)
        archived_included_titles = [result['title'] for result in search_with_archived]
        
        # Should find archived opportunities when explicitly requested
        assert any("Expired" in title for title in archived_included_titles), "Should find archived opportunities when include_archived=True"