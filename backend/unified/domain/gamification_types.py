"""
Domain types for gamification system following the Intentional Disclosure Principle.

All types are immutable and maximize disclosure through the type system.
Pure domain logic with no infrastructure concerns.

Copyright: DarkLightX / Dana Edwards
"""

from dataclasses import dataclass, field
from typing import NewType, List, Optional, Dict, Set, Literal
from enum import Enum
from datetime import datetime

# =======================
# Domain Type Aliases (Rule 3: Maximize Disclosure via Type System)
# =======================

ExperiencePoints = NewType("ExperiencePoints", int)
LevelNumber = NewType("LevelNumber", int)
AchievementId = NewType("AchievementId", str)
ChallengeId = NewType("ChallengeId", str)
StreakCount = NewType("StreakCount", int)
UserId = NewType("UserId", str)
SkillPoints = NewType("SkillPoints", int)
BadgeId = NewType("BadgeId", str)

class AchievementCategory(Enum):
    """Categories of achievements."""
    LEARNING = "learning"
    PRACTICE = "practice"
    MASTERY = "mastery"
    EXPLORATION = "exploration"
    CONSISTENCY = "consistency"
    COLLABORATION = "collaboration"

class ChallengeType(Enum):
    """Types of challenges."""
    DAILY = "daily"
    WEEKLY = "weekly"
    SKILL_BASED = "skill_based"
    MILESTONE = "milestone"
    SPECIAL_EVENT = "special_event"

class SkillArea(Enum):
    """Areas of expertise in formal specification."""
    TEMPORAL_LOGIC = "temporal_logic"
    QUANTIFIERS = "quantifiers"
    STREAM_PROCESSING = "stream_processing"
    SOLVER_CONSTRAINTS = "solver_constraints"
    FUNCTION_DEFINITIONS = "function_definitions"
    PATTERN_MATCHING = "pattern_matching"
    TRANSLATION = "translation"

class BadgeRarity(Enum):
    """Rarity levels for badges."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"

# =======================
# Core Domain Models
# =======================

@dataclass(frozen=True)
class Achievement:
    """
    Immutable achievement definition.
    Follows Rule 3: Rich type disclosure.
    """
    id: AchievementId
    name: str
    description: str
    category: AchievementCategory
    points: ExperiencePoints
    icon_name: str
    unlock_criteria: str
    hidden: bool = False
    prerequisites: List[AchievementId] = field(default_factory=list)
    
    def is_unlockable(self, completed_achievements: Set[AchievementId]) -> bool:
        """Check if achievement can be unlocked based on prerequisites."""
        return all(prereq in completed_achievements for prereq in self.prerequisites)

@dataclass(frozen=True)
class Badge:
    """Visual badge earned through achievements."""
    id: BadgeId
    name: str
    description: str
    rarity: BadgeRarity
    icon_path: str
    achievement_id: AchievementId
    skill_area: Optional[SkillArea] = None

@dataclass(frozen=True)
class Challenge:
    """Time-limited challenge for users."""
    id: ChallengeId
    name: str
    description: str
    type: ChallengeType
    reward_xp: ExperiencePoints
    target_value: int
    current_value: int = 0
    expires_at: datetime
    skill_areas: List[SkillArea] = field(default_factory=list)
    
    def is_completed(self) -> bool:
        """Check if challenge is completed."""
        return self.current_value >= self.target_value
    
    def is_expired(self, current_time: datetime) -> bool:
        """Check if challenge has expired."""
        return current_time > self.expires_at
    
    def progress_percentage(self) -> float:
        """Calculate progress as percentage."""
        if self.target_value == 0:
            return 100.0
        return min(100.0, (self.current_value / self.target_value) * 100)

@dataclass(frozen=True)
class Level:
    """Player level with XP requirements."""
    number: LevelNumber
    title: str
    required_xp: ExperiencePoints
    perks: List[str] = field(default_factory=list)

@dataclass(frozen=True)
class SkillProgress:
    """Progress in a specific skill area."""
    skill: SkillArea
    current_points: SkillPoints
    level: int
    next_level_points: SkillPoints
    unlocked_abilities: List[str] = field(default_factory=list)
    
    def progress_to_next_level(self) -> float:
        """Calculate progress to next level as percentage."""
        if self.next_level_points <= self.current_points:
            return 100.0
        return (self.current_points / self.next_level_points) * 100

@dataclass(frozen=True)
class PlayerProfile:
    """
    Complete player profile with gamification data.
    Central aggregate for all player progress.
    """
    user_id: UserId
    username: str
    total_xp: ExperiencePoints
    current_level: LevelNumber
    completed_achievements: Set[AchievementId]
    earned_badges: Set[BadgeId]
    active_challenges: List[ChallengeId]
    skill_progress: Dict[SkillArea, SkillProgress]
    daily_streak: StreakCount
    last_active: datetime
    created_at: datetime
    
    def has_achievement(self, achievement_id: AchievementId) -> bool:
        """Check if player has completed an achievement."""
        return achievement_id in self.completed_achievements
    
    def get_skill_level(self, skill: SkillArea) -> int:
        """Get player's level in a specific skill."""
        progress = self.skill_progress.get(skill)
        return progress.level if progress else 0

