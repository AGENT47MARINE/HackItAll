from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from database import get_db
from api.auth import get_current_user
from services.gamification_service import GamificationService

router = APIRouter(prefix="/api/gamification", tags=["gamification"])


class UserGamificationStats(BaseModel):
    total_xp: int
    league_tier: int
    tier_name: str
    streak_days: int
    next_tier_xp: int
    progress_pct: int
    unlocked_badges: List[str]
    last_login: str
    rank: int
    total_users: int


class LeaderboardEntry(BaseModel):
    email: str
    xp: int
    tier: int
    streak: int


@router.get("/stats", response_model=UserGamificationStats)
async def get_stats(
    current_user_id: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve current user's XP, tier, and streak stats."""
    service = GamificationService(db)
    return service.get_user_stats(current_user_id)


@router.get("/leaderboard", response_model=List[LeaderboardEntry])
async def get_leaderboard(
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """Retrieve global leaderboard of top XP earners."""
    service = GamificationService(db)
    return service.get_leaderboard(limit=limit)


@router.post("/admin/seed", status_code=status.HTTP_201_CREATED)
async def seed_achievements(
    db: Session = Depends(get_db)
):
    """Admin tool to seed achievement metadata (idempotent)."""
    service = GamificationService(db)
    service.seed_achievements()
    return {"status": "Achievements seeded successfully"}
