import sqlite3
import json
import contextlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone

from returns.result import Result, Success, Failure

from backend.unified.core.domain_types import AppError
from backend.unified.domain.gamification_types import (
    PlayerProfile,
    UserId,
    ExperiencePoints,
    LevelNumber,
    AchievementId,
    SkillArea,
    SkillProgress,
    SkillPoints,
    StreakCount,
    Challenge,
    ChallengeId,
    ChallengeType,
    Ability
)

# Compatibility alias for tests expecting GamificationCache
class GamificationCache:
    pass

class GamificationRepository:
    """
    Repository for persisting gamification data.
    
    Uses SQLite for local storage with JSON serialization for complex types.
    Follows Rule 1: All I/O operations at the boundary.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize with a persistent database connection."""
        self._db_path = db_path or self._get_default_db_path()
        # Use check_same_thread=False for in-memory DBs in multi-threaded test environments
        self._connection = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._ensure_database_exists()

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    # =======================
    # Public API Methods
    # =======================
    
    def save_profile(self, profile: PlayerProfile) -> Result[None, AppError]:
        """Save or update player profile."""
        try:
            with self._get_connection() as conn:
                skill_data = self._serialize_skill_progress(profile.skill_progress)
                achievements = json.dumps(list(profile.completed_achievements))
                badges = json.dumps(list(profile.earned_badges))
                challenges = json.dumps([c.id for c in profile.active_challenges])
                
                conn.execute("""
                    INSERT OR REPLACE INTO player_profiles (
                        user_id, username, total_xp, current_level,
                        completed_achievements, earned_badges, active_challenges,
                        skill_progress, daily_streak, last_active, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(profile.user_id),
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
            return Success(None)
        except Exception as e:
            return Failure(AppError("DB_SAVE_PROFILE_ERROR", str(e)))

    def load_profile(self, user_id: UserId) -> Result[PlayerProfile, AppError]:
        """Load player profile."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM player_profiles WHERE user_id = ?", (str(user_id),))
                row = cursor.fetchone()
            
            if not row:
                return Failure(AppError("PROFILE_NOT_FOUND", f"Profile for user {user_id} not found."))
            
            skill_progress = self._deserialize_skill_progress(row["skill_progress"])
            completed_achievements = set(json.loads(row["completed_achievements"]))
            earned_badges = set(json.loads(row["earned_badges"]))
            
            return Success(PlayerProfile(
                user_id=UserId(row["user_id"]),
                username=row["username"],
                total_xp=ExperiencePoints(row["total_xp"]),
                current_level=LevelNumber(row["current_level"]),
                completed_achievements=completed_achievements,
                earned_badges=earned_badges,
                active_challenges=[],
                skill_progress=skill_progress,
                daily_streak=StreakCount(row["daily_streak"]),
                last_active=datetime.fromisoformat(row["last_active"]),
                created_at=datetime.fromisoformat(row["created_at"])
            ))
        except Exception as e:
            return Failure(AppError("DB_LOAD_PROFILE_ERROR", str(e)))

    def save_challenges(self, user_id: UserId, challenges: List[Challenge]) -> Result[None, AppError]:
        """Save or update challenges for a user."""
        try:
            with self._get_connection() as conn:
                for challenge in challenges:
                    conn.execute("""
                        INSERT OR REPLACE INTO challenges (
                            id, user_id, name, description, type, reward_xp,
                            target_value, current_value, expires_at, skill_areas
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        challenge.id, str(user_id), challenge.name, challenge.description,
                        challenge.type.value, challenge.reward_xp, challenge.target_value,
                        challenge.current_value, challenge.expires_at.isoformat(),
                        json.dumps([s.value for s in challenge.skill_areas])
                    ))
            return Success(None)
        except Exception as e:
            return Failure(AppError("DB_SAVE_CHALLENGES_ERROR", str(e)))

    def load_challenges(self, user_id: UserId) -> Result[List[Challenge], AppError]:
        """Load active challenges for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM challenges WHERE user_id = ?", (str(user_id),))
                rows = cursor.fetchall()

            challenges = []
            for row in rows:
                challenges.append(Challenge(
                    id=ChallengeId(row["id"]),
                    name=row["name"],
                    description=row["description"],
                    type=ChallengeType(row["type"]),
                    reward_xp=ExperiencePoints(row["reward_xp"]),
                    target_value=row["target_value"],
                    current_value=row["current_value"],
                    expires_at=datetime.fromisoformat(row["expires_at"]),
                    skill_areas=[SkillArea(s) for s in json.loads(row["skill_areas"])]
                ))
            return Success(challenges)
        except Exception as e:
            return Failure(AppError("DB_LOAD_CHALLENGES_ERROR", str(e)))

    def get_leaderboard(self, limit: int = 10) -> Result[List[Dict[str, Any]], AppError]:
        """Get top players by XP."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        RANK() OVER (ORDER BY total_xp DESC) as rank,
                        username,
                        total_xp,
                        current_level as level
                    FROM player_profiles
                    ORDER BY total_xp DESC
                    LIMIT ?
                """, (limit,))
                
                entries = [dict(row) for row in cursor.fetchall()]
                return Success(entries)
        except Exception as e:
            return Failure(AppError("DB_LEADERBOARD_ERROR", str(e)))

    # =======================
    # Private Helper Methods
    # =======================
    
    def _get_default_db_path(self) -> Path:
        """Get default database path (in-memory)."""
        return Path(":memory:")

    @contextlib.contextmanager
    def _get_connection(self) -> sqlite3.Connection:
        """Provide a transactional scope around a series of operations."""
        try:
            yield self._connection
        except Exception:
            self._connection.rollback()
            raise
        else:
            self._connection.commit()

    def _ensure_database_exists(self):
        """Ensure database and tables exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS player_profiles (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    total_xp INTEGER NOT NULL,
                    current_level INTEGER NOT NULL,
                    completed_achievements TEXT NOT NULL DEFAULT '[]',
                    earned_badges TEXT NOT NULL DEFAULT '[]',
                    active_challenges TEXT NOT NULL DEFAULT '[]',
                    skill_progress TEXT NOT NULL DEFAULT '{}',
                    daily_streak INTEGER NOT NULL,
                    last_active TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS challenges (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    type TEXT NOT NULL,
                    reward_xp INTEGER NOT NULL,
                    target_value INTEGER NOT NULL,
                    current_value INTEGER NOT NULL,
                    expires_at TEXT NOT NULL,
                    skill_areas TEXT NOT NULL DEFAULT '[]',
                    FOREIGN KEY (user_id) REFERENCES player_profiles(user_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_profiles_xp
                ON player_profiles(total_xp DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_challenges_user
                ON challenges(user_id)
            """)

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
                "unlocked_abilities": [a.value for a in progress.unlocked_abilities]
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
                unlocked_abilities=[Ability(a) for a in skill_info["unlocked_abilities"]]
            )
        
        return progress

