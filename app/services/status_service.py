"""
Status tracking service
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.schemas.travel import BookingStatus
from app.models.booking import Booking as BookingModel
from app.models.travel_plan import TravelPlan as TravelPlanModel

logger = logging.getLogger(__name__)


class StatusService:
    """Service for status tracking and monitoring"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_booking_status(self, booking_id: str) -> Optional[BookingStatus]:
        """
        Get booking status by ID
        
        Args:
            booking_id: Booking ID
            
        Returns:
            Current booking status
        """
        try:
            result = await self.db.execute(
                select(BookingModel).where(BookingModel.id == booking_id)
            )
            db_booking = result.scalar_one_or_none()
            
            if not db_booking:
                return None
            
            # Determine next steps based on status
            next_steps = self._get_next_steps(db_booking.status)
            
            status = BookingStatus(
                booking_id=db_booking.id,
                status=db_booking.status,
                last_updated=db_booking.updated_at,
                details={
                    "confirmation_numbers": db_booking.confirmation_numbers,
                    "total_cost": db_booking.total_cost,
                    "created_at": db_booking.created_at.isoformat()
                },
                next_steps=next_steps
            )
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get booking status: {e}")
            raise
    
    def _get_next_steps(self, status: str) -> List[str]:
        """Get next steps based on booking status"""
        next_steps_map = {
            "pending": [
                "Complete payment",
                "Receive confirmation email",
                "Check booking details"
            ],
            "confirmed": [
                "Check-in online 24 hours before departure",
                "Print boarding passes",
                "Arrive at airport 2 hours early"
            ],
            "paid": [
                "Receive confirmation email",
                "Check booking details",
                "Set up travel notifications"
            ],
            "cancelled": [
                "Check refund status",
                "Contact customer service if needed",
                "Consider alternative bookings"
            ],
            "completed": [
                "Leave a review",
                "Share travel experience",
                "Plan next trip"
            ]
        }
        
        return next_steps_map.get(status, ["Contact customer service"])
    
    async def get_service_metrics(self) -> Dict[str, Any]:
        """
        Get service metrics and statistics
        
        Returns:
            Service metrics
        """
        try:
            # Get booking statistics
            booking_stats = await self._get_booking_statistics()
            
            # Get travel plan statistics
            plan_stats = await self._get_plan_statistics()
            
            # Get system health metrics
            health_metrics = await self._get_health_metrics()
            
            return {
                "timestamp": datetime.utcnow().isoformat(),
                "bookings": booking_stats,
                "travel_plans": plan_stats,
                "system_health": health_metrics
            }
            
        except Exception as e:
            logger.error(f"Failed to get service metrics: {e}")
            raise
    
    async def _get_booking_statistics(self) -> Dict[str, Any]:
        """Get booking statistics"""
        try:
            # Total bookings
            total_result = await self.db.execute(select(func.count(BookingModel.id)))
            total_bookings = total_result.scalar()
            
            # Bookings by status
            status_result = await self.db.execute(
                select(BookingModel.status, func.count(BookingModel.id))
                .group_by(BookingModel.status)
            )
            bookings_by_status = dict(status_result.fetchall())
            
            # Recent bookings (last 24 hours)
            recent_cutoff = datetime.utcnow() - timedelta(hours=24)
            recent_result = await self.db.execute(
                select(func.count(BookingModel.id))
                .where(BookingModel.created_at >= recent_cutoff)
            )
            recent_bookings = recent_result.scalar()
            
            # Average booking value
            avg_result = await self.db.execute(
                select(func.avg(BookingModel.total_cost))
            )
            avg_booking_value = avg_result.scalar() or 0
            
            return {
                "total": total_bookings,
                "by_status": bookings_by_status,
                "recent_24h": recent_bookings,
                "average_value": round(avg_booking_value, 2)
            }
            
        except Exception as e:
            logger.error(f"Failed to get booking statistics: {e}")
            return {}
    
    async def _get_plan_statistics(self) -> Dict[str, Any]:
        """Get travel plan statistics"""
        try:
            # Total plans
            total_result = await self.db.execute(select(func.count(TravelPlanModel.id)))
            total_plans = total_result.scalar()
            
            # Active plans (not expired)
            active_result = await self.db.execute(
                select(func.count(TravelPlanModel.id))
                .where(TravelPlanModel.expires_at > datetime.utcnow())
            )
            active_plans = active_result.scalar()
            
            # Plans by destination
            dest_result = await self.db.execute(
                select(TravelPlanModel.destination, func.count(TravelPlanModel.id))
                .group_by(TravelPlanModel.destination)
                .order_by(func.count(TravelPlanModel.id).desc())
                .limit(10)
            )
            top_destinations = dict(dest_result.fetchall())
            
            return {
                "total": total_plans,
                "active": active_plans,
                "top_destinations": top_destinations
            }
            
        except Exception as e:
            logger.error(f"Failed to get plan statistics: {e}")
            return {}
    
    async def _get_health_metrics(self) -> Dict[str, Any]:
        """Get system health metrics"""
        try:
            # Database connection health
            db_health = await self._check_database_health()
            
            # External API health (mock for now)
            api_health = await self._check_api_health()
            
            return {
                "database": db_health,
                "external_apis": api_health,
                "overall_status": "healthy" if db_health["status"] == "healthy" else "degraded"
            }
            
        except Exception as e:
            logger.error(f"Failed to get health metrics: {e}")
            return {"overall_status": "unhealthy", "error": str(e)}
    
    async def _check_database_health(self) -> Dict[str, Any]:
        """Check database health"""
        try:
            # Simple query to test database connection
            result = await self.db.execute(select(1))
            result.scalar()
            
            return {
                "status": "healthy",
                "response_time_ms": 10,  # Mock response time
                "last_check": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "last_check": datetime.utcnow().isoformat()
            }
    
    async def _check_api_health(self) -> Dict[str, Any]:
        """Check external API health"""
        # Mock API health checks
        return {
            "amadeus": {"status": "healthy", "response_time_ms": 150},
            "booking_com": {"status": "healthy", "response_time_ms": 200},
            "expedia": {"status": "healthy", "response_time_ms": 180},
            "skyscanner": {"status": "healthy", "response_time_ms": 120}
        }
