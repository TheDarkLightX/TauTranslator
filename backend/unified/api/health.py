"""
Health check endpoints for the unified backend.

Provides system health monitoring and status information.

Author: DarkLightX / Dana Edwards
"""

import time
import psutil
from datetime import datetime
from typing import Dict, Any
from fastapi import APIRouter, Request, Depends
from ..core.responses import create_success_response, HealthResponse
from ..core.auth import get_optional_user

router = APIRouter()

# Track startup time for uptime calculation
startup_time = time.time()


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        uptime=time.time() - startup_time
    ).dict()


@router.get("/detailed")
async def detailed_health_check(request: Request, user: dict = Depends(get_optional_user)):
    """Detailed health check with system metrics."""
    
    # Get translation manager from app state
    translation_manager = getattr(request.app.state, 'translation_manager', None)
    
    # Basic health info
    health_info = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime_seconds": time.time() - startup_time,
        "version": "2.0.0"
    }
    
    # System metrics
    try:
        health_info["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "load_average": psutil.getloadavg() if hasattr(psutil, 'getloadavg') else None
        }
    except Exception as e:
        health_info["system"] = {"error": f"Could not get system metrics: {e}"}
    
    # Translation engines health
    if translation_manager:
        try:
            engine_health = translation_manager.health_check()
            health_info["translation_engines"] = engine_health
            
            # Update overall status based on engines
            if engine_health.get("overall_status") == "critical":
                health_info["status"] = "unhealthy"
            elif engine_health.get("overall_status") == "degraded":
                health_info["status"] = "degraded"
                
        except Exception as e:
            health_info["translation_engines"] = {"error": f"Could not check engines: {e}"}
            health_info["status"] = "degraded"
    
    # Additional info for authenticated users
    if user:
        health_info["statistics"] = translation_manager.get_statistics() if translation_manager else {}
    
    return create_success_response(health_info)


@router.get("/engines")
async def engines_status(request: Request):
    """Get status of all translation engines."""
    translation_manager = getattr(request.app.state, 'translation_manager', None)
    
    if not translation_manager:
        return create_success_response({
            "engines": [],
            "message": "Translation manager not initialized"
        })
    
    engine_status = translation_manager.get_engine_status()
    return create_success_response(engine_status)


@router.get("/stats")
async def translation_statistics(request: Request, user: dict = Depends(get_optional_user)):
    """Get translation statistics (requires authentication)."""
    if not user:
        return create_success_response({
            "message": "Authentication required for detailed statistics"
        })
    
    translation_manager = getattr(request.app.state, 'translation_manager', None)
    
    if not translation_manager:
        return create_success_response({
            "statistics": {},
            "message": "Translation manager not initialized"
        })
    
    stats = translation_manager.get_statistics()
    return create_success_response(stats)


@router.get("/ping")
async def ping():
    """Simple ping endpoint for load balancers."""
    return {"ping": "pong", "timestamp": datetime.utcnow().isoformat()}


@router.get("/ready")
async def readiness_check(request: Request):
    """Kubernetes-style readiness check."""
    translation_manager = getattr(request.app.state, 'translation_manager', None)
    
    if not translation_manager:
        return create_success_response({
            "ready": False,
            "reason": "Translation manager not initialized"
        }, status_code=503)
    
    # Check if at least one engine is available
    available_engines = translation_manager.get_available_engines()
    
    if not available_engines:
        return create_success_response({
            "ready": False,
            "reason": "No translation engines available"
        }, status_code=503)
    
    return create_success_response({
        "ready": True,
        "available_engines": len(available_engines)
    })


@router.get("/live")
async def liveness_check():
    """Kubernetes-style liveness check."""
    # Simple check - if we can respond, we're alive
    return {
        "alive": True,
        "timestamp": datetime.utcnow().isoformat()
    }