import sqlite3
import json
import contextlib
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime, timezone

from returns.result import Result, Success, Failure

from backend.unified.core.domain_types import AppError
from backend.unified.domain.gamification_types import (
    PlayerProfile,
    UserId,
    ExperiencePoints,
    LevelNumber,
    AchievementId,
    SkillArea,
    SkillProgress,
    SkillPoints,
    StreakCount,
    Challenge,
    ChallengeId,
    ChallengeType,
    Ability
)

class GamificationRepository:
    """
    Repository for persisting gamification data.
    
    Uses SQLite for local storage with JSON serialization for complex types.
    Follows Rule 1: All I/O operations at the boundary.
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """Initialize with a persistent database connection."""
        self._db_path = db_path or self._get_default_db_path()
        # Use check_same_thread=False for in-memory DBs in multi-threaded test environments
        self._connection = sqlite3.connect(str(self._db_path), check_same_thread=False)
        self._connection.row_factory = sqlite3.Row
        self._ensure_database_exists()

    def close(self):
        """Close the database connection."""
        if self._connection:
            self._connection.close()
            self._connection = None

    # =======================
    # Public API Methods
    # =======================
    
    def save_profile(self, profile: PlayerProfile) -> Result[None, AppError]:
        """Save or update player profile."""
        try:
            with self._get_connection() as conn:
                skill_data = self._serialize_skill_progress(profile.skill_progress)
                achievements = json.dumps(list(profile.completed_achievements))
                badges = json.dumps(list(profile.earned_badges))
                challenges = json.dumps([c.id for c in profile.active_challenges])
                
                conn.execute("""
                    INSERT OR REPLACE INTO player_profiles (
                        user_id, username, total_xp, current_level,
                        completed_achievements, earned_badges, active_challenges,
                        skill_progress, daily_streak, last_active, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(profile.user_id),
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
            return Success(None)
        except Exception as e:
            return Failure(AppError("DB_SAVE_PROFILE_ERROR", str(e)))

    def load_profile(self, user_id: UserId) -> Result[PlayerProfile, AppError]:
        """Load player profile."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM player_profiles WHERE user_id = ?", (str(user_id),))
                row = cursor.fetchone()
            
            if not row:
                return Failure(AppError("PROFILE_NOT_FOUND", f"Profile for user {user_id} not found."))
            
            skill_progress = self._deserialize_skill_progress(row["skill_progress"])
            completed_achievements = set(json.loads(row["completed_achievements"]))
            earned_badges = set(json.loads(row["earned_badges"]))
            
            return Success(PlayerProfile(
                user_id=UserId(row["user_id"]),
                username=row["username"],
                total_xp=ExperiencePoints(row["total_xp"]),
                current_level=LevelNumber(row["current_level"]),
                completed_achievements=completed_achievements,
                earned_badges=earned_badges,
                active_challenges=[],
                skill_progress=skill_progress,
                daily_streak=StreakCount(row["daily_streak"]),
                last_active=datetime.fromisoformat(row["last_active"]),
                created_at=datetime.fromisoformat(row["created_at"])
            ))
        except Exception as e:
            return Failure(AppError("DB_LOAD_PROFILE_ERROR", str(e)))

    def save_challenges(self, user_id: UserId, challenges: List[Challenge]) -> Result[None, AppError]:
        """Save or update challenges for a user."""
        try:
            with self._get_connection() as conn:
                for challenge in challenges:
                    conn.execute("""
                        INSERT OR REPLACE INTO challenges (
                            id, user_id, name, description, type, reward_xp,
                            target_value, current_value, expires_at, skill_areas
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        challenge.id, str(user_id), challenge.name, challenge.description,
                        challenge.type.value, challenge.reward_xp, challenge.target_value,
                        challenge.current_value, challenge.expires_at.isoformat(),
                        json.dumps([s.value for s in challenge.skill_areas])
                    ))
            return Success(None)
        except Exception as e:
            return Failure(AppError("DB_SAVE_CHALLENGES_ERROR", str(e)))

    def load_challenges(self, user_id: UserId) -> Result[List[Challenge], AppError]:
        """Load active challenges for a user."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("SELECT * FROM challenges WHERE user_id = ?", (str(user_id),))
                rows = cursor.fetchall()

            challenges = []
            for row in rows:
                challenges.append(Challenge(
                    id=ChallengeId(row["id"]),
                    name=row["name"],
                    description=row["description"],
                    type=ChallengeType(row["type"]),
                    reward_xp=ExperiencePoints(row["reward_xp"]),
                    target_value=row["target_value"],
                    current_value=row["current_value"],
                    expires_at=datetime.fromisoformat(row["expires_at"]),
                    skill_areas=[SkillArea(s) for s in json.loads(row["skill_areas"])]
                ))
            return Success(challenges)
        except Exception as e:
            return Failure(AppError("DB_LOAD_CHALLENGES_ERROR", str(e)))

    def get_leaderboard(self, limit: int = 10) -> Result[List[Dict[str, Any]], AppError]:
        """Get top players by XP."""
        try:
            with self._get_connection() as conn:
                cursor = conn.execute("""
                    SELECT 
                        RANK() OVER (ORDER BY total_xp DESC) as rank,
                        username,
                        total_xp,
                        current_level as level
                    FROM player_profiles
                    ORDER BY total_xp DESC
                    LIMIT ?
                """, (limit,))
                
                entries = [dict(row) for row in cursor.fetchall()]
                return Success(entries)
        except Exception as e:
            return Failure(AppError("DB_LEADERBOARD_ERROR", str(e)))

    # =======================
    # Private Helper Methods
    # =======================
    
    def _get_default_db_path(self) -> Path:
        """Get default database path (in-memory)."""
        return Path(":memory:")

    @contextlib.contextmanager
    def _get_connection(self) -> sqlite3.Connection:
        """Provide a transactional scope around a series of operations."""
        try:
            yield self._connection
        except Exception:
            self._connection.rollback()
            raise
        else:
            self._connection.commit()

    def _ensure_database_exists(self):
        """Ensure database and tables exist."""
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS player_profiles (
                    user_id TEXT PRIMARY KEY,
                    username TEXT NOT NULL,
                    total_xp INTEGER NOT NULL,
                    current_level INTEGER NOT NULL,
                    completed_achievements TEXT NOT NULL DEFAULT '[]',
                    earned_badges TEXT NOT NULL DEFAULT '[]',
                    active_challenges TEXT NOT NULL DEFAULT '[]',
                    skill_progress TEXT NOT NULL DEFAULT '{}',
                    daily_streak INTEGER NOT NULL,
                    last_active TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)
            
            conn.execute("""
                CREATE TABLE IF NOT EXISTS challenges (
                    id TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    name TEXT NOT NULL,
                    description TEXT NOT NULL,
                    type TEXT NOT NULL,
                    reward_xp INTEGER NOT NULL,
                    target_value INTEGER NOT NULL,
                    current_value INTEGER NOT NULL,
                    expires_at TEXT NOT NULL,
                    skill_areas TEXT NOT NULL DEFAULT '[]',
                    FOREIGN KEY (user_id) REFERENCES player_profiles(user_id)
                )
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_profiles_xp
                ON player_profiles(total_xp DESC)
            """)
            
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_challenges_user
                ON challenges(user_id)
            """)

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
                "unlocked_abilities": [a.value for a in progress.unlocked_abilities]
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
                unlocked_abilities=[Ability(a) for a in skill_info["unlocked_abilities"]]
            )
        
        return progress