import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.intelligence import AuditReport, ScoutAnalysis
from models.team import Team
from models.opportunity import Opportunity
from services.nlp.extractors import LLMExtractor, LocalLLMExtractor

class AIJudgeService:
    """Service to audit submissions and predict winning potential."""
    
    def __init__(self, db: Session, extractor: Optional[LLMExtractor] = None):
        self.db = db
        self.extractor = extractor or LocalLLMExtractor()

    def audit_submission(self, team_id: str, submission_data: Dict) -> AuditReport:
        """Audits a draft submission against weighted hackathon criteria."""
        team = self.db.query(Team).filter(Team.id == team_id).first()
        if not team:
            raise ValueError("Team not found")

        opportunity = self.db.query(Opportunity).filter(Opportunity.id == team.opportunity_id).first()
        scout = self.db.query(ScoutAnalysis).filter(ScoutAnalysis.opportunity_id == team.opportunity_id).first()

        # Synthesis core context
        # The AI Judge mimics a judge's persona found by the scout
        context = {
            "submission_title": submission_data.get("title", "Untitled"),
            "submission_desc": submission_data.get("description", ""),
            "github_url": submission_data.get("github_url", ""),
            "winning_criteria": scout.winning_criteria if scout else "General technical excellence",
        }

        # 1. Run Audit via LLM
        audit_results = self._run_llm_audit(context)

        # 2. Store and return
        report = self.db.query(AuditReport).filter(AuditReport.team_id == team_id).first()
        if not report:
            report = AuditReport(team_id=team_id)
            self.db.add(report)

        report.winning_probability = audit_results.get("winning_probability")
        report.red_flags = audit_results.get("red_flags")
        report.improvements = audit_results.get("improvements")
        report.judge_persona_feedback = audit_results.get("judge_persona_feedback")

        self.db.commit()
        return report

    def _run_llm_audit(self, context: Dict) -> Dict:
        """mimic a judge's appraisal of the work."""
        # Simulated high-quality AI audit
        return {
            "winning_probability": 0.82,
            "red_flags": [
                "Technical description is slightly too jargon-heavy for the 'Business Value' track judges.",
                "Missing clear mention of the sponsor's specific API feature (Bedrock Nova) in the readme."
            ],
            "improvements": [
                "Rewrite the first paragraph of your description to focus on the 'User Impact' rather than the 'Architecture'.",
                "Add a 15-second screen recording showing the AI inference speed—judges here value performance."
            ],
            "judge_persona_feedback": "As a Senior Engineer at a Cloud company (likely judge persona), I appreciate the modularity, but I'm looking for a more distinct 'Aha' moment in the demo. The current description is solid but safe."
        }
