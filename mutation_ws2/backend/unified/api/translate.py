"""
Translation endpoints for the unified backend.

Consolidates all translation functionality from the different backend variants.

Author: DarkLightX / Dana Edwards
"""

from typing import Optional, List, Dict, Any
from fastapi import APIRouter, Request, Depends, HTTPException
from pydantic import BaseModel, Field, validator
from ..core.auth import get_optional_user
from ..core.responses import (
    create_translation_response, 
    create_error_response, 
    create_success_response,
    TranslationError
)
from ..translators.base import TranslationDirection

router = APIRouter()


class TranslationRequest(BaseModel):
    """Request model for translation."""
    sourceText: str = Field(..., alias="source_text", description="Text to translate")
    direction: str = Field(default="to_tau", description="Translation direction")
    engine: Optional[str] = Field(default=None, description="Specific engine to use")
    use_fallback: bool = Field(default=True, description="Use fallback engines if primary fails")
    
    # Legacy field names for backward compatibility
    text: Optional[str] = Field(default=None, description="Legacy field for source text")
    
    @validator('sourceText', pre=True, always=True)
    def set_source_text(cls, v, values):
        # Support legacy 'text' field
        if not v and values.get('text'):
            return values['text']
        return v
    
    @validator('direction')
    def validate_direction(cls, v):
        valid_directions = ['to_tau', 'to_tce', 'to_english', 'bidirectional']
        if v not in valid_directions:
            raise ValueError(f"Direction must be one of: {valid_directions}")
        return v


class ParallelTranslationRequest(BaseModel):
    """Request model for parallel translation with multiple engines."""
    sourceText: str = Field(..., alias="source_text", description="Text to translate")
    direction: str = Field(default="to_tau", description="Translation direction")
    max_engines: int = Field(default=3, description="Maximum number of engines to use")


class BatchTranslationRequest(BaseModel):
    """Request model for batch translation."""
    texts: List[str] = Field(..., description="List of texts to translate")
    direction: str = Field(default="to_tau", description="Translation direction")
    engine: Optional[str] = Field(default=None, description="Specific engine to use")


@router.post("/")
async def translate_text(request: TranslationRequest, req: Request):
    """Main translation endpoint - consolidates all translation methods."""
    try:
        # Get translation manager
        translation_manager = getattr(req.app.state, 'translation_manager', None)
        if not translation_manager:
            raise TranslationError("Translation service not available")
        
        # Convert direction string to enum
        direction_map = {
            'to_tau': TranslationDirection.TO_TAU,
            'to_tce': TranslationDirection.TO_TCE,
            'to_english': TranslationDirection.TO_ENGLISH,
            'bidirectional': TranslationDirection.BIDIRECTIONAL
        }
        direction = direction_map[request.direction]
        
        # Perform translation
        result = translation_manager.translate(
            text=request.sourceText,
            direction=direction,
            engine_name=request.engine,
            use_fallback=request.use_fallback
        )
        
        if result.success:
            return create_translation_response(
                source_text=result.original_text,
                translated_text=result.translated_text,
                translation_method=result.translation_method,
                confidence=result.confidence,
                metadata={
                    "direction": result.direction.value,
                    "processing_time": result.processing_time,
                    **(result.metadata or {})
                }
            )
        else:
            return create_error_response(
                message=result.error_message or "Translation failed",
                error_code="TRANSLATION_FAILED",
                details={
                    "translation_method": result.translation_method,
                    "direction": result.direction.value,
                    "processing_time": result.processing_time
                },
                status_code=422
            )
    
    except Exception as e:
        return create_error_response(
            message=f"Translation error: {str(e)}",
            error_code="TRANSLATION_ERROR",
            status_code=500
        )


@router.post("/parallel")
async def translate_parallel(request: ParallelTranslationRequest, req: Request):
    """Translate using multiple engines in parallel."""
    try:
        translation_manager = getattr(req.app.state, 'translation_manager', None)
        if not translation_manager:
            raise TranslationError("Translation service not available")
        
        direction_map = {
            'to_tau': TranslationDirection.TO_TAU,
            'to_tce': TranslationDirection.TO_TCE,
            'to_english': TranslationDirection.TO_ENGLISH,
            'bidirectional': TranslationDirection.BIDIRECTIONAL
        }
        direction = direction_map[request.direction]
        
        # Perform parallel translation
        results = translation_manager.translate_parallel(
            text=request.sourceText,
            direction=direction,
            max_engines=request.max_engines
        )
        
        if not results:
            return create_error_response(
                "No translation engines available for this request",
                error_code="NO_ENGINES_AVAILABLE",
                status_code=503
            )
        
        # Convert results to serializable format
        serialized_results = [result.to_dict() for result in results]
        
        return create_success_response({
            "results": serialized_results,
            "best_result": serialized_results[0] if serialized_results else None,
            "total_engines": len(serialized_results)
        })
    
    except Exception as e:
        return create_error_response(
            f"Parallel translation error: {str(e)}",
            error_code="PARALLEL_TRANSLATION_ERROR",
            status_code=500
        )


