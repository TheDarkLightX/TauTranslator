"""
Refactored health check endpoints following the Intentional Disclosure Principle.

This module contains only FastAPI routes and orchestration logic.
All business logic is in HealthService, all I/O in HealthInfrastructure.
Every method follows IDP Rule 2 (≤10 lines).

Copyright: DarkLightX / Dana Edwards
"""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Request, Depends, HTTPException, Query

from ..core.responses import create_success_response, HealthResponse
from ..core.auth import get_optional_user
from ..domain.health_service import HealthService, PingService
from ..domain.health_types import HealthQuery, MetricHours, EngineName
from ..infrastructure.health_infrastructure import HealthInfrastructure

router = APIRouter()

def _create_health_service(request: Request) -> HealthService:
    """Create health service with request-scoped infrastructure."""
    infrastructure = HealthInfrastructure(request)
    return HealthService(infrastructure)

@router.get("/")
async def health_check():
    """Basic health check endpoint."""
    # Note: This could use the service but kept simple for load balancer compatibility
    from ..infrastructure.health_infrastructure import startup_tracker
    
    return HealthResponse(
        status="healthy",
        uptime=startup_tracker.get_uptime_seconds()
    ).dict()

@router.get("/detailed")
async def detailed_health_check_async(
    request: Request, 
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Detailed health check with comprehensive monitoring."""
    service = _create_health_service(request)
    
    health_summary = await service.get_comprehensive_health_async(user)
    
    # Add user-specific statistics if authenticated
    if user:
        stats = await service.get_translation_statistics_async(user)
        health_data = health_summary.to_dict()
        health_data["statistics"] = stats
        return create_success_response(health_data)
    
    return create_success_response(health_summary.to_dict())

@router.get("/engines")
async def engines_status_async(request: Request):
    """Get status of all translation engines."""
    service = _create_health_service(request)
    engine_status = await service.get_engine_status_async()
    return create_success_response(engine_status)

@router.get("/stats")
async def translation_statistics_async(
    request: Request, 
    user: Optional[Dict[str, Any]] = Depends(get_optional_user)
):
    """Get translation statistics (requires authentication)."""
    if not user:
        return create_success_response({
            "message": "Authentication required for detailed statistics"
        })
    
    service = _create_health_service(request)
    stats = await service.get_translation_statistics_async(user)
    return create_success_response(stats)

@router.get("/ping")
async def ping_async():
    """Simple ping endpoint for load balancers."""
    ping_response = await PingService.ping_async()
    return ping_response

@router.get("/ready")
async def readiness_check_async(request: Request):
    """Kubernetes-style readiness check."""
    service = _create_health_service(request)
    readiness = await service.get_readiness_status_async()
    
    status_code = 503 if not readiness.ready else 200
    return create_success_response(readiness.to_dict(), status_code=status_code)

@router.get("/live")
async def liveness_check_async():
    """Kubernetes-style liveness check."""
    service = _create_health_service(None)  # No request needed for liveness
    liveness = await service.get_liveness_status_async()
    return liveness.to_dict()

@router.get("/metrics")
async def get_health_metrics_async(
    request: Request,
    hours: float = Query(1.0, description="Time window in hours", ge=0.1, le=168.0)
):
    """Get aggregated health metrics for specified time window."""
    service = _create_health_service(request)
    query = HealthQuery(time_window_hours=MetricHours(hours))
    
    result = await service.get_health_metrics_async(query)
    if isinstance(result, Exception):
        return create_success_response({
            "error": str(result),
            "metrics": {}
        })
    
    return create_success_response(result.unwrap())

@router.get("/history")
async def get_health_history_async(
    request: Request,
    engine_name: Optional[str] = Query(None, description="Filter by engine name"),
    hours: float = Query(24.0, description="Time window in hours", ge=0.1, le=168.0)
):
    """Get health check history."""
    service = _create_health_service(request)
    
    engine_filter = EngineName(engine_name) if engine_name else None
    query = HealthQuery(
        time_window_hours=MetricHours(hours),
        engine_filter=engine_filter
    )
    
    result = await service.get_health_history_async(query)
    if isinstance(result, Exception):
        return create_success_response({
            "error": str(result),
            "history": []
        })
    
    return create_success_response({"history": result.unwrap()})

@router.post("/engines/{engine_name}/reset")
async def reset_engine_health_async(request: Request, engine_name: str):
    """Reset health metrics for specific engine."""
    service = _create_health_service(request)
    result = await service.reset_engine_health_async(EngineName(engine_name))
    
    if isinstance(result, Exception):
        raise HTTPException(status_code=503, detail=str(result))
    
    success = result.unwrap()
    if not success:
        raise HTTPException(status_code=404, detail=f"Engine '{engine_name}' not found")
    
    from datetime import datetime
    return create_success_response({
        "status": "success",
        "message": f"Health metrics reset for engine '{engine_name}'",
        "timestamp": datetime.utcnow().isoformat()
    })

@router.post("/monitoring/start")
async def start_monitoring_async(request: Request):
    """Start continuous health monitoring."""
    service = _create_health_service(request)
    result = await service.start_monitoring_async()
    
    if isinstance(result, Exception):
        raise HTTPException(status_code=500, detail=str(result))
    
    monitoring_status = result.unwrap()
    return create_success_response({
        "status": "success",
        "message": "Health monitoring started",
        "monitoring_status": monitoring_status
    })

@router.post("/monitoring/stop")
async def stop_monitoring_async(request: Request):
    """Stop continuous health monitoring."""
    service = _create_health_service(request)
    result = await service.stop_monitoring_async()
    
    if isinstance(result, Exception):
        raise HTTPException(status_code=500, detail=str(result))
    
    monitoring_status = result.unwrap()
    return create_success_response({
        "status": "success",
        "message": "Health monitoring stopped",
        "monitoring_status": monitoring_status
    })

@router.get("/monitoring/status")
async def get_monitoring_status_async(request: Request):
    """Get current monitoring status."""
    service = _create_health_service(request)
    result = await service.get_monitoring_status_async()
    
    if isinstance(result, Exception):
        return create_success_response({
            "error": str(result),
            "monitoring_active": False
        })
    
    return create_success_response(result.unwrap())