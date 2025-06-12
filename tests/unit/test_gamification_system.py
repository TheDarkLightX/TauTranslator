"""
Comprehensive tests for the gamification system.

Tests domain logic, persistence, and integration points.

Copyright: DarkLightX / Dana Edwards
"""

import pytest
from datetime import datetime, timedelta
from pathlib import Path

from backend.unified.domain.gamification_types import (
    Achievement, AchievementId, Challenge, ChallengeId, PlayerProfile,
    ExperiencePoints, LevelNumber, SkillArea, SkillProgress, SkillPoints,
    UserId, StreakCount, AchievementCategory, ChallengeType,
    GamificationEvent, ProgressUpdate, GamificationRules
)
from backend.unified.domain.gamification_service import GamificationService
from backend.unified.infrastructure.gamification_persistence import (
    GamificationRepository, GamificationCache
)
from backend.unified.core.gamified_autocomplete_app import (
    GamifiedAutocompleteApplication
)
from backend.unified.core.result_enhanced import Success, Failure


class TestGamificationDomain:
    """Test pure domain logic for gamification."""
    
    def test_xp_calculation_basic(self):
        """Test basic XP calculation."""
        service = GamificationService()
        
        # Create test profile
        profile = self._create_test_profile()
        
        # Create test event
        event = GamificationEvent(
            event_type="suggestion_used",
            user_id=profile.user_id,
            timestamp=datetime.now(),
            metadata={},
            xp_earned=None,
            skills_affected=[]
        )
        
        # Process event
        result = service.process_event(event, profile)
        
        assert result.is_success()
        update = result.value
        assert update.xp_gained == 10  # Default for suggestion_used
    
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
    
    def _create_test_profile(self) -> PlayerProfile:
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
            daily_streak=StreakCount(3),
            last_active=datetime.now(),
            created_at=datetime.now()
        )


class TestGamificationPersistence:
    """Test persistence layer."""
    
    @pytest.fixture
    def temp_db(self, tmp_path):
        """Create temporary database."""
        db_path = tmp_path / "test_gamification.db"
        return GamificationRepository(db_path)
    
    def test_save_and_load_profile(self, temp_db):
        """Test saving and loading profiles."""
        # Create profile
        profile = PlayerProfile(
            user_id=UserId("test_user"),
            username="Test User",
            total_xp=ExperiencePoints(1234),
            current_level=LevelNumber(5),
            completed_achievements={AchievementId("ach1"), AchievementId("ach2")},
            earned_badges={},
            active_challenges=[],
            skill_progress={
                SkillArea.TEMPORAL_LOGIC: SkillProgress(
                    skill=SkillArea.TEMPORAL_LOGIC,
                    current_points=SkillPoints(50),
                    level=3,
                    next_level_points=SkillPoints(100),
                    unlocked_abilities=[]
                )
            },
            daily_streak=StreakCount(7),
            last_active=datetime.now(),
            created_at=datetime.now()
        )
        
        # Save
        save_result = temp_db.save_profile(profile)
        assert save_result.is_success()
        
        # Load
        load_result = temp_db.load_profile(profile.user_id)
        assert load_result.is_success()
        
        loaded = load_result.value
        assert loaded.user_id == profile.user_id
        assert loaded.username == profile.username
        assert loaded.total_xp == profile.total_xp
        assert loaded.current_level == profile.current_level
        assert loaded.completed_achievements == profile.completed_achievements
        assert loaded.daily_streak == profile.daily_streak
    
    def test_create_new_profile(self, temp_db):
        """Test creating new profile."""
        result = temp_db.create_profile(
            UserId("new_user"),
            "New User"
        )
        
        assert result.is_success()
        profile = result.value
        assert profile.user_id == "new_user"
        assert profile.username == "New User"
        assert profile.total_xp == 0
        assert profile.current_level == 1
    
    def test_save_and_load_challenges(self, temp_db):
        """Test saving and loading challenges."""
        user_id = UserId("test_user")
        
        challenges = [
            Challenge(
                id=ChallengeId("daily_1"),
                name="Test Challenge",
                description="Complete test",
                type=ChallengeType.DAILY,
                reward_xp=ExperiencePoints(50),
                target_value=10,
                current_value=5,
                expires_at=datetime.now() + timedelta(days=1),
                skill_areas=[SkillArea.PATTERN_MATCHING]
            )
        ]
        
        # Save
        save_result = temp_db.save_challenges(user_id, challenges)
        assert save_result.is_success()
        
        # Load
        load_result = temp_db.load_challenges(user_id)
        assert load_result.is_success()
        
        loaded = load_result.value
        assert len(loaded) == 1
        assert loaded[0].id == challenges[0].id
        assert loaded[0].current_value == 5
    
    def test_leaderboard(self, temp_db):
        """Test leaderboard functionality."""
        # Create multiple profiles
        for i in range(5):
            profile = PlayerProfile(
                user_id=UserId(f"user_{i}"),
                username=f"User {i}",
                total_xp=ExperiencePoints(100 * (5 - i)),
                current_level=LevelNumber(i + 1),
                completed_achievements=set(),
                earned_badges=set(),
                active_challenges=[],
                skill_progress={},
                daily_streak=StreakCount(0),
                last_active=datetime.now(),
                created_at=datetime.now()
            )
            temp_db.save_profile(profile)
        
        # Get leaderboard
        result = temp_db.get_leaderboard(limit=3)
        assert result.is_success()
        
        entries = result.value
        assert len(entries) == 3
        assert entries[0]["total_xp"] == 500
        assert entries[1]["total_xp"] == 400
        assert entries[2]["total_xp"] == 300


