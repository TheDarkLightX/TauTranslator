#!/usr/bin/env python3
"""
TauTranslator PyQt6 Interface with Gamified Educational AutoComplete
Following the Intentional Disclosure Principle

Architecture:
- Core Layer: Pure gamification logic and domain types
- Infrastructure Layer: UI widgets, persistence, and external services
- Application Layer: Orchestration of gamification with UI

Copyright: DarkLightX/Dana Edwards
"""

import sys
from pathlib import Path
from typing import List, Optional, Dict, Set, Tuple, NewType
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum, auto
import json

# Domain Types (Rule 3: Maximize Disclosure via Type System)
UserId = NewType('UserId', str)
AchievementId = NewType('AchievementId', str)
ChallengeId = NewType('ChallengeId', str)
ExperiencePoints = NewType('ExperiencePoints', int)
Level = NewType('Level', int)
StreakDays = NewType('StreakDays', int)
KeywordText = NewType('KeywordText', str)
PatternText = NewType('PatternText', str)
NotificationMessage = NewType('NotificationMessage', str)

class AchievementStatus(Enum):
    LOCKED = "locked"
    UNLOCKED = "unlocked"

class ChallengeStatus(Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    EXPIRED = "expired"

class PointCategory(Enum):
    KEYWORD_USE = auto()
    PATTERN_COMPLETION = auto()
    TRANSLATION = auto()
    PERFECT_TRANSLATION = auto()
    CHALLENGE_COMPLETION = auto()
    ACHIEVEMENT_UNLOCK = auto()
    STREAK_BONUS = auto()

class KeywordCategory(Enum):
    TEMPORAL = "temporal"
    QUANTIFIER = "quantifier"
    OPERATOR = "operator"
    KEYWORD = "keyword"
    SOLVER = "solver"

# =======================
# Core Domain Layer (Pure Logic)
# =======================

@dataclass(frozen=True)
class Achievement:
    """Immutable achievement definition."""
    id: AchievementId
    name: str
    description: str
    icon: str
    points: ExperiencePoints
    requirement_description: str
    
@dataclass(frozen=True)
class AchievementProgress:
    """Current state of an achievement."""
    achievement_id: AchievementId
    status: AchievementStatus
    unlocked_at: Optional[datetime] = None

@dataclass(frozen=True)
class Challenge:
    """Immutable challenge definition."""
    id: ChallengeId
    title: str
    description: str
    target_type: str
    target_value: int
    reward_points: ExperiencePoints
    expires_at: datetime

@dataclass(frozen=True)
class ChallengeProgress:
    """Current progress on a challenge."""
    challenge_id: ChallengeId
    current_value: int
    status: ChallengeStatus
    completed_at: Optional[datetime] = None

@dataclass(frozen=True)
class GamificationState:
    """Complete gamification state (immutable)."""
    level: Level
    experience_points: ExperiencePoints
    total_points: ExperiencePoints
    current_streak: StreakDays
    longest_streak: StreakDays
    last_active: Optional[datetime]
    keywords_used: Dict[KeywordText, int]
    patterns_completed: Set[PatternText]
    translations_made: int
    perfect_translations: int
    achievement_progress: List[AchievementProgress]
    challenge_progress: List[ChallengeProgress]

@dataclass(frozen=True)
class PointsAwarded:
    """Result of awarding points."""
    points: ExperiencePoints
    category: PointCategory
    reason: str
    level_up: Optional[Level] = None

@dataclass(frozen=True)
class NotificationEvent:
    """Notification to display to user."""
    message: NotificationMessage
    type: str  # 'achievement', 'level_up', 'challenge', 'streak'
    icon: Optional[str] = None

class GamificationCalculator:
    """Pure logic for gamification calculations."""
    
    POINTS_CONFIG = {
        PointCategory.KEYWORD_USE: 1,
        PointCategory.PATTERN_COMPLETION: 5,
        PointCategory.TRANSLATION: 10,
        PointCategory.PERFECT_TRANSLATION: 20,
        PointCategory.CHALLENGE_COMPLETION: 50,
        PointCategory.ACHIEVEMENT_UNLOCK: 100,
        PointCategory.STREAK_BONUS: 2
    }
    
    LEVEL_THRESHOLDS = [0, 100, 250, 500, 1000, 1500, 2500, 4000, 6000, 9000, 15000]
    
    @staticmethod
    def calculate_level_from_experience(xp: ExperiencePoints) -> Level:
        """Calculate level from experience points."""
        for i, threshold in enumerate(GamificationCalculator.LEVEL_THRESHOLDS):
            if xp < threshold:
                return Level(i)
        return Level(len(GamificationCalculator.LEVEL_THRESHOLDS))
    
    @staticmethod
    def calculate_experience_for_next_level(current_level: Level, current_xp: ExperiencePoints) -> Tuple[int, int]:
        """Calculate XP progress towards next level."""
        if current_level >= len(GamificationCalculator.LEVEL_THRESHOLDS) - 1:
            return 100, 100  # Max level
        
        current_threshold = GamificationCalculator.LEVEL_THRESHOLDS[current_level - 1]
        next_threshold = GamificationCalculator.LEVEL_THRESHOLDS[current_level]
        
        xp_in_level = current_xp - current_threshold
        xp_needed = next_threshold - current_threshold
        
        return xp_in_level, xp_needed
    
    @staticmethod
    def calculate_streak_status(last_active: Optional[datetime], current_time: datetime) -> Tuple[StreakDays, bool]:
        """Calculate streak status. Returns (new_streak, is_broken)."""
        if not last_active:
            return StreakDays(1), False
        
        days_diff = (current_time.date() - last_active.date()).days
        
        if days_diff == 0:
            return StreakDays(0), False  # Same day, no change
        elif days_diff == 1:
            return StreakDays(1), False  # Increment
        else:
            return StreakDays(0), True  # Broken

class AchievementEvaluator:
    """Pure logic for evaluating achievement requirements."""
    
    @staticmethod
    def evaluate_achievement_unlocked(
        achievement: Achievement,
        state: GamificationState
    ) -> bool:
        """Check if achievement requirements are met."""
        requirement = achievement.requirement_description
        
        # Simple requirement parser (in production, use proper expression evaluator)
        if "keywords >= " in requirement:
            required = int(requirement.split(">=")[1].strip())
            unique_keywords = len([k for k, v in state.keywords_used.items() if v > 0])
            return unique_keywords >= required
        
        elif requirement == "temporal_all":
            temporal_keywords = {'always', 'sometimes', 'eventually', 'never'}
            return temporal_keywords.issubset(state.keywords_used.keys())
        
        elif requirement == "quantifier_mastery":
            return (state.keywords_used.get(KeywordText('forall'), 0) >= 5 and
                    state.keywords_used.get(KeywordText('exists'), 0) >= 5)
        
        elif "streak >= " in requirement:
            required = int(requirement.split(">=")[1].strip())
            return state.current_streak >= required
        
        elif "translations >= " in requirement:
            required = int(requirement.split(">=")[1].strip())
            return state.translations_made >= required
        
        elif "perfect >= " in requirement:
            required = int(requirement.split(">=")[1].strip())
            return state.perfect_translations >= required
        
        elif "level >= " in requirement:
            required = int(requirement.split(">=")[1].strip())
            return state.level >= required
        
        return False

class GamificationEngine:
    """Pure gamification logic engine."""
    
    def __init__(self, achievements: List[Achievement], calculator: GamificationCalculator):
        self.achievements = achievements
        self.calculator = calculator
        self.evaluator = AchievementEvaluator()
    
    def process_keyword_use(
        self,
        state: GamificationState,
        keyword: KeywordText,
        category: KeywordCategory
    ) -> Tuple[GamificationState, List[NotificationEvent]]:
        """Process keyword usage and return new state."""
        notifications = []
        
        # Update keyword count
        new_keywords = dict(state.keywords_used)
        new_keywords[keyword] = new_keywords.get(keyword, 0) + 1
        
        # Award points
        points_result = self._award_points(
            state,
            self.calculator.POINTS_CONFIG[PointCategory.KEYWORD_USE],
            f"Used keyword: {keyword}"
        )
        
        # Create new state
        new_state = GamificationState(
            level=points_result.level_up or state.level,
            experience_points=points_result.points + state.experience_points,
            total_points=points_result.points + state.total_points,
            current_streak=state.current_streak,
            longest_streak=state.longest_streak,
            last_active=state.last_active,
            keywords_used=new_keywords,
            patterns_completed=state.patterns_completed,
            translations_made=state.translations_made,
            perfect_translations=state.perfect_translations,
            achievement_progress=state.achievement_progress,
            challenge_progress=state.challenge_progress
        )
        
        # Add points notification
        if points_result.level_up:
            notifications.append(NotificationEvent(
                NotificationMessage(f"🎉 LEVEL UP! You're now level {points_result.level_up}!"),
                'level_up',
                '🎉'
            ))
        
        # Check achievements
        unlocked = self._check_achievements(state, new_state)
        notifications.extend(unlocked)
        
        return new_state, notifications
    
    def _award_points(
        self,
        state: GamificationState,
        points: int,
        reason: str
    ) -> PointsAwarded:
        """Calculate points award and check for level up."""
        new_xp = state.experience_points + points
        new_level = self.calculator.calculate_level_from_experience(ExperiencePoints(new_xp))
        
        level_up = new_level if new_level > state.level else None
        
        return PointsAwarded(
            points=ExperiencePoints(points),
            category=PointCategory.KEYWORD_USE,
            reason=reason,
            level_up=level_up
        )
    
    def _check_achievements(
        self,
        old_state: GamificationState,
        new_state: GamificationState
    ) -> List[NotificationEvent]:
        """Check for newly unlocked achievements."""
        notifications = []
        
        for achievement in self.achievements:
            # Find current progress
            old_progress = next(
                (p for p in old_state.achievement_progress if p.achievement_id == achievement.id),
                AchievementProgress(achievement.id, AchievementStatus.LOCKED)
            )
            
            if old_progress.status == AchievementStatus.LOCKED:
                if self.evaluator.evaluate_achievement_unlocked(achievement, new_state):
                    notifications.append(NotificationEvent(
                        NotificationMessage(
                            f"🏆 Achievement Unlocked: {achievement.icon} {achievement.name}!"
                        ),
                        'achievement',
                        achievement.icon
                    ))
        
        return notifications

# =======================
# Infrastructure Layer (I/O and External Dependencies)
# =======================

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTextEdit, QLabel, QPushButton, QComboBox, QProgressBar,
    QListWidget, QListWidgetItem, QSplitter, QFrame, QToolBar, 
    QStatusBar, QToolTip, QGroupBox, QDialog, QDialogButtonBox,
    QMessageBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QTimer, QPropertyAnimation,
    QEasingCurve, QRect, QPoint, QSettings, pyqtProperty
)
from PyQt6.QtGui import (
    QAction, QFont, QFontDatabase, QTextCharFormat, 
    QSyntaxHighlighter, QTextDocument, QTextCursor, QColor,
    QPalette, QLinearGradient, QPainter, QBrush
)

