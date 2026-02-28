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
            cache_client: (Deprecated) Redis client for caching. We now use zero-cost local file caching.
        """
        self.db = db_session
        self.cache_ttl = 3600  # 1 hour TTL in seconds
        self.cache_file = ".recommendation_cache.json"

    def _read_cache(self) -> Dict[str, Any]:
        """Read the local JSON cache file."""
        import os
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, "r") as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}

    def _write_cache(self, data: Dict[str, Any]):
        """Write to the local JSON cache file."""
        try:
            with open(self.cache_file, "w") as f:
                json.dump(data, f)
        except Exception:
            pass

    def generate_recommendations(self, user_id: str, limit: int = 10) -> List[Tuple[Opportunity, float]]:
        """Generate personalized recommendations for a user.

        This method queries all active opportunities, scores them based on the user's profile,
        and returns the top N opportunities ranked by relevance score in descending order.
        Results are cached locally using a JSON file for 1 hour to improve performance.

        Args:
            user_id: User ID to generate recommendations for
            limit: Maximum number of recommendations to return (default: 10)

        Returns:
            List of tuples containing (Opportunity, score) sorted by score descending
        """
        import time
        
        # Check local file cache first
        cache_key = f"rec_{user_id}_{limit}"
        cache_data = self._read_cache()
        
        if cache_key in cache_data:
            entry = cache_data[cache_key]
            # Check TTL
            if time.time() - entry.get('timestamp', 0) < self.cache_ttl:
                # Cache hit! Reconstruct the Opportunity objects from IDs
                try:
                    result = []
                    for item in entry.get('results', []):
                        opp = self.db.query(Opportunity).filter(Opportunity.id == item['id']).first()
                        if opp:
                            result.append((opp, item['score']))
                    if result:
                        return result
                except Exception:
                    pass # Fall through to recalculate

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

        # Cache the result to the local file
        try:
            # We only cache the IDs and scores, not the full SQLAlchemy objects
            serialized_results = [{'id': opp.id, 'score': score} for opp, score in result]
            cache_data[cache_key] = {
                'timestamp': time.time(),
                'results': serialized_results
            }
            self._write_cache(cache_data)
        except Exception as e:
            # If cache fails, continue without it
            print(f"Warning: Failed to write to local cache: {e}")

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
        - ML Semantic Match (TF-IDF Cosine Similarity): Comparing profile text vs opportunity text
        - Education level compatibility: Binary match (eligible/not eligible)
        - Participation history: Boost score for similar opportunities the user engaged with successfully

        Score = (0.7 * mlScore) + (0.2 * educationMatch) + (0.1 * historyBoost)

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

        # Convert to lowercase for case-insensitive matching in ML fallback
        user_interests_lower = [interest.lower() for interest in user_interests]
        user_skills_lower = [skill.lower() for skill in user_skills]
        opportunity_tags_lower = [tag.lower() for tag in opportunity_tags]
        opportunity_skills_lower = [skill.lower() for skill in opportunity_skills]
        
        # Safe text extraction
        opp_title = opportunity.title or ""
        opp_desc = opportunity.description or ""

        # Calculate ML semantic match (0.0 to 1.0)
        ml_score = self._calculate_ml_semantic_match(
            user_interests=user_interests_lower,
            user_skills=user_skills_lower,
            opp_title=opp_title,
            opp_desc=opp_desc,
            opp_tags=opportunity_tags_lower,
            opp_skills=opportunity_skills_lower
        )

        # Calculate education match (0.0 or 1.0)
        education_match = self._calculate_education_match(profile.education_level, opportunity.eligibility)

        # Calculate history boost (0.0 to 1.0)
        history_boost = self._calculate_history_boost(opportunity.type, participation_history)

        # Apply scoring formula
        # Weights: 70% ML Semantic Match, 20% Education Match, 10% History Boost
        score = (0.7 * ml_score) + (0.2 * education_match) + (0.1 * history_boost)

        return score

    def _calculate_ml_semantic_match(self, user_interests: List[str], user_skills: List[str], 
                                     opp_title: str, opp_desc: str, opp_tags: List[str], opp_skills: List[str]) -> float:
        """Calculate semantic match score using TF-IDF and Cosine Similarity.
        
        Args:
            user_interests: List of user interests
            user_skills: List of user skills
            opp_title: Opportunity title
            opp_desc: Opportunity description
            opp_tags: Opportunity tags
            opp_skills: Required skills for the opportunity
            
        Returns:
            Cosine similarity score between 0.0 and 1.0
        """
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            # 1. Construct the "User Profile Document"
            # We heavily weight skills by repeating them, ensuring the ML model prioritizes them over generic interests
            user_doc = " ".join(user_skills) + " " + " ".join(user_skills) + " " + " ".join(user_interests)
            
            # 2. Construct the "Opportunity Document"
            # We heavily weight the required skills and tags
            opp_doc = opp_title + " " + opp_desc + " " + " ".join(opp_tags) + " " + " ".join(opp_skills) + " " + " ".join(opp_skills)
            
            # If either document is empty, return 0
            if not user_doc.strip() or not opp_doc.strip():
                return 0.0
                
            # 3. Vectorize and Calculate Cosine Similarity
            vectorizer = TfidfVectorizer(stop_words='english')
            tfidf_matrix = vectorizer.fit_transform([user_doc, opp_doc])
            
            # The matrix has 2 rows (User and Opp). We want the similarity between row 0 and row 1.
            similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])
            
            return float(similarity[0][0])
            
        except ImportError:
            # Fallback to simple matching if scikit-learn is not available
            print("WARNING: scikit-learn not installed. Falling back to basic matching.")
            user_terms = set([s.lower() for s in user_skills + user_interests])
            opp_terms = set([s.lower() for s in opp_tags + opp_skills])
            
            if not user_terms or not opp_terms:
                return 0.0
                
            match_count = len(user_terms.intersection(opp_terms))
            return match_count / max(len(user_terms), 1)

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

        # Simple exact match for now
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

    def analyze_skill_gap(self, profile: Profile, opportunity: Opportunity) -> Dict[str, Any]:
        """Analyze the skill gap between a user profile and an opportunity.
        
        Args:
            profile: User profile
            opportunity: Opportunity to analyze against
            
        Returns:
            Dictionary containing analysis results
        """
        # Parse JSON fields
        user_skills = set([s.strip().lower() for s in (json.loads(profile.skills) if isinstance(profile.skills, str) else profile.skills)])
        user_interests = set([i.strip().lower() for i in (json.loads(profile.interests) if isinstance(profile.interests, str) else profile.interests)])
        
        opp_skills = set([s.strip().lower() for s in (json.loads(opportunity.required_skills) if isinstance(opportunity.required_skills, str) else opportunity.required_skills)])
        opp_tags = set([t.strip().lower() for t in (json.loads(opportunity.tags) if isinstance(opportunity.tags, str) else opportunity.tags)])
        
        # Combine user background
        user_portfolio = user_skills.union(user_interests)
        
        if not opp_skills and not opp_tags:
            return {
                "is_ready": True,
                "matching_skills": list(user_skills)[:3],
                "missing_skills": [],
                "recommendation_text": "This opportunity has no specific required skills listed. You are good to go!"
            }
            
        # Prioritize checking explicitly required skills, fallback to tags if empty
        requirements_to_check = opp_skills if opp_skills else opp_tags
        
        matching = requirements_to_check.intersection(user_portfolio)
        missing = requirements_to_check.difference(user_portfolio)
        
        # Calculate readiness threshold
        match_ratio = len(matching) / len(requirements_to_check) if requirements_to_check else 1.0
        is_ready = match_ratio >= 0.5  # If they have 50% or more of the requirements
        
        # Generate dynamic text
        if is_ready:
            if missing:
                text = f"You are a strong candidate! You have solid experience in items like {list(matching)[0].title()}. You might want to brush up on {list(missing)[0].title()}, but you have what it takes."
            else:
                text = "Perfect match! Your skills align directly with what this opportunity is looking for."
        else:
            if matching:
                text = f"You have some relevant background in {list(matching)[0].title()}, but this requires knowledge of {list(missing)[0].title()} you might not have yet. A great learning opportunity!"
            else:
                text = "This opportunity focuses on areas outside your current profile, specifically and heavily demanding " + (list(missing)[0].title() if missing else "new skills") + ". Consider teaming up with someone who has complementary skills!"
                
        return {
            "is_ready": is_ready,
            "matching_skills": [m.title() for m in list(matching)],
            "missing_skills": [m.title() for m in list(missing)],
            "recommendation_text": text
        }

    def generate_project_ideas(self, profile: Profile, opportunity: Opportunity) -> List[Dict[str, str]]:
        """Generate heuristic-based project ideas blending user skills and hackathon tags.
        
        Args:
            profile: User profile
            opportunity: Target opportunity
            
        Returns:
            List of project idea objects containing title and description
        """
        import random
        # Extract lowercased list of skills and tags
        user_skills = [s.strip() for s in (json.loads(profile.skills) if isinstance(profile.skills, str) else profile.skills) if s.strip()]
        opp_tags = [t.strip() for t in (json.loads(opportunity.tags) if isinstance(opportunity.tags, str) else opportunity.tags) if t.strip()]
        
        # Fallbacks if lists are empty
        if not user_skills:
            user_skills = ["Software Development", "Data Analysis", "Design"]
        if not opp_tags:
            opp_tags = [opportunity.type.replace('_', ' '), "Community", "Innovation"]
            
        ideas = []
        
        # Idea 1: The "AI / Core Tech" Social Good
        skill_1 = random.choice(user_skills)
        tag_1 = random.choice(opp_tags)
        ideas.append({
            "title": f"The {tag_1.title()} Engine",
            "description": f"An intelligent platform that solves the core problem of '{tag_1}' by heavily utilizing your expertise in {skill_1}. Focus on building a seamless user experience that democratizes access."
        })
        
        # Idea 2: Gamified approach
        skill_2 = random.choice(user_skills)
        tag_2 = random.choice(opp_tags)
        ideas.append({
            "title": f"{tag_2.title()}Quest",
            "description": f"A gamified mobile-first approach to {tag_2} engagement. By integrating {skill_2} as the backbone, the project encourages daily user streaks and community leaderboards."
        })
        
        # Idea 3: The Productivity / Analytics Dashboard
        skill_3 = random.choice(user_skills)
        tag_3 = random.choice(opp_tags)
        ideas.append({
            "title": f"Insight {tag_3.title()}",
            "description": f"A technical dashboard to track and optimize {tag_3} workflows. Built entirely around {skill_3}, this tool gives administrators a holistic view of process efficiency."
        })
        
        return ideas


