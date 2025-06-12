"""
Qt UI components for gamification system.

Provides visual elements for achievements, progress, and challenges.
Follows Rule 4: Favor composition over inheritance.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Optional, List, Dict
from dataclasses import dataclass
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QListWidget, QListWidgetItem, QFrame,
    QGraphicsOpacityEffect, QScrollArea, QGridLayout
)
from PyQt6.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve,
    pyqtSignal, QRect, QPoint, pyqtProperty
)
from PyQt6.QtGui import QPixmap, QIcon, QFont, QPainter, QColor, QPalette

from ..domain.gamification_types import (
    Achievement, Badge, Challenge, PlayerProfile, SkillArea,
    ExperiencePoints, LevelNumber, ProgressUpdate
)

class AnimatedProgressBar(QProgressBar):
    """Progress bar with smooth animations."""
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._animation = QPropertyAnimation(self, b"value")
        self._animation.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self._animation.setDuration(500)
    
    def setValue_animated(self, value: int):
        """Set value with animation."""
        self._animation.setStartValue(self.value())
        self._animation.setEndValue(value)
        self._animation.start()

class AchievementWidget(QFrame):
    """Widget displaying a single achievement."""
    
    clicked = pyqtSignal(Achievement)
    
    def __init__(self, achievement: Achievement, unlocked: bool = False):
        super().__init__()
        self._achievement = achievement
        self._unlocked = unlocked
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize UI components."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedSize(280, 100)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Icon
        icon_label = QLabel()
        icon_label.setFixedSize(60, 60)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._set_achievement_icon(icon_label)
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        
        # Title
        title = QLabel(self._achievement.name)
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        info_layout.addWidget(title)
        
        # Description
        desc = QLabel(self._achievement.description)
        desc.setWordWrap(True)
        desc.setFont(QFont("Arial", 10))
        info_layout.addWidget(desc)
        
        # Points
        points = QLabel(f"+{self._achievement.points} XP")
        points.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        points.setStyleSheet("color: #4CAF50;")
        info_layout.addWidget(points)
        
        layout.addLayout(info_layout)
        
        # Apply unlocked/locked styling
        self._apply_styling()
    
    def _set_achievement_icon(self, label: QLabel):
        """Set achievement icon with fallback."""
        # In production, load actual icons
        label.setText("🏆" if self._unlocked else "🔒")
        label.setStyleSheet(
            f"font-size: 30px; background-color: {'#FFD700' if self._unlocked else '#CCCCCC'}; "
            "border-radius: 30px;"
        )
    
    def _apply_styling(self):
        """Apply visual styling based on unlock status."""
        if self._unlocked:
            self.setStyleSheet("""
                QFrame {
                    background-color: #F5F5F5;
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                }
                QFrame:hover {
                    background-color: #E8F5E9;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FAFAFA;
                    border: 2px solid #CCCCCC;
                    border-radius: 10px;
                }
                QFrame:hover {
                    background-color: #F5F5F5;
                }
            """)
            
            # Add opacity effect for locked achievements
            opacity = QGraphicsOpacityEffect()
            opacity.setOpacity(0.7)
            self.setGraphicsEffect(opacity)
    
    def mousePressEvent(self, event):
        """Handle click events."""
        self.clicked.emit(self._achievement)

class ChallengeWidget(QFrame):
    """Widget displaying a challenge with progress."""
    
    def __init__(self, challenge: Challenge):
        super().__init__()
        self._challenge = challenge
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize UI components."""
        self.setFrameStyle(QFrame.Shape.Box)
        self.setFixedHeight(120)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Header
        header = QHBoxLayout()
        
        # Title
        title = QLabel(self._challenge.name)
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        header.addWidget(title)
        
        # Reward
        reward = QLabel(f"+{self._challenge.reward_xp} XP")
        reward.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        reward.setStyleSheet("color: #4CAF50;")
        header.addWidget(reward)
        
        layout.addLayout(header)
        
        # Description
        desc = QLabel(self._challenge.description)
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        # Progress bar
        self._progress_bar = AnimatedProgressBar()
        self._progress_bar.setMaximum(100)
        self._progress_bar.setValue(int(self._challenge.progress_percentage()))
        self._progress_bar.setTextVisible(True)
        self._progress_bar.setFormat(
            f"{self._challenge.current_value}/{self._challenge.target_value}"
        )
        layout.addWidget(self._progress_bar)
        
        # Apply styling
        self._apply_styling()
    
    def _apply_styling(self):
        """Apply visual styling based on completion status."""
        if self._challenge.is_completed():
            self.setStyleSheet("""
                QFrame {
                    background-color: #E8F5E9;
                    border: 2px solid #4CAF50;
                    border-radius: 10px;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame {
                    background-color: #FFF3E0;
                    border: 2px solid #FF9800;
                    border-radius: 10px;
                }
            """)
    
    def update_progress(self, current_value: int):
        """Update challenge progress with animation."""
        self._challenge = dataclass.replace(
            self._challenge,
            current_value=current_value
        )
        self._progress_bar.setValue_animated(int(self._challenge.progress_percentage()))
        self._progress_bar.setFormat(
            f"{self._challenge.current_value}/{self._challenge.target_value}"
        )
        self._apply_styling()

