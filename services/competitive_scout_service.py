import json
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from models.intelligence import HistoricalProject, ScoutAnalysis
from models.opportunity import Opportunity
from services.scraper.universal import UniversalAIScraper
from services.nlp.extractors import LLMExtractor, LocalLLMExtractor

class CompetitiveScoutService:
    """Service to provide strategic 'Alpha' by analyzing past winners."""
    
    def __init__(self, db: Session, extractor: Optional[LLMExtractor] = None):
        self.db = db
        self.extractor = extractor or LocalLLMExtractor()
        self.scraper = UniversalAIScraper(extractor=self.extractor)

    def analyze_hackathon(self, opportunity_id: str) -> ScoutAnalysis:
        """Analyze a hackathon by scraping its gallery and extracting winning patterns."""
        opportunity = self.db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if not opportunity:
            raise ValueError("Opportunity not found")

        # 1. Attempt to find 'Project Gallery' or 'Winners' URL
        # We can use the source_url to guess or use the LLM to find it on the page
        gallery_url = self._find_gallery_url(opportunity)
        
        if not gallery_url:
            # Fallback: analyze based on tags/description if no gallery found
            return self._generate_lightweight_analysis(opportunity)

        # 2. Scrape past winners (Historical Projects)
        winning_projects = self._scrape_past_winners(gallery_url, opportunity.title)
        
        # 3. Use LLM to synthesize winning patterns
        analysis_data = self._synthesize_patterns(winning_projects, opportunity)
        
        # 4. Save and return analysis
        analysis = self.db.query(ScoutAnalysis).filter(ScoutAnalysis.opportunity_id == opportunity_id).first()
        if not analysis:
            analysis = ScoutAnalysis(opportunity_id=opportunity_id)
            self.db.add(analysis)
        
        analysis.winning_criteria = analysis_data.get("winning_criteria")
        analysis.suggested_tech_stack = analysis_data.get("suggested_tech_stack")
        analysis.track_difficulty = analysis_data.get("track_difficulty")
        analysis.strategic_advice = analysis_data.get("strategic_advice")
        
        self.db.commit()
        return analysis

    def _find_gallery_url(self, opportunity: Opportunity) -> Optional[str]:
        """Guesses the gallery URL based on the source platform."""
        source_url = opportunity.source_url or ""
        if "devpost.com" in source_url:
            # Devpost pattern: devpost.com/hackathons/name -> devpost.com/submissions
            if "/hackathons/" in source_url:
                base = source_url.split("?")[0].rstrip("/")
                return f"{base}/submissions"
        return None

    def _scrape_past_winners(self, gallery_url: str, event_name: str) -> List[Dict]:
        """Scrapes the submissions page to find winners."""
        try:
            # Use universal scraper to get project links
            items = self.scraper.extract(gallery_url)
            winners = [item for item in items if "winner" in str(item).lower() or "prize" in str(item).lower()]
            
            # Save to HistoricalProject table for long-term knowledge
            for winner in winners:
                existing = self.db.query(HistoricalProject).filter(HistoricalProject.title == winner.get("title")).first()
                if not existing:
                    proj = HistoricalProject(
                        title=winner.get("title", "Unknown Project"),
                        description=winner.get("description", ""),
                        domain=gallery_url.split("/")[2],
                        event_name=event_name,
                        winning_prize=winner.get("prize"),
                        tech_stack=winner.get("tech_stack", []),
                        submission_url=winner.get("application_link")
                    )
                    self.db.add(proj)
            self.db.commit()
            return winners
        except Exception as e:
            print(f"Failed to scrape winners: {e}")
            return []

    def _synthesize_patterns(self, winners: List[Dict], opportunity: Opportunity) -> Dict:
        """Use LLM to find the 'Secret Sauce' across winners."""
        prompt = f"""
        Analyze these past winning projects for the hackathon '{opportunity.title}':
        {json.dumps(winners[:5])}
        
        Based on this, provide:
        1. Winning Criteria: What do judges actually prioritize?
        2. Suggested Tech Stack: What technologies are most successful here?
        3. Strategic Advice: One specific piece of 'Alpha' advice to win.
        """
        
        # In a real scenario, this would call the LLM extractor
        # For now, we simulate the synthesis
        return {
            "winning_criteria": "Focus on high-fidelity prototypes and real-world API integrations. Judges here value technical complexity over purely visual polish.",
            "suggested_tech_stack": ["Next.js", "Python (FastAPI)", "Vector Databases", "AWS Lambda"],
            "track_difficulty": {"General": "High", "Specific Sponsor Track": "Medium"},
            "strategic_advice": "Point your AI at the sponsor's newest API documentation—they usually award prizes to teams that use their latest features first."
        }

    def _generate_lightweight_analysis(self, opportunity: Opportunity) -> ScoutAnalysis:
        """Fallback analysis using only the current opportunity data."""
        # Simple simulation
        return ScoutAnalysis(
            opportunity_id=opportunity.id,
            winning_criteria="General hackathon standards: Innovation, Technical Implementation, and Pitch quality.",
            suggested_tech_stack=[],
            track_difficulty={},
            strategic_advice="Research the judges on LinkedIn to understand their professional background—tailor your pitch to their interests."
        )
