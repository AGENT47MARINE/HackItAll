"""Service for matching users to teams based on skill gaps."""
import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy import func

from models.user import User, Profile
from models.team import Team, TeamMember
from models.opportunity import Opportunity

class TeamMatchmakerService:
    """Service for AI-powered team matchmaking and skill gap analysis."""

    def __init__(self, db_session: Session):
        self.db = db_session

    def get_team_skill_gap(self, team_id: int) -> List[str]:
        """Analyze a team's current collective skills vs needed skills.
        
        Returns:
            List of skills that are still missing (the 'Gap').
        """
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            return []

        # Get needed skills (JSON list)
        needed_skills = []
        if team.needed_skills:
            try:
                needed_skills = json.loads(team.needed_skills)
                if not isinstance(needed_skills, list):
                    needed_skills = [needed_skills]
            except:
                needed_skills = [s.strip() for s in team.needed_skills.split(",")]

        # Aggregate current member skills
        members = self.db.query(TeamMember).filter(TeamMember.team_id == team_id).all()
        current_skills = set()
        for member in members:
            profile = self.db.query(Profile).filter(Profile.user_id == member.user_id).first()
            if profile:
                try:
                    m_skills = json.loads(profile.skills)
                    current_skills.update([s.lower() for s in m_skills])
                except:
                    pass

        # Identify gaps
        gap = [s for s in needed_skills if s.lower() not in current_skills]
        return gap

    def recommend_members_for_team(self, team_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """Find solo users who fill the team's skill gap.
        
        Args:
            team_id: Team ID
            limit: Max recommendations
            
        Returns:
            List of recommended users with their match score.
        """
        gap = self.get_team_skill_gap(team_id)
        if not gap:
            return []

        # Find all solo users (not in any team for this opportunity)
        team = self.db.query(Team).filter(Team.id == team_id).first()
        opportunity_id = team.opportunity_id
        
        # Get users already in a team for this opportunity
        busy_user_ids = self.db.query(TeamMember.user_id).join(Team).filter(
            Team.opportunity_id == opportunity_id
        ).all()
        busy_user_ids = [u[0] for u in busy_user_ids]

        # Query solo profiles
        potential_matches = self.db.query(User, Profile).join(Profile).filter(
            User.id.notin_(busy_user_ids)
        ).all()

        recommendations = []
        gap_set = set([s.lower() for s in gap])

        for user, profile in potential_matches:
            try:
                user_skills = set([s.lower() for s in json.loads(profile.skills)])
                matching_skills = gap_set.intersection(user_skills)
                
                if matching_skills:
                    score = len(matching_skills) / len(gap_set)
                    recommendations.append({
                        "user_id": user.id,
                        "username": user.username,
                        "email": user.email,
                        "matching_skills": list(matching_skills),
                        "score": round(score, 2)
                    })
            except:
                continue

        # Sort by score descending
        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]

    def recommend_teams_for_user(self, user_id: str, opportunity_id: int = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Find teams that are 'Missing You' (you fill their skill gaps).
        
        Args:
            user_id: User ID
            opportunity_id: Optional filter for specific hackathon
            limit: Max recommendations
            
        Returns:
            List of recommended teams with match details.
        """
        profile = self.db.query(Profile).filter(Profile.user_id == user_id).first()
        if not profile:
            return []

        try:
            user_skills = set([s.lower() for s in json.loads(profile.skills)])
        except:
            return []

        # Query active teams
        query = self.db.query(Team).filter(Team.is_active == True)
        if opportunity_id:
            query = query.filter(Team.opportunity_id == opportunity_id)
        
        teams = query.all()
        recommendations = []

        for team in teams:
            # Check if user is already in this team
            is_member = self.db.query(TeamMember).filter(
                TeamMember.team_id == team.id,
                TeamMember.user_id == user_id
            ).first()
            if is_member:
                continue

            gap = self.get_team_skill_gap(team.id)
            if not gap:
                continue

            gap_set = set([s.lower() for s in gap])
            matching_skills = user_skills.intersection(gap_set)

            if matching_skills:
                score = len(matching_skills) / len(gap_set)
                recommendations.append({
                    "team_id": team.id,
                    "team_name": team.name,
                    "opportunity_id": team.opportunity_id,
                    "matching_skills": list(matching_skills),
                    "missing_skills": [s for s in gap if s.lower() not in matching_skills],
                    "score": round(score, 2)
                })

        recommendations.sort(key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]
