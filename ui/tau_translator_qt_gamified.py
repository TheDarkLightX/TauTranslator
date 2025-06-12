#!/usr/bin/env python3
"""
TauTranslator PyQt6 Interface with Gamified Educational AutoComplete

Enhanced version with gamification elements including:
- Achievement system
- Progress tracking
- Challenges and quests
- Skill points and levels
- Streak counters

Copyright: DarkLightX/Dana Edwards
"""

import sys
import json
import random
from pathlib import Path
from typing import List, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import requests

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

# Import base components
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
from tau_translator_desktop_qt import TauSyntaxHighlighter
from tau_translator_qt_educational import (
    EducationalSuggestion, 
    EducationalAutocompleteService,
    EducationalSuggestionWidget,
    CodeEditorWithEducationalAutoComplete
)


@dataclass
class Achievement:
    """Achievement/Badge definition."""
    id: str
    name: str
    description: str
    icon: str  # Emoji icon
    points: int
    requirement: str
    unlocked: bool = False
    unlocked_at: Optional[datetime] = None


@dataclass
class Challenge:
    """Daily/Weekly challenge."""
    id: str
    title: str
    description: str
    target_type: str  # 'keywords', 'translations', 'streak', etc
    target_value: int
    current_value: int = 0
    reward_points: int = 10
    completed: bool = False
    expires_at: datetime = field(default_factory=lambda: datetime.now() + timedelta(days=1))


@dataclass
class UserProgress:
    """User progress and statistics."""
    level: int = 1
    experience_points: int = 0
    total_points: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_active: Optional[datetime] = None
    
    # Statistics
    keywords_used: Dict[str, int] = field(default_factory=dict)
    patterns_completed: Set[str] = field(default_factory=set)
    translations_made: int = 0
    perfect_completions: int = 0
    
    # Achievements
    achievements: List[Achievement] = field(default_factory=list)
    
    # Active challenges
    challenges: List[Challenge] = field(default_factory=list)


