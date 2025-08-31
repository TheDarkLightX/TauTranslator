"""
Unified TauTranslator Backend Server

Consolidates all backend functionality from the 6 separate backend files
into a single, well-organized FastAPI application.

Author: DarkLightX / Dana Edwards
"""

import logging
import sys
from pathlib import Path
from contextlib import asynccontextmanager

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn

# Import unified backend components
from .core.config import settings
from .core.auth import auth_service, get_current_user, get_optional_user
from .core.responses import handle_exception, TauTranslatorException
from .translators.manager import TranslationManager

# Import API routers
from .api import health, auth, translate, grammar, nlp, gamified_autocomplete

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level.upper()),
    format=settings.log_format
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    logger.info("Starting TauTranslator Unified Backend")
    
    # Ensure directories exist
    settings.ensure_directories()
    
    # Initialize translation manager
    translation_manager = TranslationManager()
    
    # Register translation engines with priority order: Grammar -> LMQL -> Pattern
    
    # 1. Grammar engine (highest priority when available)
    try:
        if settings.enable_grammar:
            from .translators.grammar_translator import GrammarTranslationEngine
            grammar_engine = GrammarTranslationEngine()
            translation_manager.register_engine(grammar_engine, is_default=True)
            logger.info("Registered Grammar translation engine as default")
            # Store reference for grammar loading
            app.state.grammar_engine = grammar_engine
    except Exception as e:
        logger.warning(f"Could not load Grammar engine: {e}")
    
    # 2. LMQL engine (second priority)
    try:
        if settings.enable_lmql:
            from .translators.lmql_translator import LMQLTranslationEngine
            lmql_engine = LMQLTranslationEngine()
            # Only set as default if grammar engine wasn't loaded
            is_default = not hasattr(app.state, 'grammar_engine')
            translation_manager.register_engine(lmql_engine, is_default=is_default, is_fallback=True)
            logger.info(f"Registered LMQL translation engine (default={is_default})")
    except Exception as e:
        logger.warning(f"Could not load LMQL engine: {e}")
    
    try:
        if settings.enable_nlp:
            from .translators.nlp_translator import NLPTranslationEngine
            nlp_engine = NLPTranslationEngine()
            translation_manager.register_engine(nlp_engine)
            logger.info("Registered NLP translation engine")
    except Exception as e:
        logger.warning(f"Could not load NLP engine: {e}")
    
    # 3. Integrated Parser Pipeline (Natural Language → ILR → TCE → Tau)
    try:
        if settings.enable_parser_pipeline:
            from .translators.integrated_parser_pipeline import IntegratedParserPipeline
            parser_pipeline = IntegratedParserPipeline()
            translation_manager.register_engine(parser_pipeline)
            logger.info("Registered Integrated Parser Pipeline")
    except Exception as e:
        logger.warning(f"Could not load Integrated Parser Pipeline: {e}")
    
    # 4. Bidirectional engine (for reverse translation)
    try:
        if settings.enable_bidirectional:
            from .translators.bidirectional_engine import BidirectionalTranslationEngine
            bidirectional_engine = BidirectionalTranslationEngine()
            translation_manager.register_engine(bidirectional_engine, priority=8)
            logger.info("Registered Bidirectional translation engine")
    except Exception as e:
        logger.warning(f"Could not load Bidirectional engine: {e}")
    
    # 5. Pattern engine (always available as fallback)
    try:
        from .translators.pattern_translator import PatternTranslationEngine
        pattern_engine = PatternTranslationEngine()
        translation_manager.register_engine(pattern_engine, is_fallback=True)
        logger.info("Registered Pattern translation engine as fallback")
    except Exception as e:
        logger.warning(f"Could not load Pattern engine: {e}")
    
    # Make translation manager available to the app
    app.state.translation_manager = translation_manager
    
    # Clean up expired sessions
    auth_service.cleanup_sessions()
    
    logger.info("TauTranslator Unified Backend started successfully")
    
    yield
    
    # Shutdown
    logger.info("Shutting down TauTranslator Unified Backend")


