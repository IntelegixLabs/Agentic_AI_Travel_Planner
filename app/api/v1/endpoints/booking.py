"""
Booking endpoints
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from typing import Dict, Any
import logging
import uuid
from datetime import datetime

from app.schemas.travel import BookingRequest, BookingConfirmation, ErrorResponse
from app.services.booking_service import BookingService
from app.core.database import get_async_session
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/book", response_model=BookingConfirmation)
async def create_booking(
    request: BookingRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session)
) -> BookingConfirmation:
    """
    Create a booking for selected flight and hotel
    
    Args:
        request: Booking request details
        background_tasks: Background tasks for async processing
        db: Database session
        
    Returns:
        Booking confirmation with details
        
    Raises:
        HTTPException: If booking fails
    """
    try:
        logger.info(f"Creating booking for plan: {request.plan_id}")
        
        # Initialize booking service
        booking_service = BookingService(db)
        
        # Create booking
        booking = await booking_service.create_booking(request)
        
        # Process payment in background if provided
        if request.payment_details:
            background_tasks.add_task(booking_service.process_payment, booking.booking_id, request.payment_details)
        
        logger.info(f"Booking created successfully: {booking.booking_id}")
        return booking
        
    except Exception as e:
        logger.error(f"Failed to create booking: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create booking: {str(e)}"
        )


@router.get("/booking/{booking_id}", response_model=BookingConfirmation)
async def get_booking(
    booking_id: str,
    db: AsyncSession = Depends(get_async_session)
) -> BookingConfirmation:
    """
    Get booking details by ID
    
    Args:
        booking_id: Booking ID
        db: Database session
        
    Returns:
        Booking confirmation details
        
    Raises:
        HTTPException: If booking not found
    """
    try:
        logger.info(f"Retrieving booking: {booking_id}")
        
        booking_service = BookingService(db)
        booking = await booking_service.get_booking(booking_id)
        
        if not booking:
            raise HTTPException(
                status_code=404,
                detail=f"Booking {booking_id} not found"
            )
        
        return booking
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to retrieve booking: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve booking: {str(e)}"
        )


@router.get("/bookings", response_model=Dict[str, Any])
async def list_bookings(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, Any]:
    """
    List bookings with pagination
    
    Args:
        skip: Number of bookings to skip
        limit: Maximum number of bookings to return
        db: Database session
        
    Returns:
        List of bookings with pagination info
    """
    try:
        logger.info(f"Listing bookings: skip={skip}, limit={limit}")
        
        booking_service = BookingService(db)
        bookings, total = await booking_service.list_bookings(skip, limit)
        
        return {
            "bookings": bookings,
            "total": total,
            "skip": skip,
            "limit": limit
        }
        
    except Exception as e:
        logger.error(f"Failed to list bookings: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to list bookings: {str(e)}"
        )


@router.post("/booking/{booking_id}/cancel")
async def cancel_booking(
    booking_id: str,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    """
    Cancel a booking
    
    Args:
        booking_id: Booking ID
        background_tasks: Background tasks for async processing
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If booking not found or cancellation fails
    """
    try:
        logger.info(f"Cancelling booking: {booking_id}")
        
        booking_service = BookingService(db)
        
        # Check if booking exists
        existing_booking = await booking_service.get_booking(booking_id)
        if not existing_booking:
            raise HTTPException(
                status_code=404,
                detail=f"Booking {booking_id} not found"
            )
        
        # Cancel booking in background
        background_tasks.add_task(booking_service.cancel_booking, booking_id)
        
        return {"message": f"Booking {booking_id} cancellation initiated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to cancel booking: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to cancel booking: {str(e)}"
        )


@router.post("/booking/{booking_id}/modify")
async def modify_booking(
    booking_id: str,
    modifications: Dict[str, Any],
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_async_session)
) -> Dict[str, str]:
    """
    Modify a booking
    
    Args:
        booking_id: Booking ID
        modifications: Requested modifications
        background_tasks: Background tasks for async processing
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If booking not found or modification fails
    """
    try:
        logger.info(f"Modifying booking: {booking_id}")
        
        booking_service = BookingService(db)
        
        # Check if booking exists
        existing_booking = await booking_service.get_booking(booking_id)
        if not existing_booking:
            raise HTTPException(
                status_code=404,
                detail=f"Booking {booking_id} not found"
            )
        
        # Modify booking in background
        background_tasks.add_task(booking_service.modify_booking, booking_id, modifications)
        
        return {"message": f"Booking {booking_id} modification initiated"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to modify booking: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to modify booking: {str(e)}"
        )