class GamificationService:
    """Service managing gamification features."""
    
    def __init__(self):
        self.settings = QSettings("TauTranslator", "Gamification")
        self.progress = self._load_progress()
        self._init_achievements()
        self._init_daily_challenges()
        
        # Points configuration
        self.POINTS_CONFIG = {
            'keyword_used': 1,
            'pattern_completed': 5,
            'translation_made': 10,
            'perfect_completion': 20,
            'challenge_completed': 50,
            'achievement_unlocked': 100,
            'streak_bonus': 2  # per day
        }
        
        # Level thresholds
        self.LEVEL_THRESHOLDS = [0, 100, 250, 500, 1000, 1500, 2500, 4000, 6000, 9000, 15000]
    
    def _load_progress(self) -> UserProgress:
        """Load user progress from settings."""
        try:
            data = self.settings.value("progress", {})
            if data:
                # Reconstruct UserProgress from saved data
                progress = UserProgress()
                progress.level = data.get('level', 1)
                progress.experience_points = data.get('experience_points', 0)
                progress.total_points = data.get('total_points', 0)
                progress.current_streak = data.get('current_streak', 0)
                progress.longest_streak = data.get('longest_streak', 0)
                progress.keywords_used = data.get('keywords_used', {})
                progress.patterns_completed = set(data.get('patterns_completed', []))
                progress.translations_made = data.get('translations_made', 0)
                progress.perfect_completions = data.get('perfect_completions', 0)
                
                last_active = data.get('last_active')
                if last_active:
                    progress.last_active = datetime.fromisoformat(last_active)
                
                return progress
        except:
            pass
        
        return UserProgress()
    
    def save_progress(self):
        """Save user progress to settings."""
        data = {
            'level': self.progress.level,
            'experience_points': self.progress.experience_points,
            'total_points': self.progress.total_points,
            'current_streak': self.progress.current_streak,
            'longest_streak': self.progress.longest_streak,
            'keywords_used': self.progress.keywords_used,
            'patterns_completed': list(self.progress.patterns_completed),
            'translations_made': self.progress.translations_made,
            'perfect_completions': self.progress.perfect_completions,
            'last_active': self.progress.last_active.isoformat() if self.progress.last_active else None
        }
        self.settings.setValue("progress", data)
    
    def _init_achievements(self):
        """Initialize achievement definitions."""
        self.achievement_definitions = [
            Achievement("first_steps", "First Steps", "Use your first TAU keyword", "👶", 10, "keywords >= 1"),
            Achievement("novice", "Novice Logician", "Use 10 different TAU keywords", "🎓", 50, "keywords >= 10"),
            Achievement("temporal_master", "Temporal Master", "Use all temporal operators", "⏰", 100, "temporal_all"),
            Achievement("quantifier_expert", "Quantifier Expert", "Master forall and exists", "∀", 100, "quantifier_mastery"),
            Achievement("streak_week", "Week Warrior", "Maintain a 7-day streak", "🔥", 200, "streak >= 7"),
            Achievement("translator", "Translator", "Complete 10 translations", "🔄", 150, "translations >= 10"),
            Achievement("perfectionist", "Perfectionist", "5 perfect completions", "⭐", 300, "perfect >= 5"),
            Achievement("challenger", "Challenge Champion", "Complete 5 daily challenges", "🏆", 500, "challenges >= 5"),
            Achievement("tau_master", "TAU Master", "Reach level 10", "👑", 1000, "level >= 10")
        ]
        
        # Load unlocked achievements
        unlocked = self.settings.value("unlocked_achievements", [])
        for achievement in self.achievement_definitions:
            if achievement.id in unlocked:
                achievement.unlocked = True
    
    def _init_daily_challenges(self):
        """Initialize daily challenges."""
        # Check if we need new challenges
        last_challenge_date = self.settings.value("last_challenge_date")
        today = datetime.now().date().isoformat()
        
        if last_challenge_date != today:
            # Generate new daily challenges
            self.progress.challenges = [
                Challenge(
                    "daily_keywords",
                    "Keyword Explorer",
                    "Use 5 different TAU keywords today",
                    "keywords",
                    5,
                    reward_points=30
                ),
                Challenge(
                    "daily_translations",
                    "Translation Practice",
                    "Complete 3 translations",
                    "translations",
                    3,
                    reward_points=50
                ),
                Challenge(
                    "daily_pattern",
                    "Pattern Master",
                    "Complete a 'forall' pattern correctly",
                    "pattern",
                    1,
                    reward_points=40
                )
            ]
            self.settings.setValue("last_challenge_date", today)
    
    def check_streak(self):
        """Update streak status."""
        now = datetime.now()
        
        if self.progress.last_active:
            days_diff = (now.date() - self.progress.last_active.date()).days
            
            if days_diff == 0:
                # Same day, no change
                pass
            elif days_diff == 1:
                # Next day, increment streak
                self.progress.current_streak += 1
                self.progress.longest_streak = max(
                    self.progress.longest_streak,
                    self.progress.current_streak
                )
                # Streak bonus points
                bonus = self.progress.current_streak * self.POINTS_CONFIG['streak_bonus']
                self.add_points(bonus, f"Streak bonus: {self.progress.current_streak} days!")
            else:
                # Streak broken
                if self.progress.current_streak > 0:
                    self.progress.current_streak = 0
                    return "streak_broken"
        else:
            # First time
            self.progress.current_streak = 1
        
        self.progress.last_active = now
        self.save_progress()
        return "streak_maintained"
    
    def record_keyword_use(self, keyword: str, category: str) -> List[str]:
        """Record keyword usage and check achievements."""
        self.progress.keywords_used[keyword] = self.progress.keywords_used.get(keyword, 0) + 1
        points = self.POINTS_CONFIG['keyword_used']
        
        notifications = []
        notifications.append(self.add_points(points, f"Used keyword: {keyword}"))
        
        # Check achievements
        unlocked = self._check_keyword_achievements(category)
        notifications.extend(unlocked)
        
        # Update challenges
        for challenge in self.progress.challenges:
            if challenge.target_type == "keywords" and not challenge.completed:
                challenge.current_value = len([k for k, v in self.progress.keywords_used.items() if v > 0])
                if challenge.current_value >= challenge.target_value:
                    challenge.completed = True
                    notifications.append(self._complete_challenge(challenge))
        
        self.save_progress()
        return notifications
    
    def record_pattern_completion(self, pattern: str) -> List[str]:
        """Record successful pattern completion."""
        self.progress.patterns_completed.add(pattern)
        points = self.POINTS_CONFIG['pattern_completed']
        
        notifications = []
        notifications.append(self.add_points(points, f"Pattern completed: {pattern}"))
        
        # Check pattern challenges
        for challenge in self.progress.challenges:
            if challenge.target_type == "pattern" and pattern.lower() in challenge.description.lower():
                if not challenge.completed:
                    challenge.completed = True
                    notifications.append(self._complete_challenge(challenge))
        
        self.save_progress()
        return notifications
    
    def record_translation(self, perfect: bool = False) -> List[str]:
        """Record translation completion."""
        self.progress.translations_made += 1
        
        notifications = []
        if perfect:
            self.progress.perfect_completions += 1
            points = self.POINTS_CONFIG['perfect_completion']
            notifications.append(self.add_points(points, "Perfect translation! ⭐"))
        else:
            points = self.POINTS_CONFIG['translation_made']
            notifications.append(self.add_points(points, "Translation completed!"))
        
        # Check achievements
        unlocked = self._check_translation_achievements()
        notifications.extend(unlocked)
        
        # Update challenges
        for challenge in self.progress.challenges:
            if challenge.target_type == "translations" and not challenge.completed:
                challenge.current_value = self.progress.translations_made
                if challenge.current_value >= challenge.target_value:
                    challenge.completed = True
                    notifications.append(self._complete_challenge(challenge))
        
        self.save_progress()
        return notifications
    
    def add_points(self, points: int, reason: str) -> str:
        """Add experience points and check for level up."""
        self.progress.experience_points += points
        self.progress.total_points += points
        
        # Check for level up
        old_level = self.progress.level
        new_level = self._calculate_level(self.progress.experience_points)
        
        if new_level > old_level:
            self.progress.level = new_level
            return f"🎉 LEVEL UP! You're now level {new_level}! (+{points} XP: {reason})"
        
        return f"+{points} XP: {reason}"
    
    def _calculate_level(self, xp: int) -> int:
        """Calculate level from XP."""
        for i, threshold in enumerate(self.LEVEL_THRESHOLDS):
            if xp < threshold:
                return i
        return len(self.LEVEL_THRESHOLDS)
    
    def _check_keyword_achievements(self, category: str) -> List[str]:
        """Check and unlock keyword-related achievements."""
        notifications = []
        unique_keywords = len([k for k, v in self.progress.keywords_used.items() if v > 0])
        
        # Check temporal mastery
        temporal_keywords = {'always', 'sometimes', 'eventually', 'never'}
        if category == 'temporal' and temporal_keywords.issubset(self.progress.keywords_used.keys()):
            notifications.extend(self._unlock_achievement("temporal_master"))
        
        # Check quantifier mastery
        quantifier_keywords = {'forall', 'exists'}
        if category == 'quantifier' and all(
            self.progress.keywords_used.get(k, 0) >= 5 for k in quantifier_keywords
        ):
            notifications.extend(self._unlock_achievement("quantifier_expert"))
        
        # Check general keyword achievements
        if unique_keywords >= 1:
            notifications.extend(self._unlock_achievement("first_steps"))
        if unique_keywords >= 10:
            notifications.extend(self._unlock_achievement("novice"))
        
        return notifications
    
    def _check_translation_achievements(self) -> List[str]:
        """Check translation-related achievements."""
        notifications = []
        
        if self.progress.translations_made >= 10:
            notifications.extend(self._unlock_achievement("translator"))
        
        if self.progress.perfect_completions >= 5:
            notifications.extend(self._unlock_achievement("perfectionist"))
        
        return notifications
    
    def _unlock_achievement(self, achievement_id: str) -> List[str]:
        """Unlock an achievement."""
        for achievement in self.achievement_definitions:
            if achievement.id == achievement_id and not achievement.unlocked:
                achievement.unlocked = True
                achievement.unlocked_at = datetime.now()
                
                # Save to settings
                unlocked = self.settings.value("unlocked_achievements", [])
                unlocked.append(achievement_id)
                self.settings.setValue("unlocked_achievements", unlocked)
                
                # Award points
                self.add_points(
                    achievement.points,
                    f"Achievement unlocked: {achievement.name}"
                )
                
                return [f"🏆 Achievement Unlocked: {achievement.icon} {achievement.name}!"]
        
        return []
    
    def _complete_challenge(self, challenge: Challenge) -> str:
        """Complete a challenge and award points."""
        self.add_points(challenge.reward_points, f"Challenge completed: {challenge.title}")
        
        # Check challenge achievement
        completed_challenges = sum(1 for c in self.progress.challenges if c.completed)
        if completed_challenges >= 5:
            self._unlock_achievement("challenger")
        
        return f"✅ Challenge Completed: {challenge.title} (+{challenge.reward_points} XP)"
    
    def get_next_level_progress(self) -> tuple[int, int]:
        """Get XP progress towards next level."""
        if self.progress.level >= len(self.LEVEL_THRESHOLDS) - 1:
            return 100, 100  # Max level
        
        current_threshold = self.LEVEL_THRESHOLDS[self.progress.level - 1]
        next_threshold = self.LEVEL_THRESHOLDS[self.progress.level]
        
        xp_in_level = self.progress.experience_points - current_threshold
        xp_needed = next_threshold - current_threshold
        
        return xp_in_level, xp_needed