class LevelProgressWidget(QWidget):
    """Widget showing level and XP progress."""
    
    def __init__(self, profile: PlayerProfile):
        super().__init__()
        self._profile = profile
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Level header
        header = QHBoxLayout()
        
        # Level icon and number
        level_container = QVBoxLayout()
        level_icon = QLabel("⭐")
        level_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_icon.setStyleSheet("font-size: 40px;")
        level_container.addWidget(level_icon)
        
        level_text = QLabel(f"Level {self._profile.current_level}")
        level_text.setAlignment(Qt.AlignmentFlag.AlignCenter)
        level_text.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        level_container.addWidget(level_text)
        
        header.addLayout(level_container)
        
        # XP info
        xp_container = QVBoxLayout()
        xp_container.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        xp_label = QLabel(f"Total XP: {self._profile.total_xp}")
        xp_label.setFont(QFont("Arial", 12))
        xp_container.addWidget(xp_label)
        
        # Next level info
        next_level_xp = self._calculate_next_level_xp()
        if next_level_xp:
            next_label = QLabel(f"Next Level: {next_level_xp} XP")
            next_label.setFont(QFont("Arial", 10))
            next_label.setStyleSheet("color: #666666;")
            xp_container.addWidget(next_label)
        
        header.addLayout(xp_container)
        header.addStretch()
        
        layout.addLayout(header)
        
        # XP Progress bar
        self._xp_progress = AnimatedProgressBar()
        self._xp_progress.setMinimumHeight(25)
        self._update_xp_progress()
        layout.addWidget(self._xp_progress)
        
        # Streak info
        if self._profile.daily_streak > 0:
            streak_label = QLabel(f"🔥 {self._profile.daily_streak} day streak!")
            streak_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            streak_label.setFont(QFont("Arial", 11))
            streak_label.setStyleSheet("color: #FF5722; margin-top: 10px;")
            layout.addWidget(streak_label)
    
    def _calculate_next_level_xp(self) -> Optional[int]:
        """Calculate XP needed for next level."""
        # This would use actual level data
        level_thresholds = [0, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000]
        
        current_level = self._profile.current_level
        if current_level < len(level_thresholds) - 1:
            return level_thresholds[current_level + 1]
        return None
    
    def _update_xp_progress(self):
        """Update XP progress bar."""
        level_thresholds = [0, 100, 250, 500, 1000, 2000, 3500, 5000, 7500, 10000]
        
        current_level = self._profile.current_level
        if current_level >= len(level_thresholds) - 1:
            self._xp_progress.setMaximum(100)
            self._xp_progress.setValue(100)
            return
        
        current_threshold = level_thresholds[current_level]
        next_threshold = level_thresholds[current_level + 1]
        
        progress = self._profile.total_xp - current_threshold
        total_needed = next_threshold - current_threshold
        
        percentage = int((progress / total_needed) * 100)
        self._xp_progress.setMaximum(100)
        self._xp_progress.setValue(percentage)
        self._xp_progress.setFormat(f"{progress}/{total_needed} XP")