class TestGamificationCache:
    """Test caching functionality."""
    
    def test_cache_profile(self):
        """Test profile caching."""
        cache = GamificationCache()
        
        profile = PlayerProfile(
            user_id=UserId("test_user"),
            username="Test User",
            total_xp=ExperiencePoints(100),
            current_level=LevelNumber(2),
            completed_achievements=set(),
            earned_badges=set(),
            active_challenges=[],
            skill_progress={},
            daily_streak=StreakCount(0),
            last_active=datetime.now(),
            created_at=datetime.now()
        )
        
        # Cache profile
        cache.set_profile(profile)
        
        # Retrieve from cache
        cached = cache.get_profile(profile.user_id)
        assert cached is not None
        assert cached.user_id == profile.user_id
        assert cached.total_xp == profile.total_xp
    
    def test_cache_invalidation(self):
        """Test cache invalidation."""
        cache = GamificationCache()
        
        profile = PlayerProfile(
            user_id=UserId("test_user"),
            username="Test User",
            total_xp=ExperiencePoints(100),
            current_level=LevelNumber(2),
            completed_achievements=set(),
            earned_badges=set(),
            active_challenges=[],
            skill_progress={},
            daily_streak=StreakCount(0),
            last_active=datetime.now(),
            created_at=datetime.now()
        )
        
        # Cache and then invalidate
        cache.set_profile(profile)
        cache.invalidate_user(profile.user_id)
        
        # Should not be in cache
        assert cache.get_profile(profile.user_id) is None


class TestGamificationIntegration:
    """Test integration with autocomplete."""
    
    def test_autocomplete_with_gamification(self):
        """Test autocomplete request with XP tracking."""
        app = GamifiedAutocompleteApplication(
            user_id=UserId("test_user"),
            username="Test User"
        )
        
        # Create autocomplete request
        from backend.unified.core.autocomplete.models import (
            SuggestionRequest, SpecificationContext, LanguageMode,
            ContextType, DifficultyLevel, CursorPosition
        )
        
        context = SpecificationContext(
            full_text="forall x : ",
            cursor_position=CursorPosition(11),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.QUANTIFIER_EXPRESSION,
            parent_constructs=[],
            variables_in_scope=["x"],
            learning_level=DifficultyLevel.BEGINNER
        )
        
        request = SuggestionRequest(
            context=context,
            max_suggestions=5
        )
        
        # Process request
        result = app.process_autocomplete_request(request)
        
        assert result.is_success()
        response = result.value
        assert len(response.suggestions) > 0
    
    def test_suggestion_usage_tracking(self):
        """Test XP gain from using suggestions."""
        app = GamifiedAutocompleteApplication(
            user_id=UserId("test_user"),
            username="Test User"
        )
        
        # Get initial XP
        initial_xp = app._profile.total_xp if app._profile else 0
        
        # Create mock suggestion
        from backend.unified.core.autocomplete.models import (
            EducationalSuggestion, SuggestionText, DisplayText,
            HintText, ExampleCode, SuggestionCategory, ConfidenceScore,
            SpecificationContext, LanguageMode, ContextType,
            DifficultyLevel, CursorPosition
        )
        
        suggestion = EducationalSuggestion(
            text=SuggestionText("x > 0"),
            display=DisplayText("x > 0 - Positive constraint"),
            category=SuggestionCategory.PATTERN,
            description=HintText("Constrains x to positive values"),
            example=ExampleCode("forall x : x > 0 -> f(x) > 0"),
            difficulty=DifficultyLevel.BEGINNER,
            confidence=ConfidenceScore(0.9)
        )
        
        context = SpecificationContext(
            full_text="forall x : ",
            cursor_position=CursorPosition(11),
            language_mode=LanguageMode.TAU,
            context_type=ContextType.QUANTIFIER_EXPRESSION,
            parent_constructs=[],
            variables_in_scope=["x"]
        )
        
        # Use suggestion
        result = app.use_suggestion(suggestion, context)
        assert result.is_success()
        
        # Check XP increased
        if app._profile:
            assert app._profile.total_xp > initial_xp
    
    def test_translation_tracking(self):
        """Test XP gain from translations."""
        app = GamifiedAutocompleteApplication(
            user_id=UserId("test_user"),
            username="Test User"
        )
        
        # Get initial XP
        initial_xp = app._profile.total_xp if app._profile else 0
        
        # Complete translation
        result = app.complete_translation(
            "for all x such that x > 0",
            "forall x : x > 0",
            "TCE",
            "TAU"
        )
        
        assert result.is_success()
        
        # Check XP increased (25 XP for translations)
        if app._profile:
            assert app._profile.total_xp >= initial_xp + 25