# Create FastAPI application
app = FastAPI(
    title="TauTranslator Unified Backend",
    description="Consolidated backend for TauTranslator with all translation engines",
    version="2.0.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
    lifespan=lifespan
)

# Add security middleware
app.add_middleware(
    TrustedHostMiddleware, 
    allowed_hosts=["*"] if settings.debug else ["localhost", "127.0.0.1"]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=settings.cors_methods,
    allow_headers=settings.cors_headers,
)

# Global exception handler
@app.exception_handler(TauTranslatorException)
async def tau_translator_exception_handler(request, exc: TauTranslatorException):
    """Handle TauTranslator-specific exceptions."""
    return handle_exception(exc)

@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception):
    """Handle all other exceptions."""
    return handle_exception(exc)

# Include API routers
app.include_router(health.router, prefix="/health", tags=["Health"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])
app.include_router(translate.router, prefix="/api/translate", tags=["Translation"])

# Always include grammar router for grammar loading
app.include_router(grammar.router, prefix="/api/grammar", tags=["Grammar"])

if settings.enable_nlp:
    app.include_router(nlp.router, prefix="/api/nlp", tags=["NLP"])

# Include gamified autocomplete router
app.include_router(gamified_autocomplete.router, tags=["Gamified Autocomplete"])

# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic information."""
    return {
        "service": "TauTranslator Unified Backend",
        "version": "2.0.0",
        "status": "operational",
        "docs": "/docs" if settings.debug else "Documentation disabled in production",
        "features": {
            "lmql": settings.enable_lmql,
            "grammar": settings.enable_grammar,
            "nlp": settings.enable_nlp,
            "gemma3": settings.enable_gemma3
        }
    }

# System information endpoint
@app.get("/system/info", tags=["System"])
async def system_info(user: dict = Depends(get_optional_user)):
    """Get system information."""
    translation_manager = app.state.translation_manager
    
    info = {
        "backend_version": "2.0.0",
        "consolidation_status": "active",
        "engines": translation_manager.get_engine_status(),
        "statistics": translation_manager.get_statistics(),
        "configuration": {
            "debug": settings.debug,
            "features": {
                "lmql": settings.enable_lmql,
                "grammar": settings.enable_grammar,
                "nlp": settings.enable_nlp,
                "gemma3": settings.enable_gemma3
            }
        }
    }
    
    # Add sensitive information only for authenticated users
    if user:
        info["authentication"] = {
            "user_id": user.get("user_id"),
            "session_created": user.get("created_at"),
            "auth_method": user.get("metadata", {}).get("auth_method")
        }
    
    return info

# Legacy compatibility endpoints (for gradual migration)
@app.post("/translate", tags=["Legacy"])
async def legacy_translate(request: dict):
    """Legacy translation endpoint for backward compatibility."""
    logger.warning("Legacy /translate endpoint used - consider migrating to /api/translate")
    
    # Forward to new translation endpoint
    from .api.translate import translate_text
    return await translate_text(request)

# Development endpoints (only in debug mode)
if settings.debug:
    @app.post("/dev/reset-stats", tags=["Development"])
    async def reset_statistics(user: dict = Depends(get_current_user)):
        """Reset translation statistics (debug only)."""
        translation_manager = app.state.translation_manager
        translation_manager.reset_statistics()
        return {"message": "Statistics reset successfully"}
    
    @app.get("/dev/cache-stats", tags=["Development"])
    async def cache_statistics():
        """Get cache statistics for all engines (debug only)."""
        translation_manager = app.state.translation_manager
        cache_stats = {}
        
        for engine in translation_manager.engines:
            if hasattr(engine, 'get_cache_stats'):
                cache_stats[engine.name] = engine.get_cache_stats()
        
        return cache_stats


def create_app() -> FastAPI:
    """Factory function to create the app (useful for testing)."""
    return app


def main():
    """Main entry point for running the server."""
    logger.info(f"Starting TauTranslator Unified Backend on {settings.host}:{settings.port}")
    
    # Run with uvicorn
    uvicorn.run(
        "backend.unified.server:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload and settings.debug,
        log_level=settings.log_level.lower(),
        access_log=settings.debug
    )


if __name__ == "__main__":
    main()