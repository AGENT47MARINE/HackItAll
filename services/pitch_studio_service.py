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
        prompt = f"""
        Craft a world-class hackathon pitch for the team '{context['team_name']}'.
        They are building: {context['project_focus']}
        Tech Stack: {context['tech_stack']}
        Strategic Advice from Scouts: {context['strategic_advice']}
        
        JUDGING CRITERIA:
        {context['winning_criteria']}
        
        TASK:
        1. elevator_pitch (ONE POWERFUL SENTENCE)
        2. demo_script (3-minute minute-by-minute workflow)
        3. slide_blueprint (List of objects with 'title', 'content', 'visual_tip')
        
        Ensure the script highlights the 'Aha!' moment using judge persona preferences.
        Return ONLY valid JSON.
        """
        
        try:
            result = self.extractor.generic_extract(prompt)
            if result and "elevator_pitch" in result:
                return result
        except Exception as e:
            print(f"LLM Pitch Generation failed: {e}")

        # Fallback to high-quality template strategy if LLM is offline
        return {
            "elevator_pitch": f"We're {context['team_name']}, leveraging {context['tech_stack']} to build {context['project_focus']}. We solve the core judge concern about {context['winning_criteria']} by implementing a focus on {context['strategic_advice']}.",
            "demo_script": "[Start: 0:00] Problem statement. [Core Feature: 1:00] Live demo of the main value. [Tech Highlight: 2:00] Showcase our tech stack. [Closing: 2:45] Impact and future.",
            "slide_blueprint": [
                {"title": "The Big One", "content": "Visualizing the solution in action.", "visual_tip": "Cinematic video reel."}
            ]
        }