class GamificationRepository:
    """Repository for persisting gamification state."""
    
    def __init__(self, settings: QSettings):
        self.settings = settings
    
    def load_state_from_storage(self) -> Optional[GamificationState]:
        """Load gamification state from persistent storage."""
        try:
            data = self.settings.value("gamification_state")
            if data:
                return self._deserialize_state(data)
        except Exception:
            pass
        return None
    
    def save_state_to_storage(self, state: GamificationState) -> None:
        """Persist gamification state to storage."""
        data = self._serialize_state(state)
        self.settings.setValue("gamification_state", data)
    
    def _serialize_state(self, state: GamificationState) -> Dict:
        """Convert state to storable format."""
        return {
            'level': state.level,
            'experience_points': state.experience_points,
            'total_points': state.total_points,
            'current_streak': state.current_streak,
            'longest_streak': state.longest_streak,
            'last_active': state.last_active.isoformat() if state.last_active else None,
            'keywords_used': dict(state.keywords_used),
            'patterns_completed': list(state.patterns_completed),
            'translations_made': state.translations_made,
            'perfect_translations': state.perfect_translations,
            'achievement_progress': [
                {
                    'id': p.achievement_id,
                    'status': p.status.value,
                    'unlocked_at': p.unlocked_at.isoformat() if p.unlocked_at else None
                }
                for p in state.achievement_progress
            ],
            'challenge_progress': [
                {
                    'id': p.challenge_id,
                    'current': p.current_value,
                    'status': p.status.value,
                    'completed_at': p.completed_at.isoformat() if p.completed_at else None
                }
                for p in state.challenge_progress
            ]
        }
    
    def _deserialize_state(self, data: Dict) -> GamificationState:
        """Convert stored data to state object."""
        return GamificationState(
            level=Level(data['level']),
            experience_points=ExperiencePoints(data['experience_points']),
            total_points=ExperiencePoints(data['total_points']),
            current_streak=StreakDays(data['current_streak']),
            longest_streak=StreakDays(data['longest_streak']),
            last_active=datetime.fromisoformat(data['last_active']) if data['last_active'] else None,
            keywords_used={KeywordText(k): v for k, v in data['keywords_used'].items()},
            patterns_completed={PatternText(p) for p in data['patterns_completed']},
            translations_made=data['translations_made'],
            perfect_translations=data['perfect_translations'],
            achievement_progress=[
                AchievementProgress(
                    AchievementId(p['id']),
                    AchievementStatus(p['status']),
                    datetime.fromisoformat(p['unlocked_at']) if p['unlocked_at'] else None
                )
                for p in data['achievement_progress']
            ],
            challenge_progress=[
                ChallengeProgress(
                    ChallengeId(p['id']),
                    p['current'],
                    ChallengeStatus(p['status']),
                    datetime.fromisoformat(p['completed_at']) if p['completed_at'] else None
                )
                for p in data['challenge_progress']
            ]
        )

