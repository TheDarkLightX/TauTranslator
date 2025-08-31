"""
FastAPI endpoints for gamified educational autocomplete.

Provides REST API for the gamified autocomplete system.
Follows clean architecture with proper error handling.

Copyright: DarkLightX / Dana Edwards
"""

from typing import Optional, List, Dict
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field

from ..core.result_enhanced import Result
from ..core.gamified_autocomplete_app import GamifiedAutocompleteApplication
from ..core.autocomplete.models import (
    SuggestionRequest, SuggestionResponse, SpecificationContext,
    LanguageMode, ContextType, DifficultyLevel, CursorPosition
)
from ..domain.gamification_types import (
    PlayerProfile, Challenge, Achievement, UserId
)

# API Models
class AutocompleteRequest(BaseModel):
    """Request model for autocomplete suggestions."""
    text: str = Field(..., description="Current text in editor")
    cursor_position: int = Field(..., description="Cursor position in text")
    language: str = Field("TAU", description="Language mode (TAU or TCE)")
    max_suggestions: int = Field(10, description="Maximum suggestions to return")
    user_id: Optional[str] = Field(None, description="User ID for gamification")

class AutocompleteResponse(BaseModel):
    """Response model for autocomplete suggestions."""
    suggestions: List[Dict] = Field(..., description="List of suggestions")
    context_hint: Optional[str] = Field(None, description="Context-aware hint")
    learning_tip: Optional[str] = Field(None, description="Learning tip")
    xp_gained: Optional[int] = Field(None, description="XP gained for this action")

class UseSuggestionRequest(BaseModel):
    """Request model for using a suggestion."""
    suggestion_text: str = Field(..., description="Text of suggestion used")
    category: str = Field(..., description="Category of suggestion")
    difficulty: str = Field(..., description="Difficulty level")
    context: Dict = Field(..., description="Context when suggestion was used")
    user_id: str = Field(..., description="User ID")

class TranslationRequest(BaseModel):
    """Request model for translation."""
    source_text: str = Field(..., description="Text to translate")
    from_language: str = Field(..., description="Source language")
    to_language: str = Field(..., description="Target language")
    user_id: str = Field(..., description="User ID")

class ProfileResponse(BaseModel):
    """Response model for user profile."""
    user_id: str
    username: str
    total_xp: int
    current_level: int
    daily_streak: int
    completed_achievements: List[str]
    earned_badges: List[str]
    skill_progress: Dict[str, Dict]

class ChallengeResponse(BaseModel):
    """Response model for challenge."""
    id: str
    name: str
    description: str
    type: str
    reward_xp: int
    target_value: int
    current_value: int
    progress_percentage: float
    expires_at: str

# Create router
router = APIRouter(prefix="/api/gamified", tags=["gamified_autocomplete"])

# Application instances cache (in production, use proper DI)
_app_instances: Dict[str, GamifiedAutocompleteApplication] = {}

def get_app(user_id: str) -> GamifiedAutocompleteApplication:
    """Get or create application instance for user."""
    if user_id not in _app_instances:
        _app_instances[user_id] = GamifiedAutocompleteApplication(
            user_id=UserId(user_id),
            username=f"User_{user_id}"
        )
    return _app_instances[user_id]

