"""Recommendation service for generating personalized opportunity recommendations."""
import json
import logging
from typing import Dict, Any, List, Tuple
from datetime import datetime
from sqlalchemy.orm import Session

from models.user import Profile
from models.opportunity import Opportunity

# Configure performance logging
perf_logger = logging.getLogger('recommendation_performance')
perf_logger.setLevel(logging.INFO)
if not perf_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('[%(asctime)s] PERF - %(message)s')
    handler.setFormatter(formatter)
    perf_logger.addHandler(handler)


class RecommendationEngine:
    """Service for generating personalized opportunity recommendations."""

    def __init__(self, db_session: Session, cache_client=None):
        """Initialize the recommendation engine.

        Args:
            db_session: SQLAlchemy database session
            cache_client: Optional Redis client for caching
        """
        self.db = db_session
        self.cache_ttl = 3600  # 1 hour TTL in seconds
        
        # Redis setup
        import redis
        from config import config
        try:
            self.redis_client = cache_client or redis.from_url(config.REDIS_URL, decode_responses=True)
            # Test connection
            self.redis_client.ping()
        except Exception as e:
            print(f"Warning: Redis connection failed, falling back to no cache: {e}")
            self.redis_client = None

    def generate_recommendations(self, user_id: str, limit: int = 10) -> List[Tuple[Opportunity, float]]:
            """Generate personalized recommendations for a user.

            This method uses optimized database queries with JOIN operations and database-level
            filtering to efficiently fetch and score opportunities. Results are cached in Redis
            for improved performance on subsequent requests.

            Args:
                user_id: User ID to generate recommendations for
                limit: Maximum number of recommendations to return (default: 10)

            Returns:
                List of tuples containing (Opportunity, score) sorted by score descending
            """
            import time
            start_time = time.time()

            # Get user profile first for cache key generation
            from models.user import Profile
            profile = self.db.query(Profile).filter(Profile.user_id == user_id).first()
            if not profile:
                return []

            # Generate cache key based on user profile hash and preferences
            cache_key = self._generate_cache_key(user_id, profile, limit)

            # Check Redis cache first with improved monitoring
            if self.redis_client:
                try:
                    cached_data_str = self.redis_client.get(cache_key)
                    if cached_data_str:
                        cached_data = json.loads(cached_data_str)
                        # Use JOIN query to fetch all opportunities at once instead of individual queries
                        opportunity_ids = [item['id'] for item in cached_data]
                        if opportunity_ids:
                            opportunities_dict = {}
                            opportunities = self.db.query(Opportunity).filter(
                                Opportunity.id.in_(opportunity_ids)
                            ).all()
                            for opp in opportunities:
                                opportunities_dict[opp.id] = opp

                            result = []
                            for item in cached_data:
                                opp = opportunities_dict.get(item['id'])
                                if opp:
                                    result.append((opp, item['score']))
                            if result:
                                query_time = time.time() - start_time
                                self._log_cache_hit(user_id, len(result), query_time)
                                return result
                    else:
                        self._log_cache_miss(user_id, "no_cached_data")
                except Exception as e:
                    self._log_cache_miss(user_id, f"redis_error: {e}")
                    print(f"Warning: Redis read failed: {e}")
            else:
                self._log_cache_miss(user_id, "redis_unavailable")

            # Parse user preferences for database filtering
            user_interests = set([i.strip().lower() for i in (json.loads(profile.interests) if isinstance(profile.interests, str) else [])])
            user_skills = set([s.strip().lower() for s in (json.loads(profile.skills) if isinstance(profile.skills, str) else [])])
            user_education = profile.education_level.strip().lower() if profile.education_level else ""

            # Get user's participation history with optimized query
            participation_history = self._get_participation_history(user_id)

            # Build optimized query with database-level filtering
            query = self.db.query(Opportunity).filter(
                Opportunity.status == "active"
            )

            # Filter out expired opportunities at database level
            from datetime import datetime
            query = query.filter(Opportunity.deadline > datetime.utcnow())

            # Add education-level filtering at database level where possible
            if user_education:
                # Only include opportunities that don't have strict education requirements
                # or that match the user's education level
                if "high school" in user_education:
                    # High school users can only access high school opportunities
                    query = query.filter(
                        (Opportunity.eligibility.is_(None)) |
                        (Opportunity.eligibility.ilike('%high school%'))
                    )
                elif any(level in user_education for level in ["b.tech", "undergraduate"]):
                    # Undergraduate users can access high school, undergraduate, and general student opportunities
                    query = query.filter(
                        (Opportunity.eligibility.is_(None)) |
                        (Opportunity.eligibility.ilike('%high school%')) |
                        (Opportunity.eligibility.ilike('%b.tech%')) |
                        (Opportunity.eligibility.ilike('%undergraduate%')) |
                        (Opportunity.eligibility.ilike('%all students%')) |
                        (Opportunity.eligibility.ilike('%everyone%')) |
                        (Opportunity.eligibility.ilike('%any%'))
                    )
                # Graduate users can access all opportunities (including student-specific ones)
                elif any(level in user_education for level in ["graduate", "m.tech", "alumni"]):
                    pass # Keep full access

            # Add interest-based filtering at database level for better performance
            # Only load opportunities that have at least one matching tag or skill
            if user_interests or user_skills:
                # Create OR conditions for each user interest and skill
                filter_conditions = []
                
                for interest in user_interests:
                    filter_conditions.append(Opportunity.tags.ilike(f'%{interest}%'))
                
                for skill in user_skills:
                    filter_conditions.append(Opportunity.required_skills.ilike(f'%{skill}%'))
                    filter_conditions.append(Opportunity.tags.ilike(f'%{skill}%'))
                
                # Apply OR filter to only get potentially matching opportunities
                if filter_conditions:
                    from sqlalchemy import or_
                    query = query.filter(or_(*filter_conditions))

            # Limit the initial query to reduce memory usage and improve performance
            # We'll get more than we need and score them, then take the top results
            query = query.limit(min(500, limit * 20))  # Get at most 500 or 20x the requested limit

            # Execute optimized query
            opportunities = query.all()
            
            perf_logger.info(f"Database query returned {len(opportunities)} pre-filtered opportunities")

            # Score opportunities efficiently with new normalization system
            scored_opportunities = []
            for opportunity in opportunities:
                score = self.calculate_relevance_score(profile, opportunity, participation_history)
                # Only include opportunities that are eligible (score is not None)
                if score is not None:
                    scored_opportunities.append((opportunity, score))

            # Sort by score in descending order
            scored_opportunities.sort(key=lambda x: x[1], reverse=True)

            # Limit results
            result = scored_opportunities[:limit]

            # Cache the result to Redis with improved serialization and monitoring
            if self.redis_client:
                try:
                    # Cache only IDs and scores for efficiency
                    serialized_results = [{'id': opp.id, 'score': score} for opp, score in result]
                    self.redis_client.setex(
                        cache_key,
                        self.cache_ttl,
                        json.dumps(serialized_results)
                    )
                    self._log_cache_write(user_id, len(result))
                except Exception as e:
                    print(f"Warning: Failed to write to Redis cache: {e}")

            # Log performance metrics
            query_time = time.time() - start_time
            self._log_cache_miss_with_generation(user_id, len(result), query_time)
            perf_logger.info(f"Generated {len(result)} recommendations from {len(opportunities)} pre-filtered opportunities in {query_time:.3f}s (DB optimized)")
            print(f"[PERF] Generated {len(result)} recommendations from {len(opportunities)} pre-filtered opportunities in {query_time:.3f}s")

            return result



    def _get_participation_history(self, user_id: str) -> List[Dict[str, Any]]:
        """Get user's participation history with optimized JOIN query.

        Args:
            user_id: User ID

        Returns:
            List of participation history entries with opportunity type and status
        """
        try:
            from models.tracking import ParticipationHistory
            
            # Use JOIN query to get participation history with opportunity details in one query
            # This avoids the N+1 query problem in the original implementation
            from sqlalchemy.orm import joinedload
            
            history_entries = self.db.query(ParticipationHistory).options(
                joinedload(ParticipationHistory.opportunity)
            ).filter(
                ParticipationHistory.user_id == user_id
            ).all()

            # Convert to dict format expected by calculate_relevance_score
            result = []
            for entry in history_entries:
                if entry.opportunity:
                    result.append({
                        'opportunity_type': entry.opportunity.type,
                        'status': entry.status
                    })
            return result
            
        except ImportError:
            # ParticipationHistory model not yet implemented
            return []
        except Exception as e:
            # Handle any other database errors gracefully
            print(f"Warning: Failed to load participation history: {e}")
            return []

    def calculate_relevance_score(self, profile: Profile, opportunity: Opportunity,
                                      participation_history: List[Dict[str, Any]] = None) -> float:
            """Calculate normalized relevance score for a user-opportunity pair.

            New Weighted Scoring Algorithm:
            1. Eligibility Filter (Hard Check): Filter out ineligible opportunities (return None)
            2. Interest Matching (Weight: 40%): Semantic matching with strength consideration
            3. Skills Matching (Weight: 30%): Required skills vs user skills with proficiency
            4. Location Preference (Weight: 15%): Distance/format preference matching
            5. User Behavior (Weight: 10%): Past participation patterns and preferences
            6. Opportunity Quality (Weight: 5%): Popularity, success rate, recency

            Returns normalized score in 0-100% range using min-max scaling.

            Args:
                profile: User profile
                opportunity: Opportunity to score
                participation_history: List of user's past participation entries (optional)

            Returns:
                Normalized relevance score (0.0-1.0) or None if ineligible
            """
            import datetime
            import re
            from collections import Counter

            # Parse JSON fields securely
            user_interests = set([i.strip().lower() for i in (json.loads(profile.interests) if isinstance(profile.interests, str) else profile.interests or [])])
            user_skills = set([s.strip().lower() for s in (json.loads(profile.skills) if isinstance(profile.skills, str) else profile.skills or [])])
            opp_tags = set([t.strip().lower() for t in (json.loads(opportunity.tags) if isinstance(opportunity.tags, str) else opportunity.tags or [])])
            opp_required_skills = set([s.strip().lower() for s in (json.loads(opportunity.required_skills) if isinstance(opportunity.required_skills, str) else opportunity.required_skills or [])])

            # 1. Eligibility Filter (Hard Check) - Return None for ineligible
            if opportunity.eligibility:
                opp_elig = opportunity.eligibility.strip().lower()
                prof_elig = profile.education_level.strip().lower() if profile.education_level else ""

                # Simple exclusionary logic for basic levels
                if "high school" in opp_elig and "high school" not in prof_elig:
                    return None  # Filter out instead of negative score
                if "graduate" in opp_elig and not any(x in prof_elig for x in ["graduate", "m.tech", "alumni"]):
                    return None
                if "b.tech" in opp_elig and not any(x in prof_elig for x in ["b.tech", "undergraduate"]):
                    return None

            # Check for expired opportunities
            if opportunity.deadline and opportunity.deadline < datetime.datetime.utcnow():
                return None  # Filter out expired opportunities

            # Initialize component scores
            interest_score = 0.0
            skills_score = 0.0
            location_score = 0.0
            behavior_score = 0.0
            quality_score = 0.0

            # 2. Interest Matching (Weight: 40%) - Enhanced semantic matching
            if user_interests and opp_tags:
                # Direct matches
                direct_matches = user_interests.intersection(opp_tags)
                interest_score += len(direct_matches) * 0.8

                # Semantic/partial matches (e.g., "web dev" matches "web development")
                semantic_matches = 0
                for user_interest in user_interests:
                    for opp_tag in opp_tags:
                        if user_interest != opp_tag:  # Avoid double counting direct matches
                            # Check for partial word matches
                            user_words = set(user_interest.split())
                            opp_words = set(opp_tag.split())
                            if user_words.intersection(opp_words):
                                semantic_matches += 0.4
                            # Check for substring matches
                            elif user_interest in opp_tag or opp_tag in user_interest:
                                semantic_matches += 0.3

                interest_score += semantic_matches
                # Normalize to 0-1 range (assume max 5 strong matches)
                interest_score = min(interest_score / 5.0, 1.0)

            # 3. Skills Matching (Weight: 30%) - Required skills vs user skills
            if opp_required_skills:
                if user_skills:
                    # Direct skill matches
                    skill_matches = user_skills.intersection(opp_required_skills)
                    skills_score += len(skill_matches) * 0.7

                    # Partial skill matches (e.g., "python" matches "python programming")
                    partial_matches = 0
                    for user_skill in user_skills:
                        for req_skill in opp_required_skills:
                            if user_skill != req_skill:
                                if user_skill in req_skill or req_skill in user_skill:
                                    partial_matches += 0.4

                    skills_score += partial_matches
                    # Normalize based on number of required skills
                    skills_score = min(skills_score / max(len(opp_required_skills), 1), 1.0)
                else:
                    # Penalize if opportunity requires skills but user has none listed
                    skills_score = 0.2
            else:
                # No specific skills required - neutral score
                skills_score = 0.6

            # 4. Location Preference (Weight: 15%) - Format and location matching
            loc_type = (opportunity.location_type or "").strip().lower()
            user_location = getattr(profile, 'location', '')
            if not user_location and profile.user:
                user_location = getattr(profile.user, 'location', '')
            user_location = (user_location or "").strip().lower()

            # Format preference scoring
            if "online" in loc_type or "hybrid" in loc_type:
                location_score += 0.8  # Most flexible
            elif "remote" in loc_type:
                location_score += 0.7
            else:
                # In-person events - check location proximity
                if user_location and opportunity.location:
                    opp_location = opportunity.location.strip().lower()
                    # Simple location matching (can be enhanced with geolocation)
                    if user_location in opp_location or opp_location in user_location:
                        location_score += 0.6
                    else:
                        location_score += 0.3  # Different location penalty
                else:
                    location_score += 0.4  # Unknown location

            location_score = min(location_score, 1.0)

            # 5. User Behavior (Weight: 10%) - Past participation patterns
            if participation_history:
                # Analyze user's past preferences
                past_types = [entry.get('type', '').lower() for entry in participation_history]
                past_formats = [entry.get('format', '').lower() for entry in participation_history]

                # Type preference matching
                opp_type = opportunity.type.lower() if opportunity.type else ""
                if opp_type in past_types:
                    behavior_score += 0.6

                # Format preference matching
                if loc_type:
                    format_matches = sum(1 for fmt in past_formats if fmt in loc_type or loc_type in fmt)
                    if format_matches > 0:
                        behavior_score += 0.4

                # Activity level bonus (more active users get slight boost)
                if len(participation_history) >= 5:
                    behavior_score += 0.2
                elif len(participation_history) >= 2:
                    behavior_score += 0.1
            else:
                # New users get neutral score
                behavior_score = 0.5

            behavior_score = min(behavior_score, 1.0)

            # 6. Opportunity Quality (Weight: 5%) - Recency and urgency
            if opportunity.deadline:
                days_until = (opportunity.deadline - datetime.datetime.utcnow()).days
                if 0 <= days_until <= 7:
                    quality_score += 0.9  # Very urgent
                elif 0 <= days_until <= 14:
                    quality_score += 0.7  # Moderately urgent
                elif 0 <= days_until <= 30:
                    quality_score += 0.5  # Some urgency
                else:
                    quality_score += 0.3  # Distant deadline
            else:
                quality_score = 0.4  # No deadline specified

            # Add recency bonus (newer opportunities might be more relevant)
            if hasattr(opportunity, 'created_at') and opportunity.created_at:
                days_since_created = (datetime.datetime.utcnow() - opportunity.created_at).days
                if days_since_created <= 7:
                    quality_score += 0.1

            quality_score = min(quality_score, 1.0)

            # Calculate weighted final score
            weights = {
                'interest': 0.40,
                'skills': 0.30,
                'location': 0.15,
                'behavior': 0.10,
                'quality': 0.05
            }

            final_score = (
                interest_score * weights['interest'] +
                skills_score * weights['skills'] +
                location_score * weights['location'] +
                behavior_score * weights['behavior'] +
                quality_score * weights['quality']
            )

            # Ensure score is in 0-1 range (already normalized by component, but safety check)
            final_score = max(0.0, min(1.0, final_score))

            return final_score


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

    def _generate_cache_key(self, user_id: str, profile: 'Profile', limit: int) -> str:
        """Generate a unique cache key based on user profile and preferences.

        The cache key includes a hash of the user's profile data to ensure
        that cache is invalidated when user preferences change.

        Args:
            user_id: User ID
            profile: User profile object
            limit: Number of recommendations requested

        Returns:
            Unique cache key string
        """
        import hashlib

        # Create profile hash from key attributes that affect recommendations
        profile_data = {
            'interests': profile.interests if isinstance(profile.interests, str) else json.dumps(profile.interests or []),
            'skills': profile.skills if isinstance(profile.skills, str) else json.dumps(profile.skills or []),
            'education_level': profile.education_level or '',
            'updated_at': profile.updated_at.isoformat() if hasattr(profile, 'updated_at') and profile.updated_at else ''
        }

        # Create hash of profile data
        profile_json = json.dumps(profile_data, sort_keys=True)
        profile_hash = hashlib.md5(profile_json.encode()).hexdigest()[:8]

        return f"rec_v2_{user_id}_{profile_hash}_{limit}"

    def invalidate_user_cache(self, user_id: str) -> bool:
        """Invalidate all cached recommendations for a user.

        This should be called when user profile or preferences change.

        Args:
            user_id: User ID whose cache should be invalidated

        Returns:
            True if cache was successfully invalidated, False otherwise
        """
        if not self.redis_client:
            return False

        try:
            # Find all cache keys for this user using pattern matching
            pattern = f"rec_v2_{user_id}_*"
            keys = self.redis_client.keys(pattern)

            if keys:
                deleted_count = self.redis_client.delete(*keys)
                perf_logger.info(f"Cache invalidation - Deleted {deleted_count} cache entries for user {user_id}")
                print(f"[CACHE] Invalidated {deleted_count} cache entries for user {user_id}")
                return True
            else:
                perf_logger.info(f"Cache invalidation - No cache entries found for user {user_id}")
                return True

        except Exception as e:
            print(f"Warning: Failed to invalidate cache for user {user_id}: {e}")
            return False

    def _log_cache_hit(self, user_id: str, result_count: int, query_time: float):
        """Log cache hit with performance metrics."""
        perf_logger.info(f"Cache HIT - User: {user_id}, Results: {result_count}, Time: {query_time:.3f}s")
        print(f"[CACHE HIT] Retrieved {result_count} recommendations in {query_time:.3f}s")

        # Update cache hit rate metrics
        self._update_cache_metrics('hit')

    def _log_cache_miss(self, user_id: str, reason: str):
        """Log cache miss with reason."""
        perf_logger.info(f"Cache MISS - User: {user_id}, Reason: {reason}")
        print(f"[CACHE MISS] User {user_id}: {reason}")

        # Update cache hit rate metrics
        self._update_cache_metrics('miss')

    def _log_cache_miss_with_generation(self, user_id: str, result_count: int, query_time: float):
        """Log cache miss with generation time."""
        perf_logger.info(f"Cache MISS + Generation - User: {user_id}, Results: {result_count}, Time: {query_time:.3f}s")
        print(f"[CACHE MISS] Generated {result_count} recommendations in {query_time:.3f}s")

    def _log_cache_write(self, user_id: str, result_count: int):
        """Log successful cache write."""
        perf_logger.info(f"Cache WRITE - User: {user_id}, Cached {result_count} recommendations")
        print(f"[CACHE WRITE] Cached {result_count} recommendations for user {user_id}")

    def _update_cache_metrics(self, event_type: str):
        """Update cache hit/miss rate metrics in Redis.

        Args:
            event_type: 'hit' or 'miss'
        """
        if not self.redis_client:
            return

        try:
            # Use Redis counters to track hit/miss rates
            today = datetime.now().strftime('%Y-%m-%d')
            hit_key = f"cache_metrics:hits:{today}"
            miss_key = f"cache_metrics:misses:{today}"

            if event_type == 'hit':
                self.redis_client.incr(hit_key)
                self.redis_client.expire(hit_key, 86400 * 7)  # Keep for 7 days
            elif event_type == 'miss':
                self.redis_client.incr(miss_key)
                self.redis_client.expire(miss_key, 86400 * 7)  # Keep for 7 days

        except Exception as e:
            # Don't fail the main operation if metrics update fails
            print(f"Warning: Failed to update cache metrics: {e}")

    def get_cache_metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get cache hit/miss rate metrics for the specified number of days.

        Args:
            days: Number of days to retrieve metrics for (default: 7)

        Returns:
            Dictionary containing cache metrics
        """
        if not self.redis_client:
            return {'error': 'Redis not available'}

        try:
            from datetime import datetime, timedelta

            metrics = {
                'total_hits': 0,
                'total_misses': 0,
                'hit_rate': 0.0,
                'daily_metrics': []
            }

            for i in range(days):
                date = (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
                hit_key = f"cache_metrics:hits:{date}"
                miss_key = f"cache_metrics:misses:{date}"

                hits = int(self.redis_client.get(hit_key) or 0)
                misses = int(self.redis_client.get(miss_key) or 0)

                metrics['total_hits'] += hits
                metrics['total_misses'] += misses

                daily_hit_rate = hits / (hits + misses) if (hits + misses) > 0 else 0.0
                metrics['daily_metrics'].append({
                    'date': date,
                    'hits': hits,
                    'misses': misses,
                    'hit_rate': daily_hit_rate
                })

            total_requests = metrics['total_hits'] + metrics['total_misses']
            metrics['hit_rate'] = metrics['total_hits'] / total_requests if total_requests > 0 else 0.0

            return metrics

        except Exception as e:
            return {'error': f'Failed to retrieve cache metrics: {e}'}


