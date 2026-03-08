import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.intelligence import PitchBlueprint, ScoutAnalysis, SquadBlueprint
from models.team import Team
from models.opportunity import Opportunity
from services.nlp.extractors import LLMExtractor, LocalLLMExtractor

class PitchStudioService:
    """Service to generate high-stakes pitch assets for teams."""
    
    def __init__(self, db: Session, extractor: Optional[LLMExtractor] = None):
        self.db = db
        self.extractor = extractor or LocalLLMExtractor()

    def generate_pitch_assets(self, team_id: str) -> PitchBlueprint:
        """Generates elevator pitch, demo script, and slide blueprint."""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")

        opportunity = self.db.query(Opportunity).filter(Opportunity.id == team.opportunity_id).first()
        scout = self.db.query(ScoutAnalysis).filter(ScoutAnalysis.opportunity_id == team.opportunity_id).first()
        blueprint = self.db.query(SquadBlueprint).filter(SquadBlueprint.team_id == team_id).first()

        # Synthesis core context
        # We combine what the scouts found (winners) with what the team is actually building (blueprint)
        context = {
            "team_name": team.name,
            "project_focus": team.description,
            "winning_criteria": scout.winning_criteria if scout else "General technical excellence",
            "strategic_advice": scout.strategic_advice if scout else "Focus on clarity and demo functionality",
            "tech_stack": blueprint.suggested_skeleton if blueprint else "Standard modern stack"
        }

        # 1. Generate using LLM
        assets = self._generate_assets_via_llm(context)

        # 2. Store and return
        pitch = self.db.query(PitchBlueprint).filter(PitchBlueprint.team_id == team_id).first()
        if not pitch:
            pitch = PitchBlueprint(team_id=team_id)
            self.db.add(pitch)

        pitch.elevator_pitch = assets.get("elevator_pitch")
        pitch.demo_script = assets.get("demo_script")
        pitch.slide_blueprint = assets.get("slide_blueprint")

        self.db.commit()
        return pitch

    def _generate_assets_via_llm(self, context: Dict) -> Dict:
        """Use AI to craft the perfect pitch assets."""
        # Simulated high-quality AI output
        elevator_pitch = f"Hi, we're {context['team_name']}. We saw that judges here value {context['winning_criteria']}, so we built {context['project_focus']}. Using {context['tech_stack']}, we've solved the core bottleneck by focusing on {context['strategic_advice']}."
        
        demo_script = f"""
        [Start Demo - 0:00]
        - Intro: Start with the problem. 'Did you know that...'
        - Solution: 'That's why we built this app.'
        [Feature Walkthrough - 0:45]
        - Focus on the technical implementation of our AI logic.
        [The 'Aha' Moment - 2:00]
        - Show how we incorporated the judge's favorite features.
        [Closing - 2:45]
        - Reiterate scalability and future impact.
        """

        slide_blueprint = [
            {"title": "The Hook", "content": "Visualizing the massive inefficiency we are solving.", "visual_tip": "Use a dramatic, low-poly chart showing 40% loss."},
            {"title": "Our Secret Sauce", "content": "How our architecture uses the sponsor's API in a novel way.", "visual_tip": "High-level architecture diagram with blinking 'AI' nodes."},
            {"title": "Live Demo Highlights", "content": "Screen recording of the vector search in action.", "visual_tip": "Full-screen cinematic video clips."},
            {"title": "The Team & Future", "content": "Why we are the ones to execute this.", "visual_tip": "Clean grid of team photos and a roadmap icon."}
        ]

        return {
            "elevator_pitch": elevator_pitch,
            "demo_script": demo_script,
            "slide_blueprint": slide_blueprint
        }
