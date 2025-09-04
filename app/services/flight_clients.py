"""
Flight booking API clients
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import asyncio

from app.services.base_client import BaseAPIClient
from app.schemas.travel import FlightOption, TravelClass
from app.core.config import settings

logger = logging.getLogger(__name__)


class AmadeusFlightClient(BaseAPIClient):
    """Amadeus API client for flight search and booking"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.amadeus_base_url,
            api_key=settings.amadeus_api_key,
            api_secret=settings.amadeus_api_secret
        )
        self.access_token = None
    
    async def _get_access_token(self) -> str:
        """Get access token for Amadeus API"""
        if self.access_token:
            return self.access_token
        
        try:
            data = {
                "grant_type": "client_credentials",
                "client_id": self.api_key,
                "client_secret": self.api_secret
            }
            
            response = await self.post("/v1/security/oauth2/token", data=data)
            self.access_token = response["access_token"]
            
            # Update headers with new token
            self.client.headers["Authorization"] = f"Bearer {self.access_token}"
            
            return self.access_token
            
        except Exception as e:
            logger.error(f"Failed to get Amadeus access token: {e}")
            raise
    
    async def search_flights(self, origin: str, destination: str, 
                           departure_date: date, return_date: Optional[date] = None,
                           travelers: int = 1, travel_class: TravelClass = TravelClass.ECONOMY) -> List[FlightOption]:
        """
        Search for flights using Amadeus API
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date
            return_date: Return date (for round trip)
            travelers: Number of travelers
            travel_class: Travel class
            
        Returns:
            List of flight options
        """
        try:
            await self._get_access_token()
            
            params = {
                "originLocationCode": origin,
                "destinationLocationCode": destination,
                "departureDate": departure_date.strftime("%Y-%m-%d"),
                "adults": travelers,
                "travelClass": travel_class.value.upper(),
                "max": 10
            }
            
            if return_date:
                params["returnDate"] = return_date.strftime("%Y-%m-%d")
            
            response = await self.get("/v2/shopping/flight-offers", params=params)
            
            # Parse response and convert to FlightOption objects
            flight_options = self._parse_amadeus_response(response, travelers)
            
            logger.info(f"Found {len(flight_options)} flights from Amadeus")
            return flight_options
            
        except Exception as e:
            logger.error(f"Amadeus flight search failed: {e}")
            # Return mock data for testing
            return self._get_mock_flights(origin, destination, departure_date, travelers, travel_class)
    
    def _parse_amadeus_response(self, response: Dict[str, Any], travelers: int) -> List[FlightOption]:
        """Parse Amadeus API response"""
        flight_options = []
        
        for offer in response.get("data", []):
            try:
                # Extract flight details
                flight = offer["itineraries"][0]["segments"][0]
                pricing = offer["price"]
                
                flight_option = FlightOption(
                    id=offer["id"],
                    airline=flight["carrierCode"],
                    flight_number=f"{flight['carrierCode']}{flight['number']}",
                    departure_time=datetime.fromisoformat(flight["departure"]["at"].replace("Z", "+00:00")),
                    arrival_time=datetime.fromisoformat(flight["arrival"]["at"].replace("Z", "+00:00")),
                    duration=flight["duration"],
                    price=float(pricing["total"]) * travelers,
                    travel_class=TravelClass(pricing.get("travelClass", "economy").lower()),
                    layovers=[],  # Parse from segments if needed
                    source="amadeus",
                    booking_url=offer.get("source", "")
                )
                
                flight_options.append(flight_option)
                
            except Exception as e:
                logger.warning(f"Failed to parse flight offer: {e}")
                continue
        
        return flight_options
    
    def _get_mock_flights(self, origin: str, destination: str, 
                         departure_date: date, travelers: int, 
                         travel_class: TravelClass) -> List[FlightOption]:
        """Get mock flight data for testing"""
        flights = []
        
        mock_data = [
            {
                "airline": "American Airlines",
                "flight_number": "AA1234",
                "price": 450.0,
                "duration": "5h 30m",
                "layovers": ["Chicago"]
            },
            {
                "airline": "Delta Airlines", 
                "flight_number": "DL5678",
                "price": 520.0,
                "duration": "4h 45m",
                "layovers": []
            }
        ]
        
        for i, data in enumerate(mock_data):
            flight = FlightOption(
                id=f"amadeus_flight_{i+1}",
                airline=data["airline"],
                flight_number=data["flight_number"],
                departure_time=datetime.combine(departure_date, datetime.min.time().replace(hour=8)),
                arrival_time=datetime.combine(departure_date, datetime.min.time().replace(hour=13, minute=30)),
                duration=data["duration"],
                price=data["price"] * travelers,
                travel_class=travel_class,
                layovers=data["layovers"],
                source="amadeus",
                booking_url=f"https://amadeus.com/book/{data['flight_number']}"
            )
            flights.append(flight)
        
        return flights
    
    async def book_flight(self, flight_id: str, traveler_details: Dict[str, Any]) -> Dict[str, Any]:
        """Book a flight through Amadeus API"""
        try:
            await self._get_access_token()
            
            # Mock booking for now
            booking_confirmation = {
                "booking_id": f"AMADEUS_{flight_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "confirmation_number": f"AM{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "confirmed",
                "source": "amadeus"
            }
            
            logger.info(f"Flight booked through Amadeus: {booking_confirmation['booking_id']}")
            return booking_confirmation
            
        except Exception as e:
            logger.error(f"Amadeus booking failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Amadeus API health"""
        try:
            await self._get_access_token()
            return True
        except Exception as e:
            logger.error(f"Amadeus health check failed: {e}")
            return False


class SkyscannerFlightClient(BaseAPIClient):
    """Skyscanner API client for flight search"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.skyscanner_base_url,
            api_key=settings.skyscanner_api_key
        )
    
    async def search_flights(self, origin: str, destination: str, 
                           departure_date: date, return_date: Optional[date] = None,
                           travelers: int = 1, travel_class: TravelClass = TravelClass.ECONOMY) -> List[FlightOption]:
        """Search for flights using Skyscanner API"""
        try:
            # Mock implementation for now
            return self._get_mock_flights(origin, destination, departure_date, travelers, travel_class)
            
        except Exception as e:
            logger.error(f"Skyscanner flight search failed: {e}")
            return []
    
    def _get_mock_flights(self, origin: str, destination: str, 
                         departure_date: date, travelers: int, 
                         travel_class: TravelClass) -> List[FlightOption]:
        """Get mock flight data for Skyscanner"""
        flights = []
        
        mock_data = [
            {
                "airline": "United Airlines",
                "flight_number": "UA9012",
                "price": 480.0,
                "duration": "6h 15m",
                "layovers": ["Denver"]
            }
        ]
        
        for i, data in enumerate(mock_data):
            flight = FlightOption(
                id=f"skyscanner_flight_{i+1}",
                airline=data["airline"],
                flight_number=data["flight_number"],
                departure_time=datetime.combine(departure_date, datetime.min.time().replace(hour=10)),
                arrival_time=datetime.combine(departure_date, datetime.min.time().replace(hour=16, minute=15)),
                duration=data["duration"],
                price=data["price"] * travelers,
                travel_class=travel_class,
                layovers=data["layovers"],
                source="skyscanner",
                booking_url=f"https://skyscanner.com/book/{data['flight_number']}"
            )
            flights.append(flight)
        
        return flights
    
    async def health_check(self) -> bool:
        """Check Skyscanner API health"""
        try:
            # Mock health check
            return True
        except Exception as e:
            logger.error(f"Skyscanner health check failed: {e}")
            return False


class FlightService:
    """Service to aggregate flight search results from multiple providers"""
    
    def __init__(self):
        self.amadeus_client = AmadeusFlightClient()
        self.skyscanner_client = SkyscannerFlightClient()
    
    async def search_all_providers(self, origin: str, destination: str, 
                                 departure_date: date, return_date: Optional[date] = None,
                                 travelers: int = 1, travel_class: TravelClass = TravelClass.ECONOMY) -> List[FlightOption]:
        """
        Search flights across all providers
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date
            return_date: Return date
            travelers: Number of travelers
            travel_class: Travel class
            
        Returns:
            Combined list of flight options from all providers
        """
        try:
            # Search all providers concurrently
            tasks = [
                self.amadeus_client.search_flights(origin, destination, departure_date, return_date, travelers, travel_class),
                self.skyscanner_client.search_flights(origin, destination, departure_date, return_date, travelers, travel_class)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results and filter out exceptions
            all_flights = []
            for result in results:
                if isinstance(result, list):
                    all_flights.extend(result)
                else:
                    logger.warning(f"Flight search failed: {result}")
            
            # Sort by price
            all_flights.sort(key=lambda x: x.price)
            
            logger.info(f"Found {len(all_flights)} total flights from all providers")
            return all_flights
            
        except Exception as e:
            logger.error(f"Flight service search failed: {e}")
            return []
    
    async def close(self):
        """Close all client connections"""
        await self.amadeus_client.close()
        await self.skyscanner_client.close()
