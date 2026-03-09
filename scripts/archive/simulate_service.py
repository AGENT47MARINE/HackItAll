from sqlalchemy.orm import Session
from database import SessionLocal
from services.opportunity_service import OpportunityService
import json

db = SessionLocal()
try:
    service = OpportunityService(db)
    results = service.search_opportunities(include_archived=False)
    print(f"Results count: {len(results)}")
    for r in results:
        print(f"- {r['title']} (status: {r['status']})")
finally:
    db.close()
