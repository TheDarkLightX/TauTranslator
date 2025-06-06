"""
Health check endpoints for the unified backend.

Provides system health monitoring and status information.
Enhanced with comprehensive health monitoring via TranslationHealthMonitor.

Author: DarkLightX / Dana Edwards
"""

import time
import psutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from fastapi import APIRouter, Request, Depends, HTTPException, Query
from ..core.responses import create_success_response, HealthResponse
from ..core.auth import get_optional_user
from ..core.health_monitor import TranslationHealthMonitor, HealthStatus
from ..core.dependency_injection import get_container

router = APIRouter()

# Track startup time for uptime calculation
startup_time = time.time()


def get_health_monitor(request: Request) -> Optional[TranslationHealthMonitor]:
    """Get health monitor from app state or dependency injection."""
    # Try app state first
    manager = getattr(request.app.state, 'translation_manager', None)
    if manager and hasattr(manager, 'health_monitor'):
        return manager.health_monitor
    
    # Try dependency injection
    try:
        container = get_container()
        return container.resolve(TranslationHealthMonitor)
    except:
        return None


@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    return HealthResponse(
        status="healthy",
        uptime=time.time() - startup_time
    ).dict()


@router.get("/detailed")
async def detailed_health_check(request: Request, user: dict = Depends(get_optional_user)):
    """Detailed health check with system metrics and enhanced monitoring."""
    
    # Get translation manager and health monitor
    translation_manager = getattr(request.app.state, 'translation_manager', None)
    health_monitor = get_health_monitor(request)
    
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
    
    # Enhanced health monitoring if available
    if health_monitor:
        try:
            overall_health = health_monitor.get_overall_health()
            health_info["overall_health"] = overall_health
            health_info["status"] = overall_health["status"]
            
            # Get per-engine health
            engine_health = health_monitor.get_engine_health()
            health_info["engines"] = engine_health
            
            # Get recent metrics
            metrics = health_monitor.get_health_metrics(hours=1.0)
            health_info["recent_metrics"] = metrics
            
            # Get monitoring status
            monitoring = health_monitor.get_monitoring_status()
            health_info["monitoring"] = monitoring
            
        except Exception as e:
            health_info["health_monitor_error"] = str(e)
    
    # Legacy translation manager health check
    elif translation_manager:
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
    if user and translation_manager:
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


# Enhanced health monitoring endpoints

@router.get("/metrics")
async def get_health_metrics(
    request: Request,
    hours: float = Query(1.0, description="Time window in hours", ge=0.1, le=168.0)
):
    """Get aggregated health metrics for specified time window."""
    health_monitor = get_health_monitor(request)
    
    if not health_monitor:
        return create_success_response({
            "error": "Health monitor not available",
            "metrics": {}
        })
    
    metrics = health_monitor.get_health_metrics(hours=hours)
    return create_success_response(metrics)


@router.get("/history")
async def get_health_history(
    request: Request,
    engine_name: Optional[str] = Query(None, description="Filter by engine name"),
    hours: float = Query(24.0, description="Time window in hours", ge=0.1, le=168.0)
):
    """Get health check history."""
    health_monitor = get_health_monitor(request)
    
    if not health_monitor:
        return create_success_response({
            "error": "Health monitor not available",
            "history": []
        })
    
    history = health_monitor.get_health_history(engine_name=engine_name, hours=hours)
    return create_success_response({"history": history})


@router.post("/engines/{engine_name}/reset")
async def reset_engine_health(request: Request, engine_name: str):
    """Reset health metrics for specific engine."""
    health_monitor = get_health_monitor(request)
    
    if not health_monitor:
        raise HTTPException(status_code=503, detail="Health monitor not available")
    
    success = health_monitor.reset_engine_health(engine_name)
    if not success:
        raise HTTPException(status_code=404, detail=f"Engine '{engine_name}' not found")
    
    return create_success_response({
        "status": "success",
        "message": f"Health metrics reset for engine '{engine_name}'",
        "timestamp": datetime.utcnow().isoformat()
    })


@router.post("/monitoring/start")
async def start_monitoring(request: Request):
    """Start continuous health monitoring."""
    health_monitor = get_health_monitor(request)
    
    if not health_monitor:
        raise HTTPException(status_code=503, detail="Health monitor not available")
    
    translation_manager = getattr(request.app.state, 'translation_manager', None)
    if not translation_manager:
        raise HTTPException(status_code=503, detail="Translation manager not available")
    
    try:
        # Build engine instances map
        engines_map = {}
        if hasattr(translation_manager, 'orchestrator'):
            for engine in translation_manager.orchestrator.engines:
                engines_map[engine.metadata.name] = engine
        else:
            # Legacy support
            for engine in translation_manager.engines:
                engines_map[engine.name] = engine
        
        health_monitor.start_continuous_monitoring(engines_map)
        
        return create_success_response({
            "status": "success",
            "message": "Health monitoring started",
            "monitoring_status": health_monitor.get_monitoring_status()
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to start monitoring: {str(e)}")


@router.post("/monitoring/stop")
async def stop_monitoring(request: Request):
    """Stop continuous health monitoring."""
    health_monitor = get_health_monitor(request)
    
    if not health_monitor:
        raise HTTPException(status_code=503, detail="Health monitor not available")
    
    health_monitor.stop_continuous_monitoring()
    
    return create_success_response({
        "status": "success",
        "message": "Health monitoring stopped",
        "monitoring_status": health_monitor.get_monitoring_status()
    })


@router.get("/monitoring/status")
async def get_monitoring_status(request: Request):
    """Get current monitoring status."""
    health_monitor = get_health_monitor(request)
    
    if not health_monitor:
        return create_success_response({
            "error": "Health monitor not available",
            "monitoring_active": False
        })
    
    return create_success_response(health_monitor.get_monitoring_status())