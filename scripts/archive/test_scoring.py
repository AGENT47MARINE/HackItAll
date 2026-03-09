#!/usr/bin/env python3

from services.recommendation_service import RecommendationEngine
from models.user import Profile
from models.opportunity import Opportunity
import json
from datetime import datetime, timedelta

def test_ineligible_opportunity():
    """Test that ineligible opportunities return None"""
    # Create test profile (high school student)
    profile = Profile()
    profile.interests = json.dumps(['python', 'web development'])
    profile.skills = json.dumps(['python'])
    profile.education_level = 'high school'

    # Create test opportunity (requires graduate level)
    opportunity = Opportunity()
    opportunity.title = 'Senior Developer Position'
    opportunity.tags = json.dumps(['python', 'web development'])
    opportunity.required_skills = json.dumps(['python'])
    opportunity.location_type = 'remote'
    opportunity.type = 'job'
    opportunity.deadline = datetime.utcnow() + timedelta(days=30)
    opportunity.eligibility = 'graduate degree required'
    opportunity.status = 'active'

    # Test scoring
    engine = RecommendationEngine(None)
    score = engine.calculate_relevance_score(profile, opportunity)
    print(f'Ineligible test - Score: {score}')
    print(f'Result: {"Ineligible - filtered out" if score is None else f"Eligible - {score * 100:.1f}%"}')
    return score is None

def test_eligible_opportunity():
    """Test that eligible opportunities return normalized scores"""
    # Create test profile
    profile = Profile()
    profile.interests = json.dumps(['python', 'web development', 'machine learning'])
    profile.skills = json.dumps(['python', 'javascript', 'sql'])
    profile.education_level = 'undergraduate'
    profile.location = 'San Francisco'

    # Create test opportunity
    opportunity = Opportunity()
    opportunity.title = 'Python Developer Internship'
    opportunity.description = 'Looking for Python developers'
    opportunity.tags = json.dumps(['python', 'web development', 'internship'])
    opportunity.required_skills = json.dumps(['python', 'javascript'])
    opportunity.location_type = 'hybrid'
    opportunity.location = 'San Francisco'
    opportunity.type = 'internship'
    opportunity.deadline = datetime.utcnow() + timedelta(days=10)
    opportunity.eligibility = 'undergraduate students'
    opportunity.status = 'active'

    # Test scoring
    engine = RecommendationEngine(None)
    score = engine.calculate_relevance_score(profile, opportunity)
    print(f'Eligible test - Score: {score}')
    print(f'Percentage: {score * 100:.1f}%' if score is not None else 'Ineligible')
    return score is not None and 0 <= score <= 1

if __name__ == "__main__":
    print("Testing new scoring algorithm...")
    
    print("\n1. Testing ineligible opportunity filtering:")
    ineligible_work