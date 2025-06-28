"""
Gamification service implementing pure domain logic.

Follows Rule 2: Public methods orchestrate, private methods implement.
No infrastructure dependencies - pure domain logic only.

Copyright: DarkLightX / Dana Edwards
"""

from typing import List, Optional, Set, Dict
from datetime import datetime, timedelta
from ..core.result_enhanced import Result, Success, Failure
from .gamification_types import (
    Achievement, AchievementId, Badge, BadgeId, Challenge, ChallengeId,
    ExperiencePoints, LevelNumber, PlayerProfile, SkillArea, SkillPoints,
    SkillProgress, GamificationEvent, ProgressUpdate, XPTransaction,
    GamificationRules, UserId, StreakCount, AchievementCategory,
    ChallengeType, Level
)

class GamificationService:
    """
    Pure domain service for gamification logic.
    
    Handles XP calculation, achievement checking, level progression,
    and challenge management without any infrastructure concerns.
    """
    
    def __init__(self, rules: Optional[GamificationRules] = None):
        """Initialize with game rules configuration."""
        self._rules = rules or GamificationRules()
        self._levels = self._initialize_levels()
        self._achievements = self._initialize_achievements()
        self._badges = self._initialize_badges()
    
    # =======================
    # Public API Methods (Rule 2: Orchestration)
    # =======================
    
    def process_event(
        self,
        event: GamificationEvent,
        profile: PlayerProfile
    ) -> Result[ProgressUpdate]:
        """
        Process a gamification event and calculate progress updates.
        
        Main entry point for all gamification calculations.
        """
        # Calculate XP from event
        xp_result = self._calculate_xp_for_event(event, profile)
        if not xp_result.is_success():
            return xp_result
        
        xp_gained = xp_result.value
        
        # Check for achievements
        new_achievements = self._check_achievements(event, profile, xp_gained)
        
        # Calculate skill progress
        skill_updates = self._calculate_skill_progress(event, profile)
        
        # Check for level ups
        level_ups = self._check_level_progression(
            profile.total_xp,
            profile.total_xp + xp_gained
        )
        
        # Check challenge progress
        completed_challenges = self._update_challenge_progress(
            event,
            profile.active_challenges
        )
        
        # Calculate badges from achievements
        new_badges = self._get_badges_for_achievements(new_achievements)
        
        # Create progress update
        update = ProgressUpdate(
            xp_gained=xp_gained,
            achievements_unlocked=new_achievements,
            badges_earned=new_badges,
            challenges_completed=completed_challenges,
            level_ups=level_ups,
            skill_improvements=skill_updates
        )
        
        return Success(update)
    
    def calculate_streak_bonus(
        self,
        base_xp: ExperiencePoints,
        streak_count: StreakCount
    ) -> ExperiencePoints:
        """Calculate XP with streak bonus applied."""
        if streak_count <= 1:
            return base_xp
        
        # Apply exponential decay to prevent infinite scaling
        multiplier = min(
            self._rules.streak_bonus_multiplier ** min(streak_count, 7),
            5.0  # Cap at 5x
        )
        
        return ExperiencePoints(int(base_xp * multiplier))
    
    def generate_daily_challenges(
        self,
        profile: PlayerProfile,
        current_date: datetime
    ) -> List[Challenge]:
        """Generate personalized daily challenges."""
        challenges = []
        
        # Challenge 1: Use specific feature
        challenges.append(self._create_feature_challenge(profile, current_date))
        
        # Challenge 2: Skill-based challenge
        challenges.append(self._create_skill_challenge(profile, current_date))
        
        # Challenge 3: Streak or consistency challenge
        challenges.append(self._create_consistency_challenge(profile, current_date))
        
        return challenges[:self._rules.daily_challenge_count]
    
    def get_next_achievements(
        self,
        profile: PlayerProfile
    ) -> List[Achievement]:
        """Get achievements the player is close to unlocking."""
        available = []
        
        for achievement in self._achievements.values():
            if achievement.id in profile.completed_achievements:
                continue
                
            if achievement.is_unlockable(profile.completed_achievements):
                available.append(achievement)
        
        # Sort by how close player is to unlocking
        return sorted(available, key=lambda a: len(a.prerequisites))[:5]
    
    def calculate_level_from_xp(
        self,
        total_xp: ExperiencePoints
    ) -> LevelNumber:
        """Calculate level number from total XP."""
        for level in reversed(self._levels):
            if total_xp >= level.required_xp:
                return level.number
        
        return LevelNumber(1)
    
    # =======================
    # Private Implementation Methods
    # =======================
    
    def _calculate_xp_for_event(
        self,
        event: GamificationEvent,
        profile: PlayerProfile
    ) -> Result[ExperiencePoints]:
        """Calculate XP earned from an event."""
        base_xp = ExperiencePoints(0)
        
        # Map event types to XP values
        xp_map = {
            "suggestion_used": self._rules.xp_per_suggestion_used,
            "translation_completed": self._rules.xp_per_translation,
            "pattern_matched": self._rules.xp_per_correct_pattern,
        }
        
        base_xp = xp_map.get(event.event_type, ExperiencePoints(5))
        
        # Apply streak bonus if applicable
        if self._should_apply_streak_bonus(event):
            base_xp = self.calculate_streak_bonus(base_xp, profile.daily_streak)
        
        # Apply any event-specific XP
        if event.xp_earned:
            base_xp = ExperiencePoints(base_xp + event.xp_earned)
        
        return Success(base_xp)
    
    def _check_achievements(
        self,
        event: GamificationEvent,
        profile: PlayerProfile,
        xp_gained: ExperiencePoints
    ) -> List[AchievementId]:
        """Check if any achievements were unlocked."""
        unlocked = []
        
        # Check each achievement
        for achievement in self._achievements.values():
            if achievement.id in profile.completed_achievements:
                continue
            
            if self._is_achievement_unlocked(achievement, event, profile, xp_gained):
                unlocked.append(achievement.id)
        
        return unlocked
    
    def _is_achievement_unlocked(
        self,
        achievement: Achievement,
        event: GamificationEvent,
        profile: PlayerProfile,
        xp_gained: ExperiencePoints
    ) -> bool:
        """Check if specific achievement is unlocked."""
        # Check prerequisites
        if not achievement.is_unlockable(profile.completed_achievements):
            return False
        
        # Check specific unlock criteria
        criteria_checks = {
            "first_translation": self._check_first_translation,
            "streak_7": self._check_streak_achievement,
            "level_10": self._check_level_achievement,
            "all_skills_5": self._check_skill_achievement,
        }
        
        check_func = criteria_checks.get(achievement.unlock_criteria)
        if check_func:
            return check_func(event, profile, achievement)
        
        return False
    
    def _calculate_skill_progress(
        self,
        event: GamificationEvent,
        profile: PlayerProfile
    ) -> Dict[SkillArea, SkillPoints]:
        """Calculate skill point gains from event."""
        skill_updates = {}
        
        # Get skill allocations for event type
        allocations = self._rules.skill_points_per_action.get(event.event_type, {})
        
        # Add event-specific skills
        for skill in event.skills_affected:
            current = allocations.get(skill, SkillPoints(0))
            allocations[skill] = SkillPoints(current + 5)
        
        # Apply allocations
        for skill, points in allocations.items():
            skill_updates[skill] = points
        
        return skill_updates
    
    def _check_level_progression(
        self,
        current_xp: ExperiencePoints,
        new_xp: ExperiencePoints
    ) -> List[LevelNumber]:
        """Check if player leveled up."""
        current_level = self.calculate_level_from_xp(current_xp)
        new_level = self.calculate_level_from_xp(new_xp)
        
        level_ups = []
        for level in range(current_level + 1, new_level + 1):
            level_ups.append(LevelNumber(level))
        
        return level_ups
    
    def _update_challenge_progress(
        self,
        event: GamificationEvent,
        active_challenges: List[ChallengeId]
    ) -> List[ChallengeId]:
        """Update challenge progress and return completed ones."""
        # This would need challenge instances, not just IDs
        # In a real implementation, this would update challenge state
        return []
    
    def _get_badges_for_achievements(
        self,
        achievement_ids: List[AchievementId]
    ) -> List[BadgeId]:
        """Get badges associated with achievements."""
        badges = []
        for achievement_id in achievement_ids:
            for badge in self._badges.values():
                if badge.achievement_id == achievement_id:
                    badges.append(badge.id)
        return badges
    
    def _should_apply_streak_bonus(self, event: GamificationEvent) -> bool:
        """Check if streak bonus should apply to this event."""
        streak_eligible_events = {
            "suggestion_used",
            "translation_completed",
            "pattern_matched"
        }
        return event.event_type in streak_eligible_events
    
    def _create_feature_challenge(
        self,
        profile: PlayerProfile,
        current_date: datetime
    ) -> Challenge:
        """Create a daily challenge for using specific features."""
        return Challenge(
            id=ChallengeId(f"daily_feature_{current_date.date()}"),
            name="Feature Explorer",
            description="Use 5 different autocomplete suggestions",
            type=ChallengeType.DAILY,
            reward_xp=self._rules.xp_per_feature_challenge,
            target_value=1,
            current_value=0,
            expires_at=current_date + timedelta(days=self._rules.challenge_duration_days),
            skill_areas=[SkillArea.SYSTEM_KNOWLEDGE]
        )
    
    def _create_skill_challenge(
        self,
        profile: PlayerProfile,
        current_date: datetime
    ) -> Challenge:
        """Create a skill-based daily challenge."""
        # Find weakest skill
        weakest_skill = min(
            profile.skill_progress.items(),
            key=lambda x: x[1].current_points,
            default=(SkillArea.TEMPORAL_LOGIC, None)
        )[0]
        
        return Challenge(
            id=ChallengeId(f"daily_skill_{current_date.date()}"),
            name=f"Master {weakest_skill.value.replace('_', ' ').title()}",
            description=f"Complete 3 actions using {weakest_skill.value}",
            type=ChallengeType.DAILY,
            reward_xp=self._rules.xp_per_skill_challenge,
            target_value=3,
            current_value=0,
            expires_at=current_date + timedelta(days=self._rules.challenge_duration_days),
            skill_areas=[weakest_skill]
        )
    
    def _create_consistency_challenge(
        self,
        profile: PlayerProfile,
        current_date: datetime
    ) -> Challenge:
        """Create a consistency/streak challenge."""
        return Challenge(
            id=ChallengeId(f"daily_consistency_{current_date.date()}"),
            name="Consistent Learner",
            description="Complete 10 translations today",
            type=ChallengeType.DAILY,
            reward_xp=self._rules.xp_per_consistency_challenge,
            target_value=self._rules.consistency_challenge_days,
            current_value=profile.daily_streak, # Track against current streak
            expires_at=current_date + timedelta(days=self._rules.challenge_duration_days),
            skill_areas=[SkillArea.CONSISTENCY]
        )
    
    # Achievement checking helpers
    def _check_first_translation(
        self,
        event: GamificationEvent,
        profile: PlayerProfile,
        achievement: Achievement
    ) -> bool:
        """Check if this is user's first translation."""
        return event.event_type == "translation_completed"
    
    def _check_streak_achievement(
        self,
        event: GamificationEvent,
        profile: PlayerProfile,
        achievement: Achievement
    ) -> bool:
        """Check streak-based achievements."""
        required_streak = int(achievement.unlock_criteria.split("_")[1])
        return profile.daily_streak >= required_streak
    
    def _check_level_achievement(
        self,
        event: GamificationEvent,
        profile: PlayerProfile,
        achievement: Achievement
    ) -> bool:
        """Check level-based achievements."""
        required_level = int(achievement.unlock_criteria.split("_")[1])
        return profile.current_level >= required_level
    
    def _check_skill_achievement(
        self,
        event: GamificationEvent,
        profile: PlayerProfile,
        achievement: Achievement
    ) -> bool:
        """Check if all skills are at required level."""
        required_level = 5  # From "all_skills_5"
        for skill_progress in profile.skill_progress.values():
            if skill_progress.level < required_level:
                return False
        return True
    
    def _initialize_levels(self) -> List[Level]:
        """Initialize level progression."""
        return [
            Level(LevelNumber(1), "Novice", ExperiencePoints(0)),
            Level(LevelNumber(2), "Apprentice", ExperiencePoints(100)),
            Level(LevelNumber(3), "Practitioner", ExperiencePoints(250)),
            Level(LevelNumber(4), "Journeyman", ExperiencePoints(500)),
            Level(LevelNumber(5), "Expert", ExperiencePoints(1000)),
            Level(LevelNumber(6), "Master", ExperiencePoints(2000)),
            Level(LevelNumber(7), "Grandmaster", ExperiencePoints(3500)),
            Level(LevelNumber(8), "Sage", ExperiencePoints(5000)),
            Level(LevelNumber(9), "Oracle", ExperiencePoints(7500)),
            Level(LevelNumber(10), "Legend", ExperiencePoints(10000)),
        ]
    
    def _initialize_achievements(self) -> Dict[AchievementId, Achievement]:
        """Initialize achievement definitions."""
        achievements = [
            Achievement(
                id=AchievementId("first_translation"),
                name="First Steps",
                description="Complete your first translation",
                category=AchievementCategory.LEARNING,
                points=ExperiencePoints(50),
                icon_name="trophy_bronze",
                unlock_criteria="first_translation"
            ),
            Achievement(
                id=AchievementId("streak_7"),
                name="Week Warrior",
                description="Maintain a 7-day streak",
                category=AchievementCategory.CONSISTENCY,
                points=ExperiencePoints(100),
                icon_name="fire",
                unlock_criteria="streak_7"
            ),
            Achievement(
                id=AchievementId("level_10"),
                name="Legendary Status",
                description="Reach level 10",
                category=AchievementCategory.MASTERY,
                points=ExperiencePoints(500),
                icon_name="crown",
                unlock_criteria="level_10"
            ),
            Achievement(
                id=AchievementId("all_skills_5"),
                name="Well Rounded",
                description="Reach level 5 in all skills",
                category=AchievementCategory.MASTERY,
                points=ExperiencePoints(300),
                icon_name="star",
                unlock_criteria="all_skills_5"
            ),
        ]
        
        return {a.id: a for a in achievements}
    
    def _initialize_badges(self) -> Dict[BadgeId, Badge]:
        """Initialize badge definitions."""
        # Would be populated with badge definitions
        return {}