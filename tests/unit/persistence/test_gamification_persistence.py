import pytest
from pathlib import Path
from datetime import datetime, timedelta, timezone

from backend.unified.infrastructure.gamification_persistence import GamificationRepository
from backend.unified.domain.gamification_domain import (
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
)

class TestGamificationPersistence:
    """Test persistence layer."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary in-memory database and close after test."""
        # Uses :memory: by default, which is fine as long as the connection is persistent
        # for the duration of the test, which the refactored repository now ensures.
        repo = GamificationRepository() 
        yield repo
        repo.close()
    
    def test_save_and_load_profile(self, temp_db):
        """Test saving and loading profiles."""
        profile = PlayerProfile(
            user_id=UserId("test_user"),
            username="Test User",
            total_xp=ExperiencePoints(1234),
            current_level=LevelNumber(5),
            completed_achievements={AchievementId("ach1"), AchievementId("ach2")},
            earned_badges=set(),
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
            last_active=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        save_result = temp_db.save_profile(profile)
        assert save_result.is_success()
        
        load_result = temp_db.load_profile(profile.user_id)
        assert load_result.is_success()
        
        loaded = load_result.unwrap()
        assert loaded.user_id == profile.user_id
        assert loaded.username == profile.username
        assert loaded.total_xp == profile.total_xp
        assert loaded.current_level == profile.current_level
        assert loaded.completed_achievements == profile.completed_achievements
        assert loaded.daily_streak == profile.daily_streak

    def test_create_new_profile(self, temp_db):
        """Test creating a new profile from scratch."""
        user_id = UserId("new_user")
        profile = PlayerProfile.create_new(user_id, "Newbie")
        
        save_result = temp_db.save_profile(profile)
        assert save_result.is_success()
        
        load_result = temp_db.load_profile(user_id)
        assert load_result.is_success()
        loaded = load_result.unwrap()
        assert loaded.username == "Newbie"
        assert loaded.total_xp == 0

    def test_save_and_load_challenges(self, temp_db):
        """Test saving and loading challenges."""
        user_id = UserId("challenge_user")
        profile = PlayerProfile.create_new(user_id, "Challenger")
        temp_db.save_profile(profile)

        challenges = [
            Challenge(
                id=ChallengeId("daily_1"),
                name="Test Challenge",
                description="Complete test",
                type=ChallengeType.DAILY,
                reward_xp=ExperiencePoints(50),
                target_value=10,
                current_value=5,
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                skill_areas=[SkillArea.PATTERN_MATCHING]
            )
        ]
        
        save_result = temp_db.save_challenges(user_id, challenges)
        assert save_result.is_success()
        
        load_result = temp_db.load_challenges(user_id)
        assert load_result.is_success()
        
        loaded = load_result.unwrap()
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
                last_active=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
            temp_db.save_profile(profile)
        
        # Get leaderboard
        result = temp_db.get_leaderboard(limit=3)
        assert result.is_success()
        
        entries = result.unwrap()
        assert len(entries) == 3
        assert entries[0]["total_xp"] == 500
        assert entries[1]["total_xp"] == 400
        assert entries[2]["total_xp"] == 300

    def test_load_nonexistent_profile_fails(self, temp_db):
        """Test that loading a nonexistent profile returns a Failure."""
        result = temp_db.load_profile(UserId("no_such_user"))
        assert not result.is_success()
        failure = result.failure()
        assert failure.code == "PROFILE_NOT_FOUND"

import pytest
from pathlib import Path
from datetime import datetime, timedelta, timezone

from backend.unified.infrastructure.gamification_persistence import GamificationRepository
from backend.unified.domain.gamification_domain import (
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
)

class TestGamificationPersistence:
    """Test persistence layer."""
    
    @pytest.fixture
    def temp_db(self):
        """Create temporary in-memory database and close after test."""
        # Uses :memory: by default, which is fine as long as the connection is persistent
        # for the duration of the test, which the refactored repository now ensures.
        repo = GamificationRepository() 
        yield repo
        repo.close()
    
    def test_save_and_load_profile(self, temp_db):
        """Test saving and loading profiles."""
        profile = PlayerProfile(
            user_id=UserId("test_user"),
            username="Test User",
            total_xp=ExperiencePoints(1234),
            current_level=LevelNumber(5),
            completed_achievements={AchievementId("ach1"), AchievementId("ach2")},
            earned_badges=set(),
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
            last_active=datetime.now(timezone.utc),
            created_at=datetime.now(timezone.utc)
        )
        
        save_result = temp_db.save_profile(profile)
        assert save_result.is_success()
        
        load_result = temp_db.load_profile(profile.user_id)
        assert load_result.is_success()
        
        loaded = load_result.unwrap()
        assert loaded.user_id == profile.user_id
        assert loaded.username == profile.username
        assert loaded.total_xp == profile.total_xp
        assert loaded.current_level == profile.current_level
        assert loaded.completed_achievements == profile.completed_achievements
        assert loaded.daily_streak == profile.daily_streak

    def test_create_new_profile(self, temp_db):
        """Test creating a new profile from scratch."""
        user_id = UserId("new_user")
        profile = PlayerProfile.create_new(user_id, "Newbie")
        
        save_result = temp_db.save_profile(profile)
        assert save_result.is_success()
        
        load_result = temp_db.load_profile(user_id)
        assert load_result.is_success()
        loaded = load_result.unwrap()
        assert loaded.username == "Newbie"
        assert loaded.total_xp == 0

    def test_save_and_load_challenges(self, temp_db):
        """Test saving and loading challenges."""
        user_id = UserId("challenge_user")
        profile = PlayerProfile.create_new(user_id, "Challenger")
        temp_db.save_profile(profile)

        challenges = [
            Challenge(
                id=ChallengeId("daily_1"),
                name="Test Challenge",
                description="Complete test",
                type=ChallengeType.DAILY,
                reward_xp=ExperiencePoints(50),
                target_value=10,
                current_value=5,
                expires_at=datetime.now(timezone.utc) + timedelta(days=1),
                skill_areas=[SkillArea.PATTERN_MATCHING]
            )
        ]
        
        save_result = temp_db.save_challenges(user_id, challenges)
        assert save_result.is_success()
        
        load_result = temp_db.load_challenges(user_id)
        assert load_result.is_success()
        
        loaded = load_result.unwrap()
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
                last_active=datetime.now(timezone.utc),
                created_at=datetime.now(timezone.utc)
            )
            temp_db.save_profile(profile)
        
        # Get leaderboard
        result = temp_db.get_leaderboard(limit=3)
        assert result.is_success()
        
        entries = result.unwrap()
        assert len(entries) == 3
        assert entries[0]["total_xp"] == 500
        assert entries[1]["total_xp"] == 400
        assert entries[2]["total_xp"] == 300

    def test_load_nonexistent_profile_fails(self, temp_db):
        """Test that loading a nonexistent profile returns a Failure."""
        result = temp_db.load_profile(UserId("no_such_user"))
        assert not result.is_success()
        failure = result.failure()
        assert failure.code == "PROFILE_NOT_FOUND"