@dataclass(frozen=True)
class GamificationEvent:
    """
    Event that triggers gamification updates.
    Used to track user actions that affect progress.
    """
    event_type: str
    user_id: UserId
    timestamp: datetime
    metadata: Dict[str, any] = field(default_factory=dict)
    xp_earned: Optional[ExperiencePoints] = None
    skills_affected: List[SkillArea] = field(default_factory=list)

@dataclass(frozen=True)
class Leaderboard:
    """Leaderboard for competitive elements."""
    period: Literal["daily", "weekly", "monthly", "all_time"]
    entries: List['LeaderboardEntry']
    last_updated: datetime

@dataclass(frozen=True)
class LeaderboardEntry:
    """Single entry in a leaderboard."""
    rank: int
    user_id: UserId
    username: str
    score: int
    level: LevelNumber
    badges_count: int

# =======================
# Value Objects
# =======================

@dataclass(frozen=True)
class XPTransaction:
    """Record of XP gain/loss."""
    amount: ExperiencePoints
    reason: str
    timestamp: datetime
    source: str

@dataclass(frozen=True)
class ProgressUpdate:
    """Update to player progress."""
    xp_gained: ExperiencePoints
    achievements_unlocked: List[AchievementId]
    badges_earned: List[BadgeId]
    challenges_completed: List[ChallengeId]
    level_ups: List[LevelNumber]
    skill_improvements: Dict[SkillArea, SkillPoints]

# =======================
# Game Rules Configuration
# =======================

@dataclass(frozen=True)
class GamificationRules:
    """Configuration for gamification mechanics."""
    xp_per_suggestion_used: ExperiencePoints = ExperiencePoints(10)
    xp_per_translation: ExperiencePoints = ExperiencePoints(25)
    xp_per_correct_pattern: ExperiencePoints = ExperiencePoints(15)
    streak_bonus_multiplier: float = 1.5
    daily_challenge_count: int = 3
    level_up_bonus_xp: ExperiencePoints = ExperiencePoints(100)
    
    # XP penalties (optional)
    xp_penalty_for_error: ExperiencePoints = ExperiencePoints(0)
    
    # Skill point allocations
    skill_points_per_action: Dict[str, Dict[SkillArea, SkillPoints]] = field(
        default_factory=lambda: {
            "temporal_usage": {SkillArea.TEMPORAL_LOGIC: SkillPoints(5)},
            "quantifier_usage": {SkillArea.QUANTIFIERS: SkillPoints(5)},
            "stream_usage": {SkillArea.STREAM_PROCESSING: SkillPoints(5)},
            "solver_usage": {SkillArea.SOLVER_CONSTRAINTS: SkillPoints(5)},
            "translation": {SkillArea.TRANSLATION: SkillPoints(10)},
        }
    )