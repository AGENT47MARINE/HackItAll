"""Recommendation service for generating personalized opportunity recommendations."""
import json
from typing import Dict, Any, List, Tuple
from sqlalchemy.orm import Session

from models.user import Profile
from models.opportunity import Opportunity


class RecommendationEngine:
    """Service for generating personalized opportunity recommendations."""

    def __init__(self, db_session: Session, cache_client=None):
        """Initialize the recommendation engine.

        Args:
            db_session: SQLAlchemy database session
            cache_client: Redis client for caching (optional)
        """
        self.db = db_session
        self.cache = cache_client
        self.cache_ttl = 3600  # 1 hour TTL in seconds

    def generate_recommendations(self, user_id: str, limit: int = 10) -> List[Tuple[Opportunity, float]]:
        """Generate personalized recommendations for a user.

        This method queries all active opportunities, scores them based on the user's profile,
        and returns the top N opportunities ranked by relevance score in descending order.
        Results are cached for 1 hour to improve performance.

        Args:
            user_id: User ID to generate recommendations for
            limit: Maximum number of recommendations to return (default: 10)

        Returns:
            List of tuples containing (Opportunity, score) sorted by score descending
        """
        # Check cache first
        cache_key = f"recommendations:{user_id}:{limit}"
        if self.cache:
            try:
                cached_result = self.cache.get(cache_key)
                if cached_result:
                    # Deserialize cached data
                    import pickle
                    return pickle.loads(cached_result)
            except Exception:
                # If cache fails, continue without it
                pass

        # Get user profile
        from models.user import Profile
        profile = self.db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return []

        # Get user's participation history
        participation_history = self._get_participation_history(user_id)

        # Query all active opportunities
        opportunities = self.db.query(Opportunity).filter(
            Opportunity.status == "active"
        ).all()

        # Score each opportunity
        scored_opportunities = []
        for opportunity in opportunities:
            score = self.calculate_relevance_score(profile, opportunity, participation_history)
            scored_opportunities.append((opportunity, score))

        # Sort by score in descending order
        scored_opportunities.sort(key=lambda x: x[1], reverse=True)

        # Limit results
        result = scored_opportunities[:limit]

        # Cache the result
        if self.cache:
            try:
                import pickle
                self.cache.setex(cache_key, self.cache_ttl, pickle.dumps(result))
            except Exception:
                # If cache fails, continue without it
                pass

        return result

    def _get_participation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's participation history.

        Args:
            user_id: User ID

        Returns:
            List of participation history entries with opportunity type and status
        """
        # This will be implemented when ParticipationHistory model is created
        # For now, return empty list
        try:
            from models.participation import ParticipationHistory
            history_entries = self.db.query(ParticipationHistory).filter(
                ParticipationHistory.user_id == user_id
            ).all()

            # Convert to dict format expected by calculate_relevance_score
            result = []
            for entry in history_entries:
                # Get opportunity type
                opportunity = self.db.query(Opportunity).filter(
                    Opportunity.id == entry.opportunity_id
                ).first()
                if opportunity:
                    result.append({
                        'opportunity_type': opportunity.type,
                        'status': entry.status
                    })
            return result
        except ImportError:
            # ParticipationHistory model not yet implemented
            return []

    def calculate_relevance_score(self, profile: Profile, opportunity: Opportunity,
                                  participation_history: List[Dict[str, Any]] = None) -> float:
        """Calculate relevance score for a user-opportunity pair.

        The scoring algorithm combines multiple factors:
        - Interest match: Percentage of user interests that overlap with opportunity tags
        - Skill match: Percentage of required skills the user possesses
        - Education level compatibility: Binary match (eligible/not eligible)
        - Participation history: Boost score for similar opportunities the user engaged with successfully

        Score = (0.4 × interestMatch) + (0.3 × skillMatch) + (0.2 × educationMatch) + (0.1 × historyBoost)

        Args:
            profile: User profile
            opportunity: Opportunity to score
            participation_history: List of user's past participation entries (optional)

        Returns:
            Relevance score between 0.0 and 1.0
        """
        # Parse JSON fields
        user_interests = json.loads(profile.interests) if isinstance(profile.interests, str) else profile.interests
        user_skills = json.loads(profile.skills) if isinstance(profile.skills, str) else profile.skills
        opportunity_tags = json.loads(opportunity.tags) if isinstance(opportunity.tags, str) else opportunity.tags
        opportunity_skills = json.loads(opportunity.required_skills) if isinstance(opportunity.required_skills, str) else opportunity.required_skills

        # Convert to lowercase for case-insensitive matching
        user_interests_lower = [interest.lower() for interest in user_interests]
        user_skills_lower = [skill.lower() for skill in user_skills]
        opportunity_tags_lower = [tag.lower() for tag in opportunity_tags]
        opportunity_skills_lower = [skill.lower() for skill in opportunity_skills]

        # Calculate interest match (0.0 to 1.0)
        interest_match = self._calculate_interest_match(user_interests_lower, opportunity_tags_lower)

        # Calculate skill match (0.0 to 1.0)
        skill_match = self._calculate_skill_match(user_skills_lower, opportunity_skills_lower)

        # Calculate education match (0.0 or 1.0)
        education_match = self._calculate_education_match(profile.education_level, opportunity.eligibility)

        # Calculate history boost (0.0 to 1.0)
        history_boost = self._calculate_history_boost(opportunity.type, participation_history)

        # Apply scoring formula
        score = (0.4 * interest_match) + (0.3 * skill_match) + (0.2 * education_match) + (0.1 * history_boost)

        return score

    def _calculate_interest_match(self, user_interests: List[str], opportunity_tags: List[str]) -> float:
        """Calculate interest match score.

        Args:
            user_interests: List of user interests (lowercase)
            opportunity_tags: List of opportunity tags (lowercase)

        Returns:
            Interest match score between 0.0 and 1.0
        """
        if not user_interests:
            return 0.0

        if not opportunity_tags:
            return 0.0

        # Count how many user interests match opportunity tags
        matching_interests = sum(1 for interest in user_interests if interest in opportunity_tags)

        # Return percentage of user interests that match
        return matching_interests / len(user_interests)

    def _calculate_skill_match(self, user_skills: List[str], required_skills: List[str]) -> float:
        """Calculate skill match score.

        Args:
            user_skills: List of user skills (lowercase)
            required_skills: List of required skills (lowercase)

        Returns:
            Skill match score between 0.0 and 1.0
        """
        if not required_skills:
            # If no skills are required, give full score
            return 1.0

        if not user_skills:
            # If user has no skills but opportunity requires skills, give zero score
            return 0.0

        # Count how many required skills the user has
        matching_skills = sum(1 for skill in required_skills if skill in user_skills)

        # Return percentage of required skills the user possesses
        return matching_skills / len(required_skills)

    def _calculate_education_match(self, user_education: str, required_education: str) -> float:
        """Calculate education match score.

        Args:
            user_education: User's education level
            required_education: Required education level (or None if no requirement)

        Returns:
            Education match score: 1.0 if eligible, 0.0 if not eligible
        """
        # If no education requirement, user is eligible
        if not required_education:
            return 1.0

        # Simple exact match for now (can be enhanced with education level hierarchy)
        return 1.0 if user_education.lower() == required_education.lower() else 0.0

    def _calculate_history_boost(self, opportunity_type: str,
                                participation_history: List[Dict[str, Any]] = None) -> float:
        """Calculate history boost score based on past successful participation.

        Args:
            opportunity_type: Type of the current opportunity
            participation_history: List of user's past participation entries

        Returns:
            History boost score between 0.0 and 1.0
        """
        if not participation_history:
            return 0.0

        # Count successful participations in similar opportunity types
        successful_similar = 0
        total_similar = 0

        for entry in participation_history:
            # Check if this entry is for a similar opportunity type
            if entry.get('opportunity_type') == opportunity_type:
                total_similar += 1
                # Count as successful if status is 'completed' or 'accepted'
                if entry.get('status') in ['completed', 'accepted']:
                    successful_similar += 1

        # If user has no history with this type, return 0
        if total_similar == 0:
            return 0.0

        # Return ratio of successful to total participations in this type
        return successful_similar / total_similar