class SkillProgressWidget(QWidget):
    """Widget showing progress in different skill areas."""
    
    def __init__(self, skill_progress: Dict[SkillArea, any]):
        super().__init__()
        self._skill_progress = skill_progress
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Title
        title = QLabel("Skills")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        layout.addWidget(title)
        
        # Skill grid
        grid = QGridLayout()
        grid.setSpacing(15)
        
        skill_icons = {
            SkillArea.TEMPORAL_LOGIC: "⏱️",
            SkillArea.QUANTIFIERS: "∀",
            SkillArea.STREAM_PROCESSING: "〜",
            SkillArea.SOLVER_CONSTRAINTS: "✓",
            SkillArea.FUNCTION_DEFINITIONS: "ƒ",
            SkillArea.PATTERN_MATCHING: "🎯",
            SkillArea.TRANSLATION: "🔄"
        }
        
        for i, (skill, progress) in enumerate(self._skill_progress.items()):
            row = i // 2
            col = i % 2
            
            skill_frame = self._create_skill_frame(
                skill,
                skill_icons.get(skill, "📊"),
                progress
            )
            grid.addWidget(skill_frame, row, col)
        
        layout.addLayout(grid)
    
    def _create_skill_frame(self, skill: SkillArea, icon: str, progress: any) -> QFrame:
        """Create frame for individual skill."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.Shape.Box)
        frame.setFixedSize(180, 80)
        
        layout = QHBoxLayout(frame)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(icon_label)
        
        # Info
        info_layout = QVBoxLayout()
        
        # Skill name
        name = QLabel(skill.value.replace('_', ' ').title())
        name.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        info_layout.addWidget(name)
        
        # Level
        level_text = f"Level {progress.level if progress else 0}"
        level_label = QLabel(level_text)
        info_layout.addWidget(level_label)
        
        # Progress bar
        progress_bar = QProgressBar()
        progress_bar.setMaximum(100)
        progress_bar.setValue(
            int(progress.progress_to_next_level()) if progress else 0
        )
        progress_bar.setFixedHeight(10)
        progress_bar.setTextVisible(False)
        info_layout.addWidget(progress_bar)
        
        layout.addLayout(info_layout)
        
        return frame

class GamificationDashboard(QWidget):
    """Main dashboard combining all gamification widgets."""
    
    challenge_clicked = pyqtSignal(Challenge)
    achievement_clicked = pyqtSignal(Achievement)
    
    def __init__(self, profile: PlayerProfile):
        super().__init__()
        self._profile = profile
        self._setup_ui()
    
    def _setup_ui(self):
        """Initialize UI components."""
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Content widget
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(20)
        
        # Level progress
        self._level_widget = LevelProgressWidget(self._profile)
        content_layout.addWidget(self._level_widget)
        
        # Daily challenges
        self._add_challenges_section(content_layout)
        
        # Recent achievements
        self._add_achievements_section(content_layout)
        
        # Skills progress
        self._skill_widget = SkillProgressWidget(self._profile.skill_progress)
        content_layout.addWidget(self._skill_widget)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        main_layout.addWidget(scroll)
    
    def _add_challenges_section(self, layout: QVBoxLayout):
        """Add challenges section."""
        # Title
        title = QLabel("Daily Challenges")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("margin-left: 15px;")
        layout.addWidget(title)
        
        # Placeholder for challenges
        # In real implementation, would load actual challenges
        for i in range(3):
            challenge = Challenge(
                id=f"challenge_{i}",
                name=f"Challenge {i+1}",
                description="Complete this challenge for bonus XP!",
                type="daily",
                reward_xp=50,
                target_value=10,
                current_value=i * 3,
                expires_at=None,
                skill_areas=[]
            )
            widget = ChallengeWidget(challenge)
            layout.addWidget(widget)
    
    def _add_achievements_section(self, layout: QVBoxLayout):
        """Add achievements section."""
        # Title
        title = QLabel("Recent Achievements")
        title.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        title.setStyleSheet("margin-left: 15px;")
        layout.addWidget(title)
        
        # Achievement grid
        grid_widget = QWidget()
        grid = QGridLayout(grid_widget)
        grid.setSpacing(10)
        
        # Add some sample achievements
        # In real implementation, would show actual achievements
        for i in range(4):
            achievement = Achievement(
                id=f"achievement_{i}",
                name=f"Achievement {i+1}",
                description="Great job on this achievement!",
                category="learning",
                points=50,
                icon_name="trophy",
                unlock_criteria="",
                hidden=False
            )
            
            widget = AchievementWidget(
                achievement,
                unlocked=i < 2  # First 2 are unlocked
            )
            widget.clicked.connect(self.achievement_clicked)
            
            grid.addWidget(widget, i // 2, i % 2)
        
        layout.addWidget(grid_widget)
    
    def update_profile(self, profile: PlayerProfile):
        """Update dashboard with new profile data."""
        self._profile = profile
        # Update widgets
        # In full implementation, would update all child widgets