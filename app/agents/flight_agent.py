"""
Flight Booking Agent using CrewAI
"""

from typing import Dict, Any, List
import logging
from datetime import datetime, timedelta
import json

from app.agents.base import BaseAgent
from app.schemas.travel import TravelPlanRequest, FlightOption, TravelClass

logger = logging.getLogger(__name__)


class FlightBookingAgent(BaseAgent):
    """Agent responsible for flight search and booking"""
    
    def __init__(self):
        super().__init__(
            name="FlightBookingAgent",
            role="Flight Search and Booking Specialist",
            goal="Find the best flight options that match user requirements and budget constraints",
            backstory="""You are a seasoned flight booking specialist with extensive experience 
            working with multiple airline APIs and booking platforms. You understand airline 
            pricing strategies, route optimization, and can identify the best deals across 
            different carriers. You excel at finding alternative routes, understanding layover 
            implications, and providing detailed flight information to help users make informed 
            decisions."""
        )
    
    def search_flights(self, request: TravelPlanRequest) -> List[FlightOption]:
        """
        Search for flight options
        
        Args:
            request: Travel plan request
            
        Returns:
            List of flight options
        """
        try:
            # Create task description
            task_description = f"""
            Search for flight options with the following criteria:
            
            Destination: {request.destination}
            Departure Date: {request.start_date}
            Return Date: {request.end_date}
            Travelers: {request.travelers}
            Travel Class: {request.travel_class}
            Budget: ${request.budget}
            
            Please provide:
            1. Multiple flight options with different airlines
            2. Price comparisons and value analysis
            3. Flight duration and layover information
            4. Best booking timing recommendations
            5. Alternative routes if available
            """
            
            result = self.execute_task(task_description)
            
            # Generate mock flight options (in production, this would come from real APIs)
            flight_options = self._generate_mock_flights(request)
            
            logger.info(f"Found {len(flight_options)} flight options for {request.destination}")
            return flight_options
            
        except Exception as e:
            logger.error(f"Failed to search flights: {e}")
            raise
    
    def _generate_mock_flights(self, request: TravelPlanRequest) -> List[FlightOption]:
        """Generate mock flight options for testing"""
        flights = []
        
        # Mock flight data
        mock_flights = [
            {
                "airline": "American Airlines",
                "flight_number": "AA1234",
                "price": 450.0,
                "duration": "5h 30m",
                "layovers": ["Chicago"],
                "source": "amadeus"
            },
            {
                "airline": "Delta Airlines",
                "flight_number": "DL5678",
                "price": 520.0,
                "duration": "4h 45m",
                "layovers": [],
                "source": "skyscanner"
            },
            {
                "airline": "United Airlines",
                "flight_number": "UA9012",
                "price": 480.0,
                "duration": "6h 15m",
                "layovers": ["Denver"],
                "source": "amadeus"
            }
        ]
        
        for i, flight_data in enumerate(mock_flights):
            flight = FlightOption(
                id=f"flight_{i+1}",
                airline=flight_data["airline"],
                flight_number=flight_data["flight_number"],
                departure_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=8)),
                arrival_time=datetime.combine(request.start_date, datetime.min.time().replace(hour=13, minute=30)),
                duration=flight_data["duration"],
                price=flight_data["price"] * request.travelers,
                travel_class=request.travel_class,
                layovers=flight_data["layovers"],
                source=flight_data["source"],
                booking_url=f"https://{flight_data['source']}.com/book/{flight_data['flight_number']}"
            )
            flights.append(flight)
        
        return flights
    
    def book_flight(self, flight_id: str, traveler_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Book a flight
        
        Args:
            flight_id: Flight option ID
            traveler_details: Traveler information
            
        Returns:
            Booking confirmation details
        """
        try:
            task_description = f"""
            Book the following flight:
            
            Flight ID: {flight_id}
            Traveler Details: {json.dumps(traveler_details, indent=2)}
            
            Please provide:
            1. Booking confirmation number
            2. Seat assignments
            3. Check-in information
            4. Baggage allowance details
            5. Cancellation policy
            """
            
            result = self.execute_task(task_description)
            
            # Mock booking confirmation
            booking_confirmation = {
                "booking_id": f"FLT_{flight_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "confirmation_number": f"ABC{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "confirmed",
                "seat_assignments": ["12A", "12B"] if traveler_details.get("travelers", 1) > 1 else ["12A"],
                "check_in_time": "24 hours before departure",
                "baggage_allowance": "1 carry-on + 1 personal item",
                "cancellation_policy": "Free cancellation within 24 hours",
                "booking_details": result
            }
            
            logger.info(f"Flight booked successfully: {booking_confirmation['booking_id']}")
            return booking_confirmation
            
        except Exception as e:
            logger.error(f"Failed to book flight: {e}")
            raise