class AnimatedProgressBar(QProgressBar):
    """Custom progress bar with smooth animations."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.animation = QPropertyAnimation(self, b"value")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
    
    def set_value_animated(self, value: int):
        """Set value with animation."""
        self.animation.setStartValue(self.value())
        self.animation.setEndValue(value)
        self.animation.start()


class GamifiedStatusWidget(QWidget):
    """Widget displaying gamification status."""
    
    def __init__(self, gamification_service: GamificationService, parent=None):
        super().__init__(parent)
        self.service = gamification_service
        self.init_ui()
        
        # Update timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_display)
        self.update_timer.start(1000)  # Update every second
    
    def init_ui(self):
        """Initialize the status UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # Level display
        self.level_label = QLabel(f"Level {self.service.progress.level}")
        self.level_label.setStyleSheet("""
            QLabel {
                font-size: 16px;
                font-weight: bold;
                color: #0070f3;
                padding: 5px 10px;
                background-color: rgba(0, 112, 243, 0.1);
                border-radius: 15px;
            }
        """)
        layout.addWidget(self.level_label)
        
        # XP Progress bar
        xp_layout = QVBoxLayout()
        xp_label = QLabel("Experience")
        xp_label.setStyleSheet("font-size: 10px; color: #666;")
        xp_layout.addWidget(xp_label)
        
        self.xp_bar = AnimatedProgressBar()
        self.xp_bar.setTextVisible(True)
        self.xp_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #e0e0e0;
                border-radius: 5px;
                text-align: center;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #4CAF50, stop: 1 #8BC34A
                );
                border-radius: 4px;
            }
        """)
        self.xp_bar.setMaximumHeight(20)
        xp_layout.addWidget(self.xp_bar)
        layout.addLayout(xp_layout)
        
        layout.addSpacing(20)
        
        # Streak display
        self.streak_label = QLabel(f"🔥 {self.service.progress.current_streak} day streak")
        self.streak_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #ff6b6b;
                padding: 5px 10px;
                background-color: rgba(255, 107, 107, 0.1);
                border-radius: 12px;
            }
        """)
        layout.addWidget(self.streak_label)
        
        # Total points
        self.points_label = QLabel(f"⭐ {self.service.progress.total_points} points")
        self.points_label.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #f59e0b;
                padding: 5px 10px;
                background-color: rgba(245, 158, 11, 0.1);
                border-radius: 12px;
            }
        """)
        layout.addWidget(self.points_label)
        
        layout.addStretch()
        
        # View achievements button
        self.achievements_btn = QPushButton("🏆 Achievements")
        self.achievements_btn.clicked.connect(self.show_achievements)
        self.achievements_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        layout.addWidget(self.achievements_btn)
        
        # Challenges button
        self.challenges_btn = QPushButton("🎯 Challenges")
        self.challenges_btn.clicked.connect(self.show_challenges)
        self.challenges_btn.setStyleSheet("""
            QPushButton {
                background-color: #ec4899;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #db2777;
            }
        """)
        layout.addWidget(self.challenges_btn)
        
        self.update_display()
    
    def update_display(self):
        """Update the gamification display."""
        progress = self.service.progress
        
        # Update level
        self.level_label.setText(f"Level {progress.level}")
        
        # Update XP bar
        xp_current, xp_needed = self.service.get_next_level_progress()
        if xp_needed > 0:
            percentage = int((xp_current / xp_needed) * 100)
            self.xp_bar.set_value_animated(percentage)
            self.xp_bar.setFormat(f"{xp_current}/{xp_needed} XP")
        
        # Update streak
        self.streak_label.setText(f"🔥 {progress.current_streak} day streak")
        
        # Update points
        self.points_label.setText(f"⭐ {progress.total_points} points")
    
    def show_achievements(self):
        """Show achievements dialog."""
        dialog = AchievementsDialog(self.service, self)
        dialog.exec()
    
    def show_challenges(self):
        """Show challenges dialog."""
        dialog = ChallengesDialog(self.service, self)
        dialog.exec()
    
    def show_notification(self, message: str):
        """Show floating notification."""
        notification = NotificationWidget(message, self.window())
        notification.show_animated()


class NotificationWidget(QLabel):
    """Floating notification widget."""
    
    def __init__(self, message: str, parent=None):
        super().__init__(message, parent)
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
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.setGraphicsEffect(shadow)
        
        # Animation
        self.animation = QPropertyAnimation(self, b"pos")
        self.animation.setDuration(500)
        self.animation.setEasingCurve(QEasingCurve.Type.OutBounce)
        self.animation.finished.connect(self._start_fade_timer)
        
        # Fade timer
        self.fade_timer = QTimer()
        self.fade_timer.timeout.connect(self.hide)
        self.fade_timer.setSingleShot(True)
    
    def show_animated(self):
        """Show with animation."""
        if self.parent():
            # Position at top center of parent
            parent_rect = self.parent().rect()
            x = (parent_rect.width() - self.sizeHint().width()) // 2
            start_y = -self.sizeHint().height()
            end_y = 50
            
            self.move(x, start_y)
            self.show()
            
            self.animation.setStartValue(QPoint(x, start_y))
            self.animation.setEndValue(QPoint(x, end_y))
            self.animation.start()
    
    def _start_fade_timer(self):
        """Start timer to fade out."""
        self.fade_timer.start(3000)  # Show for 3 seconds


class AchievementsDialog(QDialog):
    """Dialog showing achievements."""
    
    def __init__(self, service: GamificationService, parent=None):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Achievements")
        self.setModal(True)
        self.resize(600, 400)
        self.init_ui()
    
    def init_ui(self):
        """Initialize achievements UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🏆 Your Achievements")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Achievement list
        list_widget = QListWidget()
        list_widget.setSpacing(5)
        
        for achievement in self.service.achievement_definitions:
            item_text = f"{achievement.icon} {achievement.name}"
            if achievement.unlocked:
                item_text += " ✅"
                description = achievement.description
            else:
                item_text += " 🔒"
                description = f"{achievement.description} ({achievement.requirement})"
            
            item = QListWidgetItem(item_text)
            item.setToolTip(f"{description}\nReward: {achievement.points} points")
            
            if achievement.unlocked:
                item.setForeground(QColor("#059862"))
            else:
                item.setForeground(QColor("#666666"))
            
            list_widget.addItem(item)
        
        layout.addWidget(list_widget)
        
        # Stats
        unlocked = sum(1 for a in self.service.achievement_definitions if a.unlocked)
        total = len(self.service.achievement_definitions)
        stats_label = QLabel(f"Unlocked: {unlocked}/{total}")
        stats_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(stats_label)
        
        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)