@router.post("/autocomplete", response_model=AutocompleteResponse)
async def get_autocomplete_suggestions(request: AutocompleteRequest):
    """
    Get gamified autocomplete suggestions.
    
    Returns suggestions with XP tracking and learning tips.
    """
    try:
        # Get app instance
        app = get_app(request.user_id or "anonymous")
        
        # Build context
        context = SpecificationContext(
            full_text=request.text,
            cursor_position=CursorPosition(request.cursor_position),
            language_mode=LanguageMode[request.language.upper()],
            context_type=ContextType.LOGICAL_ASSERTION,  # Would detect from text
            parent_constructs=[],
            variables_in_scope=[],
            learning_level=DifficultyLevel.INTERMEDIATE
        )
        
        # Create suggestion request
        suggestion_request = SuggestionRequest(
            context=context,
            max_suggestions=request.max_suggestions
        )
        
        # Get suggestions
        result = app.process_autocomplete_request(suggestion_request)
        
        if not result.is_success():
            raise HTTPException(status_code=400, detail=result.error)
        
        response = result.value
        
        # Convert to API response
        suggestions = []
        for s in response.suggestions:
            suggestions.append({
                "text": s.text,
                "display": s.display,
                "category": s.category.value,
                "description": str(s.description),
                "example": str(s.example),
                "difficulty": s.difficulty.value,
                "confidence": float(s.confidence)
            })
        
        return AutocompleteResponse(
            suggestions=suggestions,
            context_hint=str(response.context_hint) if response.context_hint else None,
            learning_tip=str(response.learning_tip) if response.learning_tip else None,
            xp_gained=None  # Set when suggestion is used
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/use-suggestion")
async def use_suggestion(request: UseSuggestionRequest):
    """
    Track when a suggestion is used.
    
    Awards XP and updates achievements.
    """
    try:
        app = get_app(request.user_id)
        
        # Create mock suggestion object
        from ..core.autocomplete.models import (
            EducationalSuggestion, SuggestionText, DisplayText,
            HintText, ExampleCode, SuggestionCategory, ConfidenceScore
        )
        
        suggestion = EducationalSuggestion(
            text=SuggestionText(request.suggestion_text),
            display=DisplayText(request.suggestion_text),
            category=SuggestionCategory(request.category),
            description=HintText(""),
            example=ExampleCode(""),
            difficulty=DifficultyLevel(request.difficulty),
            confidence=ConfidenceScore(1.0)
        )
        
        # Create context from request
        context = SpecificationContext(
            full_text=request.context.get("text", ""),
            cursor_position=CursorPosition(request.context.get("cursor", 0)),
            language_mode=LanguageMode[request.context.get("language", "TAU")],
            context_type=ContextType.LOGICAL_ASSERTION,
            parent_constructs=[],
            variables_in_scope=[]
        )
        
        # Use suggestion
        result = app.use_suggestion(suggestion, context)
        
        if not result.is_success():
            raise HTTPException(status_code=400, detail=result.error)
        
        # Get XP gained (would need to track from event)
        return {"success": True, "xp_gained": 10}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/translate")
async def translate_text(request: TranslationRequest):
    """
    Translate between TAU and TCE with gamification.
    
    Awards XP for successful translations.
    """
    try:
        app = get_app(request.user_id)
        
        # Perform translation
        result = app._autocomplete_service.translate_selection_async(
            request.source_text,
            LanguageMode[request.from_language],
            LanguageMode[request.to_language]
        )
        
        if not result.is_success():
            raise HTTPException(status_code=400, detail=result.error)
        
        # Track translation for gamification
        app.complete_translation(
            request.source_text,
            result.value,
            request.from_language,
            request.to_language
        )
        
        return {
            "translated_text": result.value,
            "xp_gained": 25
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/profile/{user_id}", response_model=ProfileResponse)
async def get_user_profile(user_id: str):
    """Get user's gamification profile."""
    try:
        app = get_app(user_id)
        
        if not app._profile:
            raise HTTPException(status_code=404, detail="Profile not found")
        
        profile = app._profile
        
        # Convert skill progress
        skill_progress = {}
        for skill, progress in profile.skill_progress.items():
            skill_progress[skill.value] = {
                "level": progress.level,
                "current_points": progress.current_points,
                "progress_percentage": progress.progress_to_next_level()
            }
        
        return ProfileResponse(
            user_id=profile.user_id,
            username=profile.username,
            total_xp=profile.total_xp,
            current_level=profile.current_level,
            daily_streak=profile.daily_streak,
            completed_achievements=list(profile.completed_achievements),
            earned_badges=list(profile.earned_badges),
            skill_progress=skill_progress
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/challenges/{user_id}", response_model=List[ChallengeResponse])
async def get_daily_challenges(user_id: str):
    """Get user's daily challenges."""
    try:
        app = get_app(user_id)
        challenges = app.get_daily_challenges()
        
        response = []
        for challenge in challenges:
            response.append(ChallengeResponse(
                id=challenge.id,
                name=challenge.name,
                description=challenge.description,
                type=challenge.type.value,
                reward_xp=challenge.reward_xp,
                target_value=challenge.target_value,
                current_value=challenge.current_value,
                progress_percentage=challenge.progress_percentage(),
                expires_at=challenge.expires_at.isoformat()
            ))
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/achievements/{user_id}/next")
async def get_next_achievements(user_id: str):
    """Get achievements close to being unlocked."""
    try:
        app = get_app(user_id)
        achievements = app.get_next_achievements()
        
        response = []
        for achievement in achievements:
            response.append({
                "id": achievement.id,
                "name": achievement.name,
                "description": achievement.description,
                "points": achievement.points,
                "category": achievement.category.value,
                "hidden": achievement.hidden
            })
        
        return response
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save-progress/{user_id}")
async def save_progress(user_id: str):
    """Manually save user's progress."""
    try:
        app = get_app(user_id)
        result = app.save_progress()
        
        if not result.is_success():
            raise HTTPException(status_code=400, detail=result.error)
        
        return {"success": True, "message": "Progress saved"}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/leaderboard")
async def get_leaderboard(limit: int = 10, offset: int = 0):
    """Get global leaderboard."""
    try:
        # Use any app instance to access repository
        app = get_app("system")
        result = app._repository.get_leaderboard(limit, offset)
        
        if not result.is_success():
            raise HTTPException(status_code=400, detail=result.error)
        
        return result.value
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@router.get("/health")
async def health_check():
    """Check if gamified autocomplete service is healthy."""
    return {
        "status": "healthy",
        "service": "gamified_autocomplete",
        "timestamp": datetime.now().isoformat()
    }