"""
Persistence layer for gamification data.

Handles saving and loading player profiles, achievements, and progress.
Follows Rule 1: I/O at the boundaries.

Copyright: DarkLightX / Dana Edwards
"""

import json
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Set
from datetime import datetime
from contextlib import contextmanager

from ..core.result_enhanced import Result, Success, Failure
from ..domain.gamification_types import (
    PlayerProfile, Achievement, AchievementId, Badge, BadgeId,
    Challenge, ChallengeId, ExperiencePoints, LevelNumber,
    SkillArea, SkillProgress, SkillPoints, UserId, StreakCount
)

class GamificationRepository:
    """
    Repository for persisting gamification data.
    
    Uses SQLite for local storage with JSON serialization for complex types.
    Follows Rule 1: All I/O operations at the boundary.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize with database path."""
        self._db_path = db_path or self._get_default_db_path()
        self._ensure_database_exists()
    
    # =======================
    # Public API Methods
    # =======================
    
    def save_profile(self, profile: PlayerProfile) -> Result[None]:
        """Save or update player profile."""
        try:
            with self._get_connection() as conn:
                # Serialize complex data
                skill_data = self._serialize_skill_progress(profile.skill_progress)
                achievements = json.dumps(list(profile.completed_achievements))
                badges = json.dumps(list(profile.earned_badges))
                challenges = json.dumps(profile.active_challenges)
                
                conn.execute("""
                    INSERT OR REPLACE INTO player_profiles (
                        user_id, username, total_xp, current_level,
                        completed_achievements, earned_badges, active_challenges,
                        skill_progress, daily_streak, last_active, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    profile.user_id,
                    profile.username,
                    profile.total_xp,
                    profile.current_level,
                    achievements,
                    badges,
                    challenges,
                    skill_data,
                    profile.daily_streak,
                    profile.last_active.isoformat(),
                    profile.created_at.isoformat()
                ))
                
                conn.commit()
                return Success(None)
                
        except Exception as e:
            return Failure("SAVE_FAILED", f"Failed to save profile: {str(e)}")
    
    def load_profile(self, user_id: UserId) -> Result[PlayerProfile]:
        """Load player profile by user ID."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT username, total_xp, current_level,
                           completed_achievements, earned_badges, active_challenges,
                           skill_progress, daily_streak, last_active, created_at
                    FROM player_profiles
                    WHERE user_id = ?
                """, (user_id,))
                
                row = cursor.fetchone()
                if not row:
                    return Failure("NOT_FOUND", f"Profile not found for user {user_id}")
                
                # Deserialize data
                profile = PlayerProfile(
                    user_id=user_id,
                    username=row[0],
                    total_xp=ExperiencePoints(row[1]),
                    current_level=LevelNumber(row[2]),
                    completed_achievements=set(json.loads(row[3])),
                    earned_badges=set(json.loads(row[4])),
                    active_challenges=json.loads(row[5]),
                    skill_progress=self._deserialize_skill_progress(row[6]),
                    daily_streak=StreakCount(row[7]),
                    last_active=datetime.fromisoformat(row[8]),
                    created_at=datetime.fromisoformat(row[9])
                )
                
                return Success(profile)
                
        except Exception as e:
            return Failure("LOAD_FAILED", f"Failed to load profile: {str(e)}")
    
    def create_profile(
        self,
        user_id: UserId,
        username: str
    ) -> Result[PlayerProfile]:
        """Create a new player profile."""
        profile = PlayerProfile(
            user_id=user_id,
            username=username,
            total_xp=ExperiencePoints(0),
            current_level=LevelNumber(1),
            completed_achievements=set(),
            earned_badges=set(),
            active_challenges=[],
            skill_progress={},
            daily_streak=StreakCount(0),
            last_active=datetime.now(),
            created_at=datetime.now()
        )
        
        save_result = self.save_profile(profile)
        if save_result.is_success():
            return Success(profile)
        return save_result
    
    def save_challenges(
        self,
        user_id: UserId,
        challenges: List[Challenge]
    ) -> Result[None]:
        """Save user's active challenges."""
        try:
            with self._get_connection() as conn:
                # Clear existing challenges
                conn.execute(
                    "DELETE FROM challenges WHERE user_id = ?",
                    (user_id,)
                )
                
                # Insert new challenges
                for challenge in challenges:
                    conn.execute("""
                        INSERT INTO challenges (
                            challenge_id, user_id, name, description,
                            type, reward_xp, target_value, current_value,
                            expires_at, skill_areas
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        challenge.id,
                        user_id,
                        challenge.name,
                        challenge.description,
                        challenge.type.value,
                        challenge.reward_xp,
                        challenge.target_value,
                        challenge.current_value,
                        challenge.expires_at.isoformat(),
                        json.dumps([s.value for s in challenge.skill_areas])
                    ))
                
                conn.commit()
                return Success(None)
                
        except Exception as e:
            return Failure("SAVE_FAILED", f"Failed to save challenges: {str(e)}")
    
    def load_challenges(self, user_id: UserId) -> Result[List[Challenge]]:
        """Load user's active challenges."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT challenge_id, name, description, type,
                           reward_xp, target_value, current_value,
                           expires_at, skill_areas
                    FROM challenges
                    WHERE user_id = ?
                """, (user_id,))
                
                challenges = []
                for row in cursor.fetchall():
                    challenge = Challenge(
                        id=ChallengeId(row[0]),
                        name=row[1],
                        description=row[2],
                        type=row[3],
                        reward_xp=ExperiencePoints(row[4]),
                        target_value=row[5],
                        current_value=row[6],
                        expires_at=datetime.fromisoformat(row[7]),
                        skill_areas=[
                            SkillArea(s) for s in json.loads(row[8])
                        ]
                    )
                    challenges.append(challenge)
                
                return Success(challenges)
                
        except Exception as e:
            return Failure("LOAD_FAILED", f"Failed to load challenges: {str(e)}")
    
    def get_leaderboard(
        self,
        limit: int = 10,
        offset: int = 0
    ) -> Result[List[Dict]]:
        """Get leaderboard entries."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT user_id, username, total_xp, current_level,
                           COUNT(DISTINCT earned_badges) as badge_count
                    FROM player_profiles
                    ORDER BY total_xp DESC
                    LIMIT ? OFFSET ?
                """, (limit, offset))
                
                entries = []
                for i, row in enumerate(cursor.fetchall()):
                    entries.append({
                        "rank": offset + i + 1,
                        "user_id": row[0],
                        "username": row[1],
                        "total_xp": row[2],
                        "level": row[3],
                        "badges": row[4]
                    })
                
                return Success(entries)
                
        except Exception as e:
            return Failure("LOAD_FAILED", f"Failed to load leaderboard: {str(e)}")
    
    def update_streak(
        self,
        user_id: UserId,
        new_streak: StreakCount
    ) -> Result[None]:
        """Update user's daily streak."""
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    UPDATE player_profiles
                    SET daily_streak = ?, last_active = ?
                    WHERE user_id = ?
                """, (new_streak, datetime.now().isoformat(), user_id))
                
                conn.commit()
                return Success(None)
                
        except Exception as e:
            return Failure("UPDATE_FAILED", f"Failed to update streak: {str(e)}")
    
    # =======================
    # Private Implementation Methods
    # =======================
    
    def _get_default_db_path(self) -> Path:
        """Get default database path."""
        app_data = Path.home() / ".tau_translator" / "gamification"
        app_data.mkdir(parents=True, exist_ok=True)
        return app_data / "progress.db"
    
    @contextmanager
    def _get_connection(self):
        """Get database connection with automatic cleanup."""
        conn = sqlite3.connect(str(self._db_path))
        try:
            yield conn
        finally:
            conn.close()
    
    def _ensure_database_exists(self):
        """Create database tables if they don't exist."""
        with self._get_connection() as conn:
            # Player profiles table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS player_profiles (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    total_xp INTEGER NOT NULL DEFAULT 0,
                    current_level INTEGER NOT NULL DEFAULT 1,
                    completed_achievements TEXT NOT NULL DEFAULT '[]',
                    earned_badges TEXT NOT NULL DEFAULT '[]',
                    active_challenges TEXT NOT NULL DEFAULT '[]',
                    skill_progress TEXT NOT NULL DEFAULT '{}',
                    daily_streak INTEGER NOT NULL DEFAULT 0,
                    last_active TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            # Challenges table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS challenges (
                    challenge_id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    type TEXT NOT NULL,
                    reward_xp INTEGER NOT NULL,
                    target_value INTEGER NOT NULL,
                    current_value INTEGER NOT NULL DEFAULT 0,
                    expires_at TEXT NOT NULL,
                    skill_areas TEXT NOT NULL DEFAULT '[]',
                    FOREIGN KEY (user_id) REFERENCES player_profiles(user_id)
                )
            """)
            
            # Create indexes
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_profiles_xp
                ON player_profiles(total_xp DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_challenges_user
                ON challenges(user_id)
            """)
            
            conn.commit()
    
    def _serialize_skill_progress(
        self,
        skill_progress: Dict[SkillArea, SkillProgress]
    ) -> str:
        """Serialize skill progress to JSON."""
        data = {}
        for skill, progress in skill_progress.items():
            data[skill.value] = {
                "current_points": progress.current_points,
                "level": progress.level,
                "next_level_points": progress.next_level_points,
                "unlocked_abilities": progress.unlocked_abilities
            }
        return json.dumps(data)
    
    def _deserialize_skill_progress(
        self,
        data: str
    ) -> Dict[SkillArea, SkillProgress]:
        """Deserialize skill progress from JSON."""
        skill_data = json.loads(data)
        progress = {}
        
        for skill_name, skill_info in skill_data.items():
            skill = SkillArea(skill_name)
            progress[skill] = SkillProgress(
                skill=skill,
                current_points=SkillPoints(skill_info["current_points"]),
                level=skill_info["level"],
                next_level_points=SkillPoints(skill_info["next_level_points"]),
                unlocked_abilities=skill_info["unlocked_abilities"]
            )
        
        return progress

