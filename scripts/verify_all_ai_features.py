import sys
import os
# Add the project root to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.orm import Session
from database import SessionLocal
from services.competitive_scout_service import CompetitiveScoutService
from services.squad_architect_service import SquadArchitectService
from services.pitch_studio_service import PitchStudioService
from services.ai_judge_service import AIJudgeService
from models.opportunity import Opportunity
from models.team import Team
from models.user import User

def verify_all_features():
    db = SessionLocal()
    try:
        print("--- VERIFYING STRATEGIC AI ALPHA ---")
        
        # 1. Competitive Scout Verification
        print("\n[1] Testing Competitive Scout Service...")
        scout_service = CompetitiveScoutService(db)
        # Mocking an opportunity for testing
        test_opp = db.query(Opportunity).first()
        if test_opp:
            print(f"Analyzing Hackathon: {test_opp.title}")
            analysis = scout_service.analyze_hackathon(test_opp.id)
            print(f"SUCCESS: Analysis generated with {len(analysis.winning_criteria)} winning criteria.")
        else:
            print("SKIP: No opportunities found in DB.")

        # 2. Squad Architect Verification
        print("\n[2] Testing Squad Architect Service...")
        test_team = db.query(Team).first()
        if not test_team:
            print("INFO: Creating mock team for verification...")
            # Using an existing user ID found in schema check
            existing_user_id = 'd54d1fe2-1cf8-462d-a726-d0b5a7c1652a'
            test_team = Team(
                name="DeepMind Visionaries",
                description="A computer vision project for environmental sustainability.",
                opportunity_id=test_opp.id,
                leader_id=existing_user_id
            )
            db.add(test_team)
            db.commit()

        architect_service = SquadArchitectService(db)
        print(f"Generating Blueprint for Team: {test_team.name}")
        blueprint = architect_service.generate_blueprint(test_team.id)
        print(f"SUCCESS: Roadmap generated with {len(blueprint.roadmap)} steps.")

        # 3. Pitch Studio Verification
        print("\n[3] Testing Pitch Studio Service...")
        pitch_service = PitchStudioService(db)
        pitch = pitch_service.generate_pitch_assets(test_team.id)
        print(f"SUCCESS: Elevator pitch length: {len(pitch.elevator_pitch)} chars.")
        print(f"SUCCESS: Slide blueprint contains {len(pitch.slide_blueprint)} slides.")

        # 4. AI Judge Verification
        print("\n[4] Testing AI Judge Service...")
        judge_service = AIJudgeService(db)
        audit = judge_service.audit_submission(test_team.id, {
            "title": "HackItAll AI",
            "description": "An AI platform for hackathons.",
            "github_url": "https://github.com/test/repo"
        })
        print(f"SUCCESS: Winning Probability: {audit.winning_probability*100}%")
        print(f"SUCCESS: Red Flags identified: {len(audit.red_flags)}")

        print("\n--- ALL CORE AI SERVICES VERIFIED ---")
        
    except Exception as e:
        print(f"\nERROR DURING VERIFICATION: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    verify_all_features()