class ChallengesDialog(QDialog):
    """Dialog showing daily challenges."""
    
    def __init__(self, service: GamificationService, parent=None):
        super().__init__(parent)
        self.service = service
        self.setWindowTitle("Daily Challenges")
        self.setModal(True)
        self.resize(500, 300)
        self.init_ui()
    
    def init_ui(self):
        """Initialize challenges UI."""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("🎯 Daily Challenges")
        title.setStyleSheet("font-size: 20px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Challenge list
        for challenge in self.service.progress.challenges:
            frame = QFrame()
            frame.setFrameStyle(QFrame.Shape.Box)
            frame_layout = QVBoxLayout(frame)
            
            # Challenge title
            title_layout = QHBoxLayout()
            title_label = QLabel(f"<b>{challenge.title}</b>")
            title_layout.addWidget(title_label)
            
            if challenge.completed:
                status_label = QLabel("✅ Completed")
                status_label.setStyleSheet("color: #059862;")
            else:
                status_label = QLabel(f"🎯 {challenge.current_value}/{challenge.target_value}")
            title_layout.addWidget(status_label)
            title_layout.addStretch()
            
            reward_label = QLabel(f"+{challenge.reward_points} XP")
            reward_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
            title_layout.addWidget(reward_label)
            
            frame_layout.addLayout(title_layout)
            
            # Description
            desc_label = QLabel(challenge.description)
            desc_label.setWordWrap(True)
            desc_label.setStyleSheet("color: #666; padding: 5px 0;")
            frame_layout.addWidget(desc_label)
            
            # Progress bar
            if not challenge.completed:
                progress = QProgressBar()
                progress.setMaximum(challenge.target_value)
                progress.setValue(challenge.current_value)
                progress.setTextVisible(True)
                frame_layout.addWidget(progress)
            
            layout.addWidget(frame)
        
        layout.addStretch()
        
        # Close button
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Close)
        buttons.rejected.connect(self.accept)
        layout.addWidget(buttons)


