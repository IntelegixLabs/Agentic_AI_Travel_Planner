"""
Flight booking API clients using RapidAPI
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import asyncio

from app.services.rapidapi_client import RapidAPIClient
from app.schemas.travel import FlightOption, TravelClass
from app.core.config import settings

logger = logging.getLogger(__name__)


class FlightService:
    """Service to search flights using RapidAPI"""
    
    def __init__(self):
        self.rapidapi_client = RapidAPIClient()
    
    async def search_all_providers(self, origin: str, destination: str, 
                                 departure_date: date, return_date: Optional[date] = None,
                                 travelers: int = 1, travel_class: TravelClass = TravelClass.ECONOMY) -> List[FlightOption]:
        """
        Search flights using RapidAPI
        
        Args:
            origin: Origin airport code
            destination: Destination airport code
            departure_date: Departure date
            return_date: Return date
            travelers: Number of travelers
            travel_class: Travel class
            
        Returns:
            List of flight options from RapidAPI
        """
        try:
            # Search flights using RapidAPI
            flight_data = await self.rapidapi_client.search_flights(
                origin, destination, departure_date, return_date, travelers, travel_class.value
            )
            
            # Convert to FlightOption objects
            flight_options = []
            for flight in flight_data:
                try:
                    flight_option = FlightOption(
                        id=flight["id"],
                        airline=flight["airline"],
                        flight_number=flight["flight_number"],
                        departure_time=datetime.fromisoformat(flight["departure_time"]),
                        arrival_time=datetime.fromisoformat(flight["arrival_time"]),
                        duration=flight["duration"],
                        price=flight["price"],
                        travel_class=TravelClass(flight["travel_class"]),
                        layovers=flight["layovers"],
                        source=flight["source"],
                        booking_url=flight["booking_url"]
                    )
                    flight_options.append(flight_option)
                except Exception as e:
                    logger.warning(f"Failed to convert flight data: {e}")
                    continue
            
            # Sort by price
            flight_options.sort(key=lambda x: x.price)
            
            logger.info(f"Found {len(flight_options)} flights from RapidAPI")
            return flight_options
            
        except Exception as e:
            logger.error(f"Flight service search failed: {e}")
            return []
    
    async def close(self):
        """Close client connections"""
        await self.rapidapi_client.close()
