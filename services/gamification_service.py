"""Service for handling user XP awards, streaks, tiers, and achievements."""
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple, Optional
from sqlalchemy.orm import Session
import uuid

from models.gamification import UserXP, XPTransaction, Achievement, UserAchievement
from database import Base


class GamificationService:
    """Service to manage user progression, tiers, and reward XP."""

    # XP threshold for league tiers (1=Bronze, 6=Obsidian)
    TIER_THRESHOLDS = {
        1: 0,      # Bronze Byte
        2: 500,    # Silver Script 
        3: 1500,   # Gold Gateway
        4: 3500,   # Platinum Pixel
        5: 7000,   # Diamond Debug
        6: 15000,  # Obsidian Overlord
    }

    # XP Reward configuration (mapped to existing platform features)
    XP_REWARDS = {
        "profile_complete": 100,
        "track": 10,
        "apply": 25,
        "accepted": 50,
        "completed": 100,
        "analyze_fit": 15,
        "view_content": 5,
        "daily_login": 10,
        "scrape": 20,
        "streak_bonus_7": 75,
    }

    def __init__(self, db_session: Session):
        self.db = db_session

    def award_xp(self, user_id: str, action_type: str, reference_id: str = None) -> Tuple[int, bool]:
        """Award XP to a user based on an action and check for tier promotion.
        
        Args:
            user_id: User ID to reward
            action_type: Action code from XP_REWARDS
            reference_id: Optional ID to avoid double-rewarding (e.g. content_id)
            
        Returns:
            Tuple: (XP gained, True if tier promoted)
        """
        xp_gain = self.XP_REWARDS.get(action_type, 0)
        if xp_gain <= 0 and action_type != "daily_login": # Allow daily_login even if xp is 0 (unlikely)
            return 0, False

        # 1. Log Transaction (only if reference_id unique for this action/user)
        if reference_id:
            existing = self.db.query(XPTransaction).filter(
                XPTransaction.user_id == user_id,
                XPTransaction.action_type == action_type,
                XPTransaction.reference_id == reference_id
            ).first()
            if existing: # Avoid double-rewarding same content/action
                return 0, False

        # 2. Update User Stats (create if not exist)
        stats = self.db.query(UserXP).filter(UserXP.user_id == user_id).first()
        if not stats:
            stats = UserXP(user_id=user_id, total_xp=0, league_tier=1, last_login_at=datetime.utcnow() - timedelta(days=2))
            self.db.add(stats)
            self.db.flush()

        old_tier = stats.league_tier
        
        # 3. Handle Login Streaks (if daily_login)
        if action_type == "daily_login":
            now = datetime.utcnow()
            # Calculate days since last login
            if stats.last_login_at:
                last_date = stats.last_login_at.date()
                today_date = now.date()
                diff = (today_date - last_date).days
                
                if diff == 1:
                    stats.streak_days += 1
                elif diff > 1:
                    stats.streak_days = 1 # Streak broken
                # if diff == 0, keep current streak
            else:
                stats.streak_days = 1
                
            stats.last_login_at = now
            
            # Check for streak achievements
            if stats.streak_days >= 7:
                self.unlock_achievement(user_id, "streak_7")
            if stats.streak_days >= 30:
                self.unlock_achievement(user_id, "streak_30")

        # Only reward if we haven't rewarded this reference_id yet (already checked above)
        if xp_gain > 0:
            transaction = XPTransaction(
                user_id=user_id,
                xp_amount=xp_gain,
                action_type=action_type,
                reference_id=reference_id
            )
            self.db.add(transaction)
            stats.total_xp += xp_gain
            stats.last_xp_at = datetime.utcnow()

        stats.updated_at = datetime.utcnow()

        # 4. Calculate Tier Promotion
        new_tier = self._calculate_tier(stats.total_xp)
        stats.league_tier = new_tier
        
        # 5. Milestone Achievements
        if action_type == "track":
            track_count = self.db.query(XPTransaction).filter(XPTransaction.user_id == user_id, XPTransaction.action_type == "track").count()
            if track_count >= 1: self.unlock_achievement(user_id, "first_steps")
            if track_count >= 10: self.unlock_achievement(user_id, "tracker_10")
        
        if action_type == "profile_complete":
            self.unlock_achievement(user_id, "onboarding")

        self.db.commit()
        return xp_gain, (new_tier > old_tier)

    def unlock_achievement(self, user_id: str, achievement_code: str) -> bool:
        """Unlock an achievement for a user and award its bonus XP."""
        achievement = self.db.query(Achievement).filter(Achievement.code == achievement_code).first()
        if not achievement:
            return False
            
        exists = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id,
            UserAchievement.achievement_id == achievement.id
        ).first()
        
        if exists:
            return False
            
        user_ach = UserAchievement(user_id=user_id, achievement_id=achievement.id)
        self.db.add(user_ach)
        
        # Award bonus XP for achievement
        if achievement.xp_reward > 0:
            stats = self.db.query(UserXP).filter(UserXP.user_id == user_id).first()
            if stats:
                stats.total_xp += achievement.xp_reward
                
            transaction = XPTransaction(
                user_id=user_id,
                xp_amount=achievement.xp_reward,
                action_type="achievement",
                reference_id=achievement_code
            )
            self.db.add(transaction)
            
        return True

    def _calculate_tier(self, total_xp: int) -> int:
        """Heuristic to map total XP to league tier levels."""
        highest_tier = 1
        for tier, threshold in self.TIER_THRESHOLDS.items():
            if total_xp >= threshold:
                highest_tier = tier
        return highest_tier

    def get_user_stats(self, user_id: str) -> Dict[str, Any]:
        """Fetch user's current XP stats, tier info, and recent achievements."""
        stats = self.db.query(UserXP).filter(UserXP.user_id == user_id).first()
        if not stats:
            return {
                "total_xp": 0, "league_tier": 1, "streak_days": 0,
                "tier_name": "Bronze Byte", "next_tier_xp": 500,
                "progress_pct": 0
            }

        tier_names = {
            1: "Bronze Byte", 2: "Silver Script", 3: "Gold Gateway",
            4: "Platinum Pixel", 5: "Diamond Debug", 6: "Obsidian Overlord"
        }
        
        next_xp = self.TIER_THRESHOLDS.get(stats.league_tier + 1, 999999)
        curr_xp_start = self.TIER_THRESHOLDS.get(stats.league_tier, 0)
        progress = stats.total_xp - curr_xp_start
        total_needed = next_xp - curr_xp_start
        pct = min(100, int((progress / total_needed) * 100)) if total_needed > 0 else 100

        # Fetch achievements
        achievements = self.db.query(UserAchievement).filter(
            UserAchievement.user_id == user_id
        ).all()

        # Calculate global rank
        rank = self.db.query(UserXP).filter(UserXP.total_xp > stats.total_xp).count() + 1
        total_users = self.db.query(UserXP).count()

        return {
            "total_xp": stats.total_xp,
            "league_tier": stats.league_tier,
            "tier_name": tier_names.get(stats.league_tier, "Unknown"),
            "streak_days": stats.streak_days,
            "next_tier_xp": next_xp,
            "progress_pct": pct,
            "unlocked_badges": [a.achievement.code for a in achievements],
            "last_login": stats.last_login_at.isoformat() if stats.last_login_at else None,
            "rank": rank,
            "total_users": total_users
        }

    def get_leaderboard(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Rank users by total XP for the global leaderboard."""
        from models.user import User
        results = self.db.query(User.email, UserXP.total_xp, UserXP.league_tier, UserXP.streak_days, User.username)\
            .join(UserXP, User.id == UserXP.user_id)\
            .order_by(UserXP.total_xp.desc())\
            .limit(limit).all()
        
        def mask_email(email):
            parts = email.split('@')
            if len(parts[0]) <= 2:
                return parts[0] + "****"
            return parts[0][0] + "****" + parts[0][-1]

        return [
            {
                "email": r[4] if r[4] else mask_email(r[0]), # Use username if available, else mask 
                "xp": r[1],
                "tier": r[2],
                "streak": r[3]
            } for r in results
        ]

    def seed_achievements(self):
        """Seed the initial achievement meta-data as defined in the plan."""
        badges = [
            # Basic Achievements
            ("first_steps", "First Steps", "Track your first hackathon", "runner", 50),
            ("onboarding", "Citizen", "Complete your user profile", "medal", 100),
            ("tracker_10", "Bug Catcher", "Track 10 opportunities", "bug", 150),
            
            # Action Milestones
            ("first_scrape", "Data Miner", "Scrape your first custom URL", "spider", 75),
            ("content_10", "Knowledge Seeker", "View 10 educational articles", "books", 150),
            ("analyze_5", "Strategist", "Analyze your fit for 5 events", "search", 200),
            
            # Participation
            ("applied_5", "Form Filler", "Apply to 5 different events", "books", 300),
            ("accepted_1", "Golden Ticket", "Get accepted for the first time", "circuit", 500),
            ("completed_3", "Hat Trick", "Complete 3 hackathons", "crown", 1000),
            ("completed_10", "Legendary Dev", "Complete 10 hackathons", "skull", 5000),
            
            # Streaks
            ("streak_7", "Week Warrior", "7-day daily login streak", "flame", 250),
            ("streak_30", "Monthly Monster", "30-day daily login streak", "gem", 1500),
        ]
        
        for code, title, desc, icon, xp in badges:
            existing = self.db.query(Achievement).filter(Achievement.code == code).first()
            if not existing:
                a = Achievement(code=code, title=title, description=desc, icon_name=icon, xp_reward=xp)
                self.db.add(a)
        
        self.db.commit()
