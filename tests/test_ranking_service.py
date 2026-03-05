import pytest
from datetime import datetime, timedelta
from models.opportunity import Opportunity
from services.ranking_service import RankingService
import json

def test_ranking_by_deadline():
    now = datetime.utcnow()
    opp1 = Opportunity(id="1", deadline=now + timedelta(days=10))
    opp2 = Opportunity(id="2", deadline=now + timedelta(days=2))
    opp3 = Opportunity(id="3", deadline=now + timedelta(days=5))

    service = RankingService()
    ranked = service.rank_opportunities([opp1, opp2, opp3], sort_by="deadline")

    assert [o.id for o in ranked] == ["2", "3", "1"]

def test_ranking_by_popularity():
    opp1 = Opportunity(id="1", tracked_count=5)
    opp2 = Opportunity(id="2", tracked_count=20)
    opp3 = Opportunity(id="3", tracked_count=10)

    service = RankingService()
    ranked = service.rank_opportunities([opp1, opp2, opp3], sort_by="popularity")

    assert [o.id for o in ranked] == ["2", "3", "1"]

def test_ranking_by_relevance():
    opp1 = Opportunity(id="1", tags=json.dumps(["python", "ai"]), required_skills=json.dumps(["machine learning"]))
    opp2 = Opportunity(id="2", tags=json.dumps(["javascript", "web"]), required_skills=json.dumps(["react"]))
    opp3 = Opportunity(id="3", tags=json.dumps(["python", "web"]), required_skills=json.dumps(["django"]))

    service = RankingService()
    interests = ["python", "machine learning"]

    ranked = service.rank_opportunities([opp1, opp2, opp3], sort_by="relevance", user_interests=interests)

    # opp1 has 2 matches (python, machine learning)
    # opp3 has 1 match (python)
    # opp2 has 0 matches
    assert [o.id for o in ranked] == ["1", "3", "2"]