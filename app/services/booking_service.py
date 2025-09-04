"""
Booking service
"""

import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid
import asyncio

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from sqlalchemy.orm import selectinload

from app.schemas.travel import BookingRequest, BookingConfirmation, BookingStatus
from app.agents.flight_agent import FlightBookingAgent
from app.agents.hotel_agent import HotelBookingAgent
from app.models.booking import Booking as BookingModel
from app.models.travel_plan import TravelPlan as TravelPlanModel

logger = logging.getLogger(__name__)


class BookingService:
    """Service for booking operations"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.flight_agent = FlightBookingAgent()
        self.hotel_agent = HotelBookingAgent()
    
    async def create_booking(self, request: BookingRequest) -> BookingConfirmation:
        """
        Create a booking for selected flight and hotel
        
        Args:
            request: Booking request details
            
        Returns:
            Booking confirmation
        """
        try:
            logger.info(f"Creating booking for plan: {request.plan_id}")
            
            # Get travel plan
            plan = await self._get_travel_plan(request.plan_id)
            if not plan:
                raise ValueError(f"Travel plan {request.plan_id} not found")
            
            # Find selected flight and hotel
            selected_flight = self._find_flight_option(plan, request.selected_flight_id)
            selected_hotel = self._find_hotel_option(plan, request.selected_hotel_id)
            
            if not selected_flight:
                raise ValueError(f"Flight option {request.selected_flight_id} not found")
            
            if not selected_hotel:
                raise ValueError(f"Hotel option {request.selected_hotel_id} not found")
            
            # Book flight and hotel concurrently
            flight_booking_task = self._book_flight(selected_flight, request.traveler_details)
            hotel_booking_task = self._book_hotel(selected_hotel, request.traveler_details, 
                                                plan.request.start_date, plan.request.end_date)
            
            flight_booking, hotel_booking = await asyncio.gather(flight_booking_task, hotel_booking_task)
            
            # Calculate total cost
            total_cost = selected_flight.price + selected_hotel.total_price
            
            # Generate booking ID
            booking_id = str(uuid.uuid4())
            
            # Create booking confirmation
            booking_confirmation = BookingConfirmation(
                booking_id=booking_id,
                plan_id=request.plan_id,
                flight_booking=flight_booking,
                hotel_booking=hotel_booking,
                total_cost=total_cost,
                status="confirmed",
                confirmation_numbers={
                    "flight": flight_booking.get("confirmation_number", ""),
                    "hotel": hotel_booking.get("confirmation_number", "")
                },
                itinerary=self._create_itinerary(plan, selected_flight, selected_hotel)
            )
            
            # Store booking in database
            await self._store_booking(booking_confirmation, request)
            
            logger.info(f"Booking created successfully: {booking_id}")
            return booking_confirmation
            
        except Exception as e:
            logger.error(f"Failed to create booking: {e}")
            raise
    
    async def _get_travel_plan(self, plan_id: str) -> Optional[Dict[str, Any]]:
        """Get travel plan from database"""
        try:
            result = await self.db.execute(
                select(TravelPlanModel).where(TravelPlanModel.id == plan_id)
            )
            db_plan = result.scalar_one_or_none()
            
            if not db_plan:
                return None
            
            return {
                "id": db_plan.id,
                "destination": db_plan.destination,
                "start_date": db_plan.start_date,
                "end_date": db_plan.end_date,
                "flight_options": db_plan.flight_options,
                "hotel_options": db_plan.hotel_options,
                "request": {
                    "start_date": db_plan.start_date,
                    "end_date": db_plan.end_date
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to get travel plan: {e}")
            raise
    
    def _find_flight_option(self, plan: Dict[str, Any], flight_id: str) -> Optional[Dict[str, Any]]:
        """Find flight option by ID"""
        for flight in plan["flight_options"]:
            if flight["id"] == flight_id:
                return flight
        return None
    
    def _find_hotel_option(self, plan: Dict[str, Any], hotel_id: str) -> Optional[Dict[str, Any]]:
        """Find hotel option by ID"""
        for hotel in plan["hotel_options"]:
            if hotel["id"] == hotel_id:
                return hotel
        return None
    
    async def _book_flight(self, flight_option: Dict[str, Any], traveler_details: Dict[str, Any]) -> Dict[str, Any]:
        """Book flight using flight agent"""
        try:
            booking_confirmation = self.flight_agent.book_flight(
                flight_option["id"], 
                traveler_details
            )
            return booking_confirmation
            
        except Exception as e:
            logger.error(f"Flight booking failed: {e}")
            raise
    
    async def _book_hotel(self, hotel_option: Dict[str, Any], traveler_details: Dict[str, Any],
                         check_in: datetime, check_out: datetime) -> Dict[str, Any]:
        """Book hotel using hotel agent"""
        try:
            booking_confirmation = self.hotel_agent.book_hotel(
                hotel_option["id"],
                traveler_details,
                check_in,
                check_out
            )
            return booking_confirmation
            
        except Exception as e:
            logger.error(f"Hotel booking failed: {e}")
            raise
    
    def _create_itinerary(self, plan: Dict[str, Any], flight: Dict[str, Any], hotel: Dict[str, Any]) -> Dict[str, Any]:
        """Create complete itinerary"""
        return {
            "destination": plan["destination"],
            "dates": {
                "start": plan["start_date"].isoformat(),
                "end": plan["end_date"].isoformat()
            },
            "flight": {
                "airline": flight["airline"],
                "flight_number": flight["flight_number"],
                "departure": flight["departure_time"],
                "arrival": flight["arrival_time"],
                "duration": flight["duration"]
            },
            "hotel": {
                "name": hotel["name"],
                "address": hotel["address"],
                "check_in": plan["start_date"].isoformat(),
                "check_out": plan["end_date"].isoformat()
            },
            "total_cost": flight["price"] + hotel["total_price"]
        }
    
    async def _store_booking(self, booking: BookingConfirmation, request: BookingRequest) -> None:
        """Store booking in database"""
        try:
            db_booking = BookingModel(
                id=booking.booking_id,
                plan_id=booking.plan_id,
                selected_flight_id=request.selected_flight_id,
                selected_hotel_id=request.selected_hotel_id,
                traveler_details=request.traveler_details,
                payment_details=request.payment_details,
                flight_booking=booking.flight_booking,
                hotel_booking=booking.hotel_booking,
                total_cost=booking.total_cost,
                status=booking.status,
                confirmation_numbers=booking.confirmation_numbers,
                itinerary=booking.itinerary
            )
            
            self.db.add(db_booking)
            await self.db.commit()
            
            logger.info(f"Booking stored in database: {booking.booking_id}")
            
        except Exception as e:
            logger.error(f"Failed to store booking: {e}")
            await self.db.rollback()
            raise
    
    async def get_booking(self, booking_id: str) -> Optional[BookingConfirmation]:
        """Get booking from database"""
        try:
            result = await self.db.execute(
                select(BookingModel).where(BookingModel.id == booking_id)
            )
            db_booking = result.scalar_one_or_none()
            
            if not db_booking:
                return None
            
            return self._db_booking_to_pydantic(db_booking)
            
        except Exception as e:
            logger.error(f"Failed to get booking: {e}")
            raise
    
    async def list_bookings(self, skip: int = 0, limit: int = 10) -> Tuple[List[BookingConfirmation], int]:
        """List bookings with pagination"""
        try:
            # Get total count
            count_result = await self.db.execute(select(BookingModel))
            total = len(count_result.scalars().all())
            
            # Get paginated results
            result = await self.db.execute(
                select(BookingModel)
                .offset(skip)
                .limit(limit)
                .order_by(BookingModel.created_at.desc())
            )
            db_bookings = result.scalars().all()
            
            # Convert to Pydantic models
            bookings = [self._db_booking_to_pydantic(booking) for booking in db_bookings]
            
            return bookings, total
            
        except Exception as e:
            logger.error(f"Failed to list bookings: {e}")
            raise
    
    async def cancel_booking(self, booking_id: str) -> None:
        """Cancel a booking"""
        try:
            # Get booking
            booking = await self.get_booking(booking_id)
            if not booking:
                logger.warning(f"Booking {booking_id} not found for cancellation")
                return
            
            # Update status in database
            result = await self.db.execute(
                select(BookingModel).where(BookingModel.id == booking_id)
            )
            db_booking = result.scalar_one_or_none()
            
            if db_booking:
                db_booking.status = "cancelled"
                db_booking.updated_at = datetime.utcnow()
                await self.db.commit()
            
            logger.info(f"Booking cancelled: {booking_id}")
            
        except Exception as e:
            logger.error(f"Failed to cancel booking: {e}")
            await self.db.rollback()
            raise
    
    async def modify_booking(self, booking_id: str, modifications: Dict[str, Any]) -> None:
        """Modify a booking"""
        try:
            # Get booking
            booking = await self.get_booking(booking_id)
            if not booking:
                logger.warning(f"Booking {booking_id} not found for modification")
                return
            
            # Apply modifications
            result = await self.db.execute(
                select(BookingModel).where(BookingModel.id == booking_id)
            )
            db_booking = result.scalar_one_or_none()
            
            if db_booking:
                # Update fields based on modifications
                if "traveler_details" in modifications:
                    db_booking.traveler_details = modifications["traveler_details"]
                
                if "special_requests" in modifications:
                    db_booking.itinerary["special_requests"] = modifications["special_requests"]
                
                db_booking.updated_at = datetime.utcnow()
                await self.db.commit()
            
            logger.info(f"Booking modified: {booking_id}")
            
        except Exception as e:
            logger.error(f"Failed to modify booking: {e}")
            await self.db.rollback()
            raise
    
    async def process_payment(self, booking_id: str, payment_details: Dict[str, Any]) -> None:
        """Process payment for booking"""
        try:
            logger.info(f"Processing payment for booking: {booking_id}")
            
            # Mock payment processing
            # In production, this would integrate with payment gateways
            
            # Update booking status
            result = await self.db.execute(
                select(BookingModel).where(BookingModel.id == booking_id)
            )
            db_booking = result.scalar_one_or_none()
            
            if db_booking:
                db_booking.status = "paid"
                db_booking.updated_at = datetime.utcnow()
                await self.db.commit()
            
            logger.info(f"Payment processed for booking: {booking_id}")
            
        except Exception as e:
            logger.error(f"Failed to process payment: {e}")
            await self.db.rollback()
            raise
    
    def _db_booking_to_pydantic(self, db_booking: BookingModel) -> BookingConfirmation:
        """Convert database model to Pydantic model"""
        return BookingConfirmation(
            booking_id=db_booking.id,
            plan_id=db_booking.plan_id,
            flight_booking=db_booking.flight_booking,
            hotel_booking=db_booking.hotel_booking,
            total_cost=db_booking.total_cost,
            status=db_booking.status,
            confirmation_numbers=db_booking.confirmation_numbers or {},
            created_at=db_booking.created_at,
            itinerary=db_booking.itinerary
        )
