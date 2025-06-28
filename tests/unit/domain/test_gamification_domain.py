"""
Tests for the domain logic of the gamification system.

Copyright: DarkLightX / Dana Edwards
"""

from datetime import datetime

import pytest

from backend.unified.domain.gamification_types import (
    PlayerProfile, ExperiencePoints, LevelNumber, SkillArea, UserId, StreakCount, 
    ChallengeType, GamificationEvent
)
from backend.unified.domain.gamification_service import GamificationService
from src.tau_translator_omega.core_engine.result_enhanced import Success, Failure # Updated import


class TestGamificationDomain:
    """Test pure domain logic for gamification."""
    
    def test_xp_calculation_basic(self):
        """Test basic XP calculation without streak bonuses."""
        service = GamificationService()

        # GIVEN a player profile with no active streak
        profile = self._create_test_profile(daily_streak=StreakCount(1))

        # WHEN a standard event occurs
        event = GamificationEvent(
            event_type="suggestion_used",
            user_id=profile.user_id,
            timestamp=datetime.now(),
            metadata={},
            xp_earned=None,
            skills_affected=[]
        )
        result = service.process_event(event, profile)

        # THEN the base XP is awarded
        assert result.is_success()
        update = result.value
        assert update.xp_gained == 10

    def test_xp_calculation_with_streak_bonus(self):
        """Test that XP calculations correctly apply streak bonuses."""
        service = GamificationService()

        # GIVEN a player profile with an active streak of 3 days
        profile = self._create_test_profile(daily_streak=StreakCount(3))

        # WHEN a standard event occurs
        event = GamificationEvent(
            event_type="suggestion_used",
            user_id=profile.user_id,
            timestamp=datetime.now(),
            metadata={},
            xp_earned=None,
            skills_affected=[]
        )
        result = service.process_event(event, profile)

        # THEN the XP awarded includes the streak bonus
        assert result.is_success()
        update = result.value
        # Base XP is 10. Bonus for 3 days is 1.5^3 = 3.375. 10 * 3.375 = 33.75, cast to int is 33.
        assert update.xp_gained == 33
    
    def test_streak_bonus_calculation(self):
        """Test streak bonus multiplier."""
        service = GamificationService()
        
        # Test various streak counts
        base_xp = ExperiencePoints(10)
        
        # No streak
        assert service.calculate_streak_bonus(base_xp, StreakCount(0)) == 10
        assert service.calculate_streak_bonus(base_xp, StreakCount(1)) == 10
        
        # Active streak
        assert service.calculate_streak_bonus(base_xp, StreakCount(2)) > 10
        assert service.calculate_streak_bonus(base_xp, StreakCount(7)) > 20
        
        # Verify cap
        assert service.calculate_streak_bonus(base_xp, StreakCount(20)) <= 50
    
    def test_level_progression(self):
        """Test level calculation from XP."""
        service = GamificationService()
        
        # Test level boundaries
        assert service.calculate_level_from_xp(ExperiencePoints(0)) == 1
        assert service.calculate_level_from_xp(ExperiencePoints(99)) == 1
        assert service.calculate_level_from_xp(ExperiencePoints(100)) == 2
        assert service.calculate_level_from_xp(ExperiencePoints(250)) == 3
        assert service.calculate_level_from_xp(ExperiencePoints(10000)) == 10
    
    def test_achievement_unlocking(self):
        """Test achievement unlock logic."""
        service = GamificationService()
        profile = self._create_test_profile()
        
        # First translation achievement
        event = GamificationEvent(
            event_type="translation_completed",
            user_id=profile.user_id,
            timestamp=datetime.now(),
            metadata={},
            xp_earned=None,
            skills_affected=[]
        )
        
        result = service.process_event(event, profile)
        assert result.is_success()
        
        update = result.value
        assert any("first_translation" in aid for aid in update.achievements_unlocked)
    
    def test_challenge_generation(self):
        """Test daily challenge generation."""
        service = GamificationService()
        profile = self._create_test_profile()
        
        challenges = service.generate_daily_challenges(profile, datetime.now())
        
        assert len(challenges) == 3
        assert all(c.type == ChallengeType.DAILY for c in challenges)
        assert all(c.target_value > 0 for c in challenges)
        assert all(c.reward_xp > 0 for c in challenges)
    
    def test_skill_progression(self):
        """Test skill point allocation."""
        service = GamificationService()
        profile = self._create_test_profile()
        
        # Use temporal logic
        event = GamificationEvent(
            event_type="temporal_usage",
            user_id=profile.user_id,
            timestamp=datetime.now(),
            metadata={},
            xp_earned=None,
            skills_affected=[SkillArea.TEMPORAL_LOGIC]
        )
        
        result = service.process_event(event, profile)
        assert result.is_success()
        
        update = result.value
        assert SkillArea.TEMPORAL_LOGIC in update.skill_improvements
        assert update.skill_improvements[SkillArea.TEMPORAL_LOGIC] > 0
    
    def _create_test_profile(self, daily_streak: StreakCount = StreakCount(3)) -> PlayerProfile:
        """Create a test player profile."""
        return PlayerProfile(
            user_id=UserId("test_user"),
            username="Test User",
            total_xp=ExperiencePoints(500),
            current_level=LevelNumber(4),
            completed_achievements=set(),
            earned_badges=set(),
            active_challenges=[],
            skill_progress={},
            daily_streak=daily_streak,
            last_active=datetime.now(),
            created_at=datetime.now()
        )