class GamifiedCodeEditor(CodeEditorWithEducationalAutoComplete):
    """Code editor with gamification integration."""
    
    notification_triggered = pyqtSignal(str)
    
    def __init__(self, gamification_service: GamificationService, parent=None):
        super().__init__(parent)
        self.gamification_service = gamification_service
        self.last_completed_pattern = None
    
    def _insert_suggestion(self, suggestion: EducationalSuggestion):
        """Override to add gamification."""
        super()._insert_suggestion(suggestion)
        
        # Record keyword usage
        notifications = self.gamification_service.record_keyword_use(
            suggestion.text,
            suggestion.category
        )
        
        for notification in notifications:
            self.notification_triggered.emit(notification)
        
        # Check for pattern completion
        if suggestion.template and "$" in suggestion.template:
            self.last_completed_pattern = suggestion.text
    
    def check_pattern_completion(self):
        """Check if user completed a pattern correctly."""
        if self.last_completed_pattern:
            # Simple check - in real implementation, verify syntax
            cursor = self.textCursor()
            cursor.select(QTextCursor.SelectionType.LineUnderCursor)
            line = cursor.selectedText()
            
            if self.last_completed_pattern in line and not "$" in line:
                notifications = self.gamification_service.record_pattern_completion(
                    self.last_completed_pattern
                )
                for notification in notifications:
                    self.notification_triggered.emit(notification)
                
                self.last_completed_pattern = None


