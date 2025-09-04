"""
Hotel Booking Agent using CrewAI
"""

from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import json

from app.agents.base import BaseAgent
from app.schemas.travel import TravelPlanRequest, HotelOption, HotelCategory

logger = logging.getLogger(__name__)


class HotelBookingAgent(BaseAgent):
    """Agent responsible for hotel search and booking"""
    
    def __init__(self):
        super().__init__(
            name="HotelBookingAgent",
            role="Hotel Search and Booking Specialist",
            goal="Find the best hotel accommodations that match user preferences and budget",
            backstory="""You are an expert hotel booking specialist with deep knowledge of 
            accommodation options worldwide. You understand hotel pricing, location advantages, 
            amenities, and guest experiences. You excel at matching user preferences with 
            available properties, negotiating rates, and providing detailed information about 
            hotel features, nearby attractions, and booking policies."""
        )
    
    def search_hotels(self, request: TravelPlanRequest) -> List[HotelOption]:
        """
        Search for hotel options
        
        Args:
            request: Travel plan request
            
        Returns:
            List of hotel options
        """
        try:
            # Calculate nights
            nights = (request.end_date - request.start_date).days
            
            # Create task description
            task_description = f"""
            Search for hotel accommodations with the following criteria:
            
            Destination: {request.destination}
            Check-in: {request.start_date}
            Check-out: {request.end_date}
            Nights: {nights}
            Travelers: {request.travelers}
            Hotel Category: {request.hotel_category}
            Budget: ${request.budget}
            
            Please provide:
            1. Multiple hotel options with different price points
            2. Location analysis and proximity to attractions
            3. Amenities comparison
            4. Guest review insights
            5. Best value recommendations
            """
            
            result = self.execute_task(task_description)
            
            # Generate mock hotel options
            hotel_options = self._generate_mock_hotels(request, nights)
            
            logger.info(f"Found {len(hotel_options)} hotel options for {request.destination}")
            return hotel_options
            
        except Exception as e:
            logger.error(f"Failed to search hotels: {e}")
            raise
    
    def _generate_mock_hotels(self, request: TravelPlanRequest, nights: int) -> List[HotelOption]:
        """Generate mock hotel options for testing"""
        hotels = []
        
        # Mock hotel data
        mock_hotels = [
            {
                "name": "Grand Plaza Hotel",
                "address": "123 Main Street, Downtown",
                "price_per_night": 120.0,
                "rating": 4.5,
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant", "Spa"],
                "category": "luxury",
                "source": "booking.com"
            },
            {
                "name": "Comfort Inn Central",
                "address": "456 Business District",
                "price_per_night": 85.0,
                "rating": 4.0,
                "amenities": ["WiFi", "Breakfast", "Parking", "Business Center"],
                "category": "standard",
                "source": "expedia"
            },
            {
                "name": "Budget Stay Hostel",
                "address": "789 Backpacker Lane",
                "price_per_night": 45.0,
                "rating": 3.5,
                "amenities": ["WiFi", "Shared Kitchen", "Laundry", "Common Area"],
                "category": "budget",
                "source": "airbnb"
            }
        ]
        
        for i, hotel_data in enumerate(mock_hotels):
            total_price = hotel_data["price_per_night"] * nights
            hotel = HotelOption(
                id=f"hotel_{i+1}",
                name=hotel_data["name"],
                address=hotel_data["address"],
                price_per_night=hotel_data["price_per_night"],
                total_price=total_price,
                rating=hotel_data["rating"],
                amenities=hotel_data["amenities"],
                category=HotelCategory(hotel_data["category"]),
                source=hotel_data["source"],
                booking_url=f"https://{hotel_data['source']}.com/book/hotel_{i+1}",
                images=[f"https://example.com/hotel_{i+1}_1.jpg", f"https://example.com/hotel_{i+1}_2.jpg"]
            )
            hotels.append(hotel)
        
        return hotels
    
    def book_hotel(self, hotel_id: str, traveler_details: Dict[str, Any], 
                   check_in: datetime, check_out: datetime) -> Dict[str, Any]:
        """
        Book a hotel
        
        Args:
            hotel_id: Hotel option ID
            traveler_details: Traveler information
            check_in: Check-in date
            check_out: Check-out date
            
        Returns:
            Booking confirmation details
        """
        try:
            task_description = f"""
            Book the following hotel:
            
            Hotel ID: {hotel_id}
            Check-in: {check_in}
            Check-out: {check_out}
            Traveler Details: {json.dumps(traveler_details, indent=2)}
            
            Please provide:
            1. Booking confirmation number
            2. Room details and amenities
            3. Check-in/check-out procedures
            4. Cancellation policy
            5. Special requests handling
            """
            
            result = self.execute_task(task_description)
            
            # Mock booking confirmation
            booking_confirmation = {
                "booking_id": f"HTL_{hotel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "confirmation_number": f"HTL{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "confirmed",
                "room_type": "Standard Double Room",
                "check_in_time": "3:00 PM",
                "check_out_time": "11:00 AM",
                "cancellation_policy": "Free cancellation until 24 hours before check-in",
                "special_requests": "Late check-in requested",
                "booking_details": result
            }
            
            logger.info(f"Hotel booked successfully: {booking_confirmation['booking_id']}")
            return booking_confirmation
            
        except Exception as e:
            logger.error(f"Failed to book hotel: {e}")
            raise
