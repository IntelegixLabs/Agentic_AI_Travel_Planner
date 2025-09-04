"""
Status tracking endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging

from app.schemas.travel import BookingStatus, ErrorResponse
from app.services.status_service import StatusService
from app.core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/booking/{booking_id}", response_model=BookingStatus)
async def get_booking_status(
    booking_id: str,
    db: AsyncSession = Depends(get_async_session)
) -> BookingStatus:
    """
    Get booking status by ID
    
    Args:
        booking_id: Booking ID
        db: Database session
        
    Returns:
        Current booking status
        
    Raises:
        HTTPException: If booking not found
    """
    try:
        logger.info(f"Retrieving booking status: {booking_id}")
        
        status_service = StatusService(db)
        status = await status_service.get_booking_status(booking_id)
        
        if not status:
            raise HTTPException(
                status_code=404,
                detail=f"Booking {booking_id} not found"
            )
        
        return status
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve booking status: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve booking status: {str(e)}"
        )


@router.get("/health", response_model=Dict[str, str])
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint for the service
    
    Returns:
        Service health status
    """
    try:
        logger.info("Performing health check")
        
        # Check database connection
        # Check external API connections
        # Check CrewAI agents
        
        return {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "version": "1.0.0"
        }
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=503,
            detail=f"Service unhealthy: {str(e)}"
        )


@router.get("/metrics", response_model=Dict[str, Any])
async def get_metrics(
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    Get service metrics
    
    Args:
        db: Database session
        
    Returns:
        Service metrics and statistics
    """
    try:
        logger.info("Retrieving service metrics")
        
        status_service = StatusService(db)
        metrics = await status_service.get_service_metrics()
        
        return metrics
        
    except Exception as e:
        logger.error(f"Failed to retrieve metrics: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve metrics: {str(e)}"
        )
