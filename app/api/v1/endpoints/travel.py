"""
Travel planning endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
import logging
import uuid
from datetime import datetime, timedelta

from app.schemas.travel import TravelPlanRequest, TravelPlan, ErrorResponse
from app.services.travel_service import TravelService
from app.core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/plan", response_model=TravelPlan)
async def create_travel_plan(
    request: TravelPlanRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session)
) -> TravelPlan:
    """
    Create a comprehensive travel plan
    
    Args:
        request: Travel plan request details
        background_tasks: Background tasks for async processing
        db: Database session
        
    Returns:
        Complete travel plan with flight and hotel options
        
    Raises:
        HTTPException: If plan creation fails
    """
    try:
        logger.info(f"Creating travel plan for {request.destination}")
        
        # Initialize travel service
        travel_service = TravelService(db)
        
        # Create travel plan
        plan = await travel_service.create_travel_plan(request)
        
        # Store plan in database in background
        background_tasks.add_task(travel_service.store_plan, plan)
        
        logger.info(f"Travel plan created successfully: {plan.plan_id}")
        return plan
        
    except Exception as e:
        logger.error(f"Failed to create travel plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create travel plan: {str(e)}"
        )


@router.get("/plan/{plan_id}", response_model=TravelPlan)
async def get_travel_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_async_session)
) -> TravelPlan:
    """
    Get a travel plan by ID
    
    Args:
        plan_id: Travel plan ID
        db: Database session
        
    Returns:
        Travel plan details
        
    Raises:
        HTTPException: If plan not found
    """
    try:
        logger.info(f"Retrieving travel plan: {plan_id}")
        
        travel_service = TravelService(db)
        plan = await travel_service.get_travel_plan(plan_id)
        
        if not plan:
            raise HTTPException(
                status_code=404,
                detail=f"Travel plan {plan_id} not found"
            )
        
        return plan
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve travel plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve travel plan: {str(e)}"
        )


@router.get("/plans", response_model=Dict[str, Any])
async def list_travel_plans(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    List travel plans with pagination
    
    Args:
        skip: Number of plans to skip
        limit: Maximum number of plans to return
        db: Database session
        
    Returns:
        List of travel plans with pagination info
    """
    try:
        logger.info(f"Listing travel plans: skip={skip}, limit={limit}")
        
        travel_service = TravelService(db)
        plans, total = await travel_service.list_travel_plans(skip, limit)
        
        return {
            "plans": plans,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to list travel plans: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list travel plans: {str(e)}"
        )


@router.delete("/plan/{plan_id}")
async def delete_travel_plan(
    plan_id: str,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    """
    Delete a travel plan
    
    Args:
        plan_id: Travel plan ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If plan not found or deletion fails
    """
    try:
        logger.info(f"Deleting travel plan: {plan_id}")
        
        travel_service = TravelService(db)
        success = await travel_service.delete_travel_plan(plan_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail=f"Travel plan {plan_id} not found"
            )
        
        return {"message": f"Travel plan {plan_id} deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete travel plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete travel plan: {str(e)}"
        )


@router.post("/plan/{plan_id}/refresh")
async def refresh_travel_plan(
    plan_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    """
    Refresh a travel plan with updated prices and availability
    
    Args:
        plan_id: Travel plan ID
        background_tasks: Background tasks for async processing
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If plan not found or refresh fails
    """
    try:
        logger.info(f"Refreshing travel plan: {plan_id}")
        
        travel_service = TravelService(db)
        
        # Check if plan exists
        existing_plan = await travel_service.get_travel_plan(plan_id)
        if not existing_plan:
            raise HTTPException(
                status_code=404,
                detail=f"Travel plan {plan_id} not found"
            )
        
        # Refresh plan in background
        background_tasks.add_task(travel_service.refresh_plan, plan_id)
        
        return {"message": f"Travel plan {plan_id} refresh initiated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to refresh travel plan: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to refresh travel plan: {str(e)}"
        )