class TauTranslatorGamified(QMainWindow):
    """Tau Translator with Gamification."""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Tau Translator - Learn & Play Edition")
        self.setGeometry(100, 100, 1400, 900)
        
        # Initialize gamification
        self.gamification_service = GamificationService()
        
        # Check daily streak
        streak_status = self.gamification_service.check_streak()
        
        self.init_ui()
        
        # Show streak notification
        if streak_status == "streak_maintained":
            self.show_notification(
                f"🔥 Welcome back! {self.gamification_service.progress.current_streak} day streak!"
            )
        elif streak_status == "streak_broken":
            self.show_notification("😔 Streak broken! Start a new one today!")
    
    def init_ui(self):
        """Initialize the gamified UI."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        
        # Gamification status bar
        self.gamification_widget = GamifiedStatusWidget(self.gamification_service)
        layout.addWidget(self.gamification_widget)
        
        # Control bar
        control_layout = QHBoxLayout()
        
        # Language selectors
        self.left_language = QComboBox()
        self.left_language.addItems(['PLAIN_ENGLISH', 'TAU', 'TCE'])
        self.left_language.currentTextChanged.connect(self._on_left_language_changed)
        
        self.right_language = QComboBox()
        self.right_language.addItems(['TAU', 'PLAIN_ENGLISH', 'TCE'])
        self.right_language.currentTextChanged.connect(self._on_right_language_changed)
        
        # Translate button
        self.translate_button = QPushButton("🚀 Translate")
        self.translate_button.clicked.connect(self._translate)
        self.translate_button.setStyleSheet("""
            QPushButton {
                background-color: #0070f3;
                color: white;
                border: none;
                padding: 10px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #0051cc;
                transform: scale(1.05);
            }
        """)
        
        control_layout.addWidget(QLabel("From:"))
        control_layout.addWidget(self.left_language)
        control_layout.addWidget(QLabel("To:"))
        control_layout.addWidget(self.right_language)
        control_layout.addStretch()
        control_layout.addWidget(self.translate_button)
        
        layout.addLayout(control_layout)
        
        # Editor panels
        editor_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left editor
        left_frame = QFrame()
        left_frame.setFrameStyle(QFrame.Shape.Box)
        left_layout = QVBoxLayout(left_frame)
        left_layout.addWidget(QLabel("Input (Start typing for suggestions!)"))
        self.left_editor = GamifiedCodeEditor(self.gamification_service)
        self.left_editor.notification_triggered.connect(self.show_notification)
        self.left_editor.setPlaceholderText(
            "🎮 Start your TAU learning journey!\n"
            "Try typing: always, forall, solve\n"
            "Earn XP and unlock achievements!"
        )
        left_layout.addWidget(self.left_editor)
        
        # Right editor
        right_frame = QFrame()
        right_frame.setFrameStyle(QFrame.Shape.Box)
        right_layout = QVBoxLayout(right_frame)
        right_layout.addWidget(QLabel("Output"))
        self.right_editor = GamifiedCodeEditor(self.gamification_service)
        self.right_editor.notification_triggered.connect(self.show_notification)
        right_layout.addWidget(self.right_editor)
        
        editor_splitter.addWidget(left_frame)
        editor_splitter.addWidget(right_frame)
        layout.addWidget(editor_splitter)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("🎮 Ready to learn! Use autocomplete to earn XP!")
        
        # Initialize
        self._on_left_language_changed(self.left_language.currentText())
        self._on_right_language_changed(self.right_language.currentText())
        
        # Pattern completion checker
        self.pattern_timer = QTimer()
        self.pattern_timer.timeout.connect(self._check_pattern_completion)
        self.pattern_timer.start(2000)  # Check every 2 seconds
    
    def _on_left_language_changed(self, language):
        """Handle language change."""
        self.left_editor.set_language(language)
        if language in ["TAU", "TCE"]:
            self.status_bar.showMessage(f"✨ {language} mode activated! Start earning XP!", 3000)
    
    def _on_right_language_changed(self, language):
        """Handle language change."""
        self.right_editor.set_language(language)
    
    def _translate(self):
        """Perform translation with gamification."""
        source_text = self.left_editor.toPlainText()
        if not source_text.strip():
            self.status_bar.showMessage("💡 Enter some text to translate!", 3000)
            return
        
        # Mock translation
        self.status_bar.showMessage("🔄 Translating...", 0)
        
        # Simulate translation
        result = f"// Translated from {self.left_language.currentText()} to {self.right_language.currentText()}\n"
        result += source_text  # In real implementation, actual translation
        
        self.right_editor.setPlainText(result)
        
        # Record translation
        perfect = random.random() > 0.7  # Mock perfect score
        notifications = self.gamification_service.record_translation(perfect)
        
        for notification in notifications:
            self.show_notification(notification)
        
        self.status_bar.showMessage("✅ Translation complete!", 3000)
    
    def _check_pattern_completion(self):
        """Check if patterns were completed."""
        self.left_editor.check_pattern_completion()
        self.right_editor.check_pattern_completion()
    
    def show_notification(self, message: str):
        """Show gamification notification."""
        notification = NotificationWidget(message, self)
        notification.show_animated()
        self.gamification_widget.update_display()
    
    def closeEvent(self, event):
        """Save progress on close."""
        self.gamification_service.save_progress()
        event.accept()


def main():
    """Run the gamified application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Tau Translator Gamified")
    
    # Set fun application style
    app.setStyleSheet("""
        QMainWindow {
            background-color: #f8fafc;
        }
        QFrame {
            background-color: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
        }
        QTextEdit {
            border: none;
            background-color: transparent;
            font-size: 14px;
        }
    """)
    
    window = TauTranslatorGamified()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()