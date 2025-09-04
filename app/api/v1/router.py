"""
Main API router for v1 endpoints
"""

from fastapi import APIRouter
from app.api.v1.endpoints import travel, booking, status

api_router = APIRouter()

# Include all endpoint routers
api_router.include_router(travel.router, prefix="/travel", tags=["travel"])
api_router.include_router(booking.router, prefix="/booking", tags=["booking"])
api_router.include_router(status.router, prefix="/status", tags=["status"])