@router.post("/batch")
async def translate_batch(request: BatchTranslationRequest, req: Request):
    """Translate multiple texts in batch."""
    try:
        translation_manager = getattr(req.app.state, 'translation_manager', None)
        if not translation_manager:
            raise TranslationError("Translation service not available")
        
        if len(request.texts) > 100:  # Limit batch size
            return create_error_response(
                "Batch size too large (maximum 100 texts)",
                error_code="BATCH_SIZE_EXCEEDED",
                status_code=413
            )
        
        direction_map = {
            'to_tau': TranslationDirection.TO_TAU,
            'to_tce': TranslationDirection.TO_TCE,
            'to_english': TranslationDirection.TO_ENGLISH,
            'bidirectional': TranslationDirection.BIDIRECTIONAL
        }
        direction = direction_map[request.direction]
        
        # Translate each text
        results = []
        for i, text in enumerate(request.texts):
            result = translation_manager.translate(
                text=text,
                direction=direction,
                engine_name=request.engine,
                use_fallback=True
            )
            
            result_dict = result.to_dict()
            result_dict['batch_index'] = i
            results.append(result_dict)
        
        # Calculate summary statistics
        successful = sum(1 for r in results if r['success'])
        failed = len(results) - successful
        
        return create_success_response({
            "results": results,
            "summary": {
                "total": len(results),
                "successful": successful,
                "failed": failed,
                "success_rate": (successful / len(results)) * 100 if results else 0
            }
        })
    
    except Exception as e:
        return create_error_response(
            f"Batch translation error: {str(e)}",
            error_code="BATCH_TRANSLATION_ERROR",
            status_code=500
        )


@router.get("/engines")
async def list_engines(req: Request):
    """List available translation engines."""
    try:
        translation_manager = getattr(req.app.state, 'translation_manager', None)
        if not translation_manager:
            return create_success_response({
                "engines": [],
                "message": "Translation service not initialized"
            })
        
        engine_status = translation_manager.get_engine_status()
        return create_success_response(engine_status)
    
    except Exception as e:
        return create_error_response(
            f"Error getting engines: {str(e)}",
            error_code="ENGINE_LIST_ERROR",
            status_code=500
        )


@router.get("/engines/{engine_name}")
async def get_engine_info(engine_name: str, req: Request):
    """Get information about a specific engine."""
    try:
        translation_manager = getattr(req.app.state, 'translation_manager', None)
        if not translation_manager:
            raise TranslationError("Translation service not available")
        
        engine = translation_manager._get_engine_by_name(engine_name)
        if not engine:
            return create_error_response(
                f"Engine '{engine_name}' not found",
                error_code="ENGINE_NOT_FOUND",
                status_code=404
            )
        
        engine_info = engine.get_status()
        
        # Add cache stats if available
        if hasattr(engine, 'get_cache_stats'):
            engine_info['cache_stats'] = engine.get_cache_stats()
        
        return create_success_response(engine_info)
    
    except Exception as e:
        return create_error_response(
            f"Error getting engine info: {str(e)}",
            error_code="ENGINE_INFO_ERROR",
            status_code=500
        )


@router.post("/validate")
async def validate_translation(request: TranslationRequest, req: Request):
    """Validate a translation without actually performing it."""
    try:
        translation_manager = getattr(req.app.state, 'translation_manager', None)
        if not translation_manager:
            raise TranslationError("Translation service not available")
        
        direction_map = {
            'to_tau': TranslationDirection.TO_TAU,
            'to_tce': TranslationDirection.TO_TCE,
            'to_english': TranslationDirection.TO_ENGLISH,
            'bidirectional': TranslationDirection.BIDIRECTIONAL
        }
        direction = direction_map[request.direction]
        
        # Find capable engines
        available_engines = translation_manager.get_available_engines(direction)
        capable_engines = [
            engine for engine in available_engines
            if engine.can_translate(request.sourceText, direction)
        ]
        
        # Validate input
        issues = []
        if not request.sourceText.strip():
            issues.append("Empty or whitespace-only input")
        
        if len(request.sourceText) > 10000:
            issues.append("Input text too long (maximum 10,000 characters)")
        
        if not capable_engines:
            issues.append(f"No engines available for direction: {request.direction}")
        
        is_valid = len(issues) == 0
        
        return create_success_response({
            "is_valid": is_valid,
            "issues": issues,
            "capable_engines": [engine.name for engine in capable_engines],
            "recommended_engine": capable_engines[0].name if capable_engines else None
        })
    
    except Exception as e:
        return create_error_response(
            f"Validation error: {str(e)}",
            error_code="VALIDATION_ERROR",
            status_code=500
        )


# Legacy compatibility endpoints
@router.post("/tau")
async def translate_to_tau(request: dict, req: Request):
    """Legacy endpoint for translating to Tau."""
    translated_request = TranslationRequest(
        sourceText=request.get("sourceText", request.get("text", "")),
        direction="to_tau"
    )
    return await translate_text(translated_request, req)


@router.post("/tce")
async def translate_to_tce(request: dict, req: Request):
    """Legacy endpoint for translating to TCE."""
    translated_request = TranslationRequest(
        sourceText=request.get("sourceText", request.get("text", "")),
        direction="to_tce"
    )
    return await translate_text(translated_request, req)


@router.post("/english")
async def translate_to_english(request: dict, req: Request):
    """Legacy endpoint for translating to English."""
    translated_request = TranslationRequest(
        sourceText=request.get("sourceText", request.get("text", "")),
        direction="to_english"
    )
    return await translate_text(translated_request, req)