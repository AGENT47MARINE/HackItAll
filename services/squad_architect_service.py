import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.intelligence import SquadBlueprint
from models.team import Team
from models.opportunity import Opportunity
from services.nlp.extractors import LLMExtractor, LocalLLMExtractor

class SquadArchitectService:
    """Service to generate a 48-hour strategic sprint roadmap for teams."""
    
    def __init__(self, db: Session, extractor: Optional[LLMExtractor] = None):
        self.db = db
        self.extractor = extractor or LocalLLMExtractor()

    def generate_blueprint(self, team_id: str) -> SquadBlueprint:
        """Generates a custom sprint roadmap and role assignments for a team."""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")

        opportunity = self.db.query(Opportunity).filter(Opportunity.id == team.opportunity_id).first()
        if not opportunity:
            raise ValueError("Opportunity not found")

        # 1. Gather team skills
        team_members = team.members
        member_profiles = []
        for member in team_members:
            profile = member.user.profile
            if profile:
                member_profiles.append({
                    "name": member.user.username,
                    "skills": profile.skills_list
                })

        # 2. Synthesize blueprints using LLM
        blueprint_data = self._synthesize_blueprint(member_profiles, opportunity)

        # 3. Store and return
        blueprint = self.db.query(SquadBlueprint).filter(SquadBlueprint.team_id == team_id).first()
        if not blueprint:
            blueprint = SquadBlueprint(team_id=team_id)
            self.db.add(blueprint)

        blueprint.roadmap = blueprint_data.get("roadmap")
        blueprint.suggested_skeleton = blueprint_data.get("suggested_skeleton")
        blueprint.role_assignments = blueprint_data.get("role_assignments")

        self.db.commit()
        return blueprint

    def _synthesize_blueprint(self, members: List[Dict], opportunity: Opportunity) -> Dict:
        """Use AI to design a 48-hour strategy based on skills and opportunity."""
        # Simulated AI output
        roadmap = [
            {"time": "0h - 4h", "task": "Project Ideation & Tech Stack lock-in", "milestone": "Brainstorming doc ready"},
            {"time": "5h - 12h", "task": "Backend API Scaffolding & Database Schema", "milestone": "Basic CRUD functional"},
            {"time": "13h - 24h", "task": "Core Feature implementation (AI integration)", "milestone": "Main logic working"},
            {"time": "25h - 36h", "task": "Frontend UI & Integration", "milestone": "End-to-end flow ready"},
            {"time": "37h - 44h", "task": "Polishing, Bug fixing, and Demo recording", "milestone": "Golden flow stable"},
            {"time": "45h - 48h", "task": "Final Submission & Documentation", "milestone": "Submitted!"}
        ]
        
        roles = {}
        for member in members:
            name = member["name"]
            skills = str(member["skills"]).lower()
            if "python" in skills or "api" in skills or "sql" in skills:
                roles[name] = "Backend & Data Architect"
            elif "react" in skills or "ui" in skills or "css" in skills:
                roles[name] = "Lead UI Engineer"
            else:
                roles[name] = "Full Stack / Product Manager"

        skeleton_suggestion = f"""# Suggested Tech Stack for {opportunity.title}
- **Frontend**: Vite + React + Tailwind CSS (Glassmorphic)
- **Backend**: Python FastAPI (matches Team skill set)
- **DB**: PostgreSQL (via Supabase or Local)
- **AI**: Bedrock Claude 3.5 Sonnet for content analysis
"""

        return {
            "roadmap": roadmap,
            "role_assignments": roles,
            "suggested_skeleton": skeleton_suggestion
        }
