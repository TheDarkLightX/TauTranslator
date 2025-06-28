"""
Tests for the caching layer of the gamification system.

Copyright: DarkLightX / Dana Edwards
"""

from datetime import datetime

import pytest

from backend.unified.domain.gamification_types import (
    PlayerProfile, ExperiencePoints, LevelNumber, UserId, StreakCount
)
from backend.unified.infrastructure.gamification_persistence import GamificationCache
# Consistently including Result types, though not directly used in these specific cache tests
from src.tau_translator_omega.core_engine.result_enhanced import Success, Failure 


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
