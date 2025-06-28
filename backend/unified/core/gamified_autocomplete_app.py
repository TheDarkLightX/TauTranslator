"""
Application layer for gamified educational autocomplete.

Orchestrates domain logic, UI, and persistence layers.
Follows Rule 2: Public methods orchestrate, private methods implement.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Optional, List, Dict
from datetime import datetime
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QWidget, QMessageBox

from ..core.result_enhanced import Result, Success, Failure
from ..domain.gamification_types import (
    PlayerProfile, Challenge, Achievement, GamificationEvent,
    ExperiencePoints, UserId, SkillArea, ProgressUpdate
)
from ..domain.gamification_service import GamificationService
from ..infrastructure.gamification_persistence import (
    GamificationRepository
)
from ..infrastructure.gamification_ui import GamificationDashboard
from .autocomplete.educational_autocomplete_service import (
    EducationalAutocompleteService,
    SuggestionRequest, SuggestionResponse, SpecificationContext
)
from .autocomplete.models import EducationalSuggestion

class GamifiedAutocompleteApplication(QObject):
    """
    Main application class orchestrating gamified autocomplete.
    
    Integrates educational autocomplete with gamification mechanics.
    Manages UI updates, persistence, and event processing.
    """
    
    # Signals for UI updates
    profile_updated = pyqtSignal(PlayerProfile)
    achievement_unlocked = pyqtSignal(Achievement)
    level_up = pyqtSignal(int)
    xp_gained = pyqtSignal(int)
    
    def __init__(
        self,
        user_id: Optional[UserId] = None,
        username: Optional[str] = None
    ):
        """Initialize application with user info."""
        super().__init__()
        
        # Core services
        self._gamification_service = GamificationService()
        self._autocomplete_service = EducationalAutocompleteService()
        self._repository = GamificationRepository()
        # self._cache = GamificationCache() # TODO: Refactor or replace caching mechanism
        
        # User state
        self._user_id = user_id or UserId("default_user")
        self._username = username or "Learner"
        self._profile: Optional[PlayerProfile] = None
        self._daily_challenges: List[Challenge] = []
        
        # UI components (created on demand)
        self._dashboard: Optional[GamificationDashboard] = None
        
        # Session tracking
        self._session_start = datetime.now()
        self._actions_count = 0
        
        # Auto-save timer
        self._save_timer = QTimer()
        self._save_timer.timeout.connect(self._auto_save)
        self._save_timer.start(60000)  # Save every minute
        
        # Initialize user profile
        self._initialize_profile()
    
    # =======================
    # Public API Methods (Rule 2: Orchestration)
    # =======================
    
    def get_dashboard_widget(self) -> GamificationDashboard:
        """Get or create gamification dashboard widget."""
        if not self._dashboard and self._profile:
            self._dashboard = GamificationDashboard(self._profile)
            self._dashboard.challenge_clicked.connect(self._handle_challenge_click)
            self._dashboard.achievement_clicked.connect(self._handle_achievement_click)
        
        return self._dashboard
    
    def process_autocomplete_request(
        self,
        request: SuggestionRequest
    ) -> Result[SuggestionResponse]:
        """
        Process autocomplete request with gamification tracking.
        
        Tracks usage for XP and achievement progress.
        """
        # Get suggestions
        response_result = self._autocomplete_service.get_suggestions_async(request)
        if not response_result.is_success():
            return response_result
        
        response = response_result.value
        
        # Track event for gamification
        self._track_autocomplete_event(request.context)
        
        # Enhance response with gamification hints
        enhanced_response = self._enhance_response_with_gamification(response)
        
        return Success(enhanced_response)
    
    def use_suggestion(
        self,
        suggestion: EducationalSuggestion,
        context: SpecificationContext
    ) -> Result[None]:
        """
        Track when a suggestion is used.
        
        Awards XP and updates achievements.
        """
        # Create gamification event
        event = GamificationEvent(
            event_type="suggestion_used",
            user_id=self._user_id,
            timestamp=datetime.now(),
            metadata={
                "suggestion_text": suggestion.text,
                "category": suggestion.category.value,
                "difficulty": suggestion.difficulty.value
            },
            xp_earned=self._calculate_suggestion_xp(suggestion),
            skills_affected=self._get_skills_for_category(suggestion.category)
        )
        
        # Process event
        return self._process_gamification_event(event)
    
    def complete_translation(
        self,
        source_text: str,
        translated_text: str,
        language_from: str,
        language_to: str
    ) -> Result[None]:
        """
        Track translation completion.
        
        Awards significant XP and progress.
        """
        # Create gamification event
        event = GamificationEvent(
            event_type="translation_completed",
            user_id=self._user_id,
            timestamp=datetime.now(),
            metadata={
                "source_length": len(source_text),
                "language_from": language_from,
                "language_to": language_to
            },
            xp_earned=ExperiencePoints(25),
            skills_affected=[SkillArea.TRANSLATION]
        )
        
        # Process event
        return self._process_gamification_event(event)
    
    def get_daily_challenges(self) -> List[Challenge]:
        """Get today's challenges, generating if needed."""
        if not self._daily_challenges or self._should_refresh_challenges():
            self._daily_challenges = self._gamification_service.generate_daily_challenges(
                self._profile,
                datetime.now()
            )
            
            # Save challenges
            self._repository.save_challenges(
                self._user_id,
                self._daily_challenges
            )
        
        return self._daily_challenges
    
    def get_next_achievements(self) -> List[Achievement]:
        """Get achievements close to being unlocked."""
        if not self._profile:
            return []
        
        return self._gamification_service.get_next_achievements(self._profile)
    
    def save_progress(self) -> Result[None]:
        """Manually save current progress."""
        if not self._profile:
            return Failure("NO_PROFILE", "No profile to save")
        
        # Update last active time
        self._profile = self._update_profile_time(self._profile)
        
        # Save to repository
        save_result = self._repository.save_profile(self._profile)
        if save_result.is_success():
            self._cache.set_profile(self._profile)
        
        return save_result
    
    # =======================
    # Private Implementation Methods
    # =======================
    
    def _initialize_profile(self):
        """Load or create user profile."""
        # Try cache first
        cached = self._cache.get_profile(self._user_id)
        if cached:
            self._profile = cached
            self._check_daily_reset()
            return
        
        # Try loading from repository
        load_result = self._repository.load_profile(self._user_id)
        if load_result.is_success():
            self._profile = load_result.value
            self._cache.set_profile(self._profile)
            self._check_daily_reset()
        else:
            # Create new profile
            create_result = self._repository.create_profile(
                self._user_id,
                self._username
            )
            if create_result.is_success():
                self._profile = create_result.value
                self._cache.set_profile(self._profile)
    
    def _process_gamification_event(
        self,
        event: GamificationEvent
    ) -> Result[None]:
        """Process a gamification event and update profile."""
        if not self._profile:
            return Failure("NO_PROFILE", "Profile not initialized")
        
        # Process event through gamification service
        update_result = self._gamification_service.process_event(
            event,
            self._profile
        )
        
        if not update_result.is_success():
            return update_result
        
        update = update_result.value
        
        # Apply updates to profile
        self._profile = self._apply_progress_update(self._profile, update)
        
        # Update cache
        self._cache.set_profile(self._profile)
        
        # Emit signals for UI updates
        self._emit_update_signals(update)
        
        # Update UI if dashboard exists
        if self._dashboard:
            self._dashboard.update_profile(self._profile)
        
        # Increment action count
        self._actions_count += 1
        
        return Success(None)
    
    def _apply_progress_update(
        self,
        profile: PlayerProfile,
        update: ProgressUpdate
    ) -> PlayerProfile:
        """Apply progress update to profile."""
        # Calculate new values
        new_xp = ExperiencePoints(profile.total_xp + update.xp_gained)
        new_level = self._gamification_service.calculate_level_from_xp(new_xp)
        
        # Update achievements
        new_achievements = profile.completed_achievements.copy()
        new_achievements.update(update.achievements_unlocked)
        
        # Update badges
        new_badges = profile.earned_badges.copy()
        new_badges.update(update.badges_earned)
        
        # Update skills
        new_skills = profile.skill_progress.copy()
        for skill, points in update.skill_improvements.items():
            current = new_skills.get(skill)
            if current:
                # Update existing skill
                new_points = current.current_points + points
                new_skills[skill] = current.__class__(
                    skill=skill,
                    current_points=new_points,
                    level=current.level,  # Would calculate new level
                    next_level_points=current.next_level_points,
                    unlocked_abilities=current.unlocked_abilities
                )
        
        # Create updated profile
        from dataclasses import replace
        return replace(
            profile,
            total_xp=new_xp,
            current_level=new_level,
            completed_achievements=new_achievements,
            earned_badges=new_badges,
            skill_progress=new_skills,
            last_active=datetime.now()
        )
    
    def _emit_update_signals(self, update: ProgressUpdate):
        """Emit Qt signals for UI updates."""
        if update.xp_gained > 0:
            self.xp_gained.emit(update.xp_gained)
        
        for achievement_id in update.achievements_unlocked:
            # Get achievement details
            achievement = self._get_achievement_by_id(achievement_id)
            if achievement:
                self.achievement_unlocked.emit(achievement)
        
        for level in update.level_ups:
            self.level_up.emit(level)
        
        self.profile_updated.emit(self._profile)
    
    def _track_autocomplete_event(self, context: SpecificationContext):
        """Track autocomplete usage for analytics."""
        # Could track pattern usage, context types, etc.
        # For now, just increment counter
        self._actions_count += 1
    
    def _enhance_response_with_gamification(
        self,
        response: SuggestionResponse
    ) -> SuggestionResponse:
        """Add gamification hints to autocomplete response."""
        # Could add hints about XP potential, achievement progress, etc.
        return response
    
    def _calculate_suggestion_xp(
        self,
        suggestion: EducationalSuggestion
    ) -> ExperiencePoints:
        """Calculate XP value for using a suggestion."""
        base_xp = 10
        
        # Bonus for difficulty
        difficulty_bonus = {
            "beginner": 0,
            "intermediate": 5,
            "advanced": 10
        }
        
        bonus = difficulty_bonus.get(suggestion.difficulty.value, 0)
        
        return ExperiencePoints(base_xp + bonus)
    
    def _get_skills_for_category(self, category) -> List[SkillArea]:
        """Map suggestion category to skill areas."""
        category_skills = {
            "temporal": [SkillArea.TEMPORAL_LOGIC],
            "quantifier": [SkillArea.QUANTIFIERS],
            "stream": [SkillArea.STREAM_PROCESSING],
            "solver": [SkillArea.SOLVER_CONSTRAINTS],
            "definition": [SkillArea.FUNCTION_DEFINITIONS],
            "pattern": [SkillArea.PATTERN_MATCHING]
        }
        
        return category_skills.get(category.value, [])
    
    def _check_daily_reset(self):
        """Check if daily streak should reset."""
        if not self._profile:
            return
        
        last_active_date = self._profile.last_active.date()
        today = datetime.now().date()
        
        days_diff = (today - last_active_date).days
        
        if days_diff > 1:
            # Streak broken
            self._repository.update_streak(self._user_id, 0)
            from dataclasses import replace
            self._profile = replace(self._profile, daily_streak=0)
        elif days_diff == 1:
            # Extend streak
            new_streak = self._profile.daily_streak + 1
            self._repository.update_streak(self._user_id, new_streak)
            from dataclasses import replace
            self._profile = replace(self._profile, daily_streak=new_streak)
    
    def _should_refresh_challenges(self) -> bool:
        """Check if challenges need refresh."""
        if not self._daily_challenges:
            return True
        
        # Check if any challenge expired
        now = datetime.now()
        return any(c.is_expired(now) for c in self._daily_challenges)
    
    def _update_profile_time(self, profile: PlayerProfile) -> PlayerProfile:
        """Update profile's last active time."""
        from dataclasses import replace
        return replace(profile, last_active=datetime.now())
    
    def _get_achievement_by_id(
        self,
        achievement_id: str
    ) -> Optional[Achievement]:
        """Get achievement details by ID."""
        # Would look up from gamification service
        # For now, return None
        return None
    
    def _auto_save(self):
        """Auto-save progress periodically."""
        if self._profile and self._actions_count > 0:
            self.save_progress()
            self._actions_count = 0
    
    def _handle_challenge_click(self, challenge: Challenge):
        """Handle challenge click from UI."""
        # Could show challenge details dialog
        pass
    
    def _handle_achievement_click(self, achievement: Achievement):
        """Handle achievement click from UI."""
        # Show achievement details
        msg = QMessageBox()
        msg.setWindowTitle(achievement.name)
        msg.setText(f"{achievement.description}\n\n+{achievement.points} XP")
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()