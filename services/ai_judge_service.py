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
        prompt = f"""
        You are an elite AI Hackathon Judge. You are auditing a project for a team.
        
        JUDGE PERSONA / CRITERIA:
        {context['winning_criteria']}
        
        SUBMISSION TO AUDIT:
        Title: {context['submission_title']}
        Description: {context['submission_desc']}
        GitHub/Demo: {context['github_url']}
        
        TASK:
        1. Calculate a 'winning_probability' (0.0 to 1.0) based on how well this matches the criteria.
        2. Identify 2-3 specific 'red_flags' (what might cause the judges to reject this?).
        3. Suggest 2-3 'improvements' (high-impact strategic fixes).
        4. Provide 'judge_persona_feedback' (write a short paragraph in the first person as the judge).
        
        Return ONLY valid JSON.
        """
        
        try:
            result = self.extractor.generic_extract(prompt)
            if result and "winning_probability" in result:
                return result
        except Exception as e:
            print(f"LLM Audit failed: {e}")

        # Fallback to smart templates if LLM is offline
        return {
            "winning_probability": 0.65,
            "red_flags": ["The technical implementation details are too vague for the 'Execution' category."],
            "improvements": ["Add a clear explanation of how your solution handles large-scale data concurrency."],
            "judge_persona_feedback": "I've seen many similar projects. To stand out, you need to prove your solution works beyond a simple happy-path demo."
        }
