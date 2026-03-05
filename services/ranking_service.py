import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.opportunity import Opportunity

class RankingService:
    """Service for ranking opportunities based on configurable parameters."""

    def __init__(self):
        pass

    def rank_opportunities(
        self,
        opportunities: List[Opportunity],
        sort_by: Optional[str] = None,
        user_interests: Optional[List[str]] = None
    ) -> List[Opportunity]:
        """Rank a list of opportunities based on specified criteria.

        Args:
            opportunities: List of Opportunity models.
            sort_by: Criteria to sort by ('relevance', 'deadline', 'popularity'). Defaults to relevance if interests are provided, else deadline.
            user_interests: Optional list of user interests for relevance matching.

        Returns:
            Sorted list of opportunities.
        """
        if not opportunities:
            return []

        # Determine default sorting if none provided
        if not sort_by:
            sort_by = 'relevance' if user_interests else 'deadline'

        if sort_by == 'deadline':
            return sorted(opportunities, key=lambda x: x.deadline)

        elif sort_by == 'popularity':
            return sorted(opportunities, key=lambda x: getattr(x, 'tracked_count', 0), reverse=True)

        elif sort_by == 'relevance':
            # Score each opportunity based on overlap with user interests
            scored_opps = []
            normalized_interests = set(i.lower().strip() for i in user_interests) if user_interests else set()

            for opp in opportunities:
                score = 0.0
                if normalized_interests:
                    # Parse tags and skills safely
                    opp_tags = set()
                    if opp.tags:
                        try:
                            tags_data = json.loads(opp.tags) if isinstance(opp.tags, str) else opp.tags
                            opp_tags = set(t.lower().strip() for t in tags_data if t)
                        except (json.JSONDecodeError, TypeError):
                            pass

                    opp_skills = set()
                    if opp.required_skills:
                        try:
                            skills_data = json.loads(opp.required_skills) if isinstance(opp.required_skills, str) else opp.required_skills
                            opp_skills = set(s.lower().strip() for s in skills_data if s)
                        except (json.JSONDecodeError, TypeError):
                            pass

                    # Calculate Jaccard-like similarity or simple overlap
                    overlap = len(normalized_interests.intersection(opp_tags.union(opp_skills)))
                    score = float(overlap)
                else:
                    # If no interests, default relevance to something else, like popularity
                    score = float(getattr(opp, 'tracked_count', 0))

                scored_opps.append((opp, score))

            # Sort descending by score
            scored_opps.sort(key=lambda x: x[1], reverse=True)
            return [opp for opp, score in scored_opps]

        # Fallback to no-op
        return opportunities