class GamificationCache:
    """
    In-memory cache for frequently accessed gamification data.
    
    Reduces database queries for better performance.
    """
    
    def __init__(self):
        """Initialize cache storage."""
        self._profiles: Dict[UserId, PlayerProfile] = {}
        self._challenges: Dict[UserId, List[Challenge]] = {}
        self._achievements: Dict[AchievementId, Achievement] = {}
        self._last_update: Dict[UserId, datetime] = {}
    
    def get_profile(self, user_id: UserId) -> Optional[PlayerProfile]:
        """Get cached profile if fresh."""
        if self._is_cache_fresh(user_id):
            return self._profiles.get(user_id)
        return None
    
    def set_profile(self, profile: PlayerProfile):
        """Cache profile."""
        self._profiles[profile.user_id] = profile
        self._last_update[profile.user_id] = datetime.now()
    
    def invalidate_user(self, user_id: UserId):
        """Invalidate all cached data for a user."""
        self._profiles.pop(user_id, None)
        self._challenges.pop(user_id, None)
        self._last_update.pop(user_id, None)
    
    def _is_cache_fresh(self, user_id: UserId) -> bool:
        """Check if cache is still fresh (5 minutes)."""
        last_update = self._last_update.get(user_id)
        if not last_update:
            return False
        
        age = datetime.now() - last_update
        return age.total_seconds() < 300  # 5 minutes