class NotificationWidget(QLabel):
    """UI widget for displaying notifications."""
    
    def __init__(self, notification: NotificationEvent, parent=None):
        message = f"{notification.icon} {notification.message}" if notification.icon else notification.message
        super().__init__(message, parent)
        self._setup_styling()
        self._setup_animation()
    
    def _setup_styling(self):
        """Configure widget styling."""
        self.setWindowFlags(Qt.WindowType.ToolTip)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 12px 20px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
        """)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
    
    def _setup_animation(self):
        """Configure show/hide animations."""
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        self.animation.finished.connect(self._start_hide_timer)
        
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide)
        self.hide_timer.setSingleShot(True)
    
    def show_animated_at_position(self, parent_center: QPoint):
        """Display notification with animation."""
        x = parent_center.x() - self.sizeHint().width() // 2
        start_y = -self.sizeHint().height()
        end_y = 50
        
        self.move(x, start_y)
        self.show()
        
        self.animation.setStartValue(QPoint(x, start_y))
        self.animation.setEndValue(QPoint(x, end_y))
        self.animation.start()
    
    def _start_hide_timer(self):
        """Start timer to hide notification."""
        self.hide_timer.start(3000)

# =======================
# Application Layer (Orchestration)
# =======================

class GamificationService:
    """Application service orchestrating gamification."""
    
    def __init__(self, repository: GamificationRepository):
        self.repository = repository
        self.engine = self._initialize_engine()
        self.state = self._load_or_create_state()
    
    def record_keyword_use_and_save(
        self,
        keyword: str,
        category: str
    ) -> List[NotificationEvent]:
        """Record keyword use and persist state (Rule 2: Orchestration)."""
        keyword_text = KeywordText(keyword)
        keyword_category = self._map_keyword_category(category)
        
        new_state, notifications = self.engine.process_keyword_use(
            self.state,
            keyword_text,
            keyword_category
        )
        
        self.state = new_state
        self.repository.save_state_to_storage(self.state)
        
        return notifications
    
    def get_current_level_progress(self) -> Tuple[int, int]:
        """Get XP progress for current level."""
        return GamificationCalculator.calculate_experience_for_next_level(
            self.state.level,
            self.state.experience_points
        )
    
    def _initialize_engine(self) -> GamificationEngine:
        """Initialize gamification engine with achievements."""
        achievements = self._create_achievement_definitions()
        calculator = GamificationCalculator()
        return GamificationEngine(achievements, calculator)
    
    def _load_or_create_state(self) -> GamificationState:
        """Load existing state or create new one."""
        state = self.repository.load_state_from_storage()
        if state:
            return state
        
        return GamificationState(
            level=Level(1),
            experience_points=ExperiencePoints(0),
            total_points=ExperiencePoints(0),
            current_streak=StreakDays(0),
            longest_streak=StreakDays(0),
            last_active=None,
            keywords_used={},
            patterns_completed=set(),
            translations_made=0,
            perfect_translations=0,
            achievement_progress=[],
            challenge_progress=[]
        )
    
    def _create_achievement_definitions(self) -> List[Achievement]:
        """Create achievement definitions."""
        return [
            Achievement(
                AchievementId("first_steps"),
                "First Steps",
                "Use your first TAU keyword",
                "👶",
                ExperiencePoints(10),
                "keywords >= 1"
            ),
            Achievement(
                AchievementId("novice"),
                "Novice Logician",
                "Use 10 different TAU keywords",
                "🎓",
                ExperiencePoints(50),
                "keywords >= 10"
            ),
            Achievement(
                AchievementId("temporal_master"),
                "Temporal Master",
                "Use all temporal operators",
                "⏰",
                ExperiencePoints(100),
                "temporal_all"
            ),
            Achievement(
                AchievementId("tau_master"),
                "TAU Master",
                "Reach level 10",
                "👑",
                ExperiencePoints(1000),
                "level >= 10"
            )
        ]
    
    def _map_keyword_category(self, category: str) -> KeywordCategory:
        """Map string category to enum."""
        mapping = {
            'temporal': KeywordCategory.TEMPORAL,
            'quantifier': KeywordCategory.QUANTIFIER,
            'operator': KeywordCategory.OPERATOR,
            'keyword': KeywordCategory.KEYWORD,
            'solver': KeywordCategory.SOLVER
        }
        return mapping.get(category, KeywordCategory.KEYWORD)

class GamifiedCodeEditor(QTextEdit):
    """Code editor with gamification integration."""
    
    notification_requested = pyqtSignal(NotificationEvent)
    
    def __init__(self, gamification_service: GamificationService, parent=None):
        super().__init__(parent)
        self.gamification_service = gamification_service
        self._setup_editor_appearance()
    
    def process_autocomplete_selection(self, suggestion_text: str, category: str):
        """Process autocomplete selection for gamification."""
        notifications = self.gamification_service.record_keyword_use_and_save(
            suggestion_text,
            category
        )
        
        for notification in notifications:
            self.notification_requested.emit(notification)
    
    def _setup_editor_appearance(self):
        """Configure editor appearance."""
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(12)
        self.setFont(font)

def main():
    """Application entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Tau Translator Gamified IDP")
    
    # Initialize infrastructure
    settings = QSettings("TauTranslator", "GamificationIDP")
    repository = GamificationRepository(settings)
    
    # Initialize application service
    gamification_service = GamificationService(repository)
    
    # Create and show main window
    window = QMainWindow()
    window.setWindowTitle("Tau Translator - Gamified (IDP)")
    window.setGeometry(100, 100, 1400, 900)
    
    # Simple demo UI
    editor = GamifiedCodeEditor(gamification_service)
    editor.notification_requested.connect(
        lambda event: NotificationWidget(event, window).show_animated_at_position(
            window.rect().center()
        )
    )
    
    window.setCentralWidget(editor)
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()