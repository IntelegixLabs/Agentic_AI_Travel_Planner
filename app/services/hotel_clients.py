"""
Hotel booking API clients using RapidAPI
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import asyncio

from app.services.rapidapi_client import RapidAPIClient
from app.schemas.travel import HotelOption, HotelCategory
from app.core.config import settings

logger = logging.getLogger(__name__)


class HotelService:
    """Service to search hotels using RapidAPI"""
    
    def __init__(self):
        self.rapidapi_client = RapidAPIClient()
    
    async def search_all_providers(self, destination: str, check_in: date, check_out: date,
                                 travelers: int = 1, hotel_category: HotelCategory = HotelCategory.STANDARD) -> List[HotelOption]:
        """
        Search hotels using RapidAPI
        
        Args:
            destination: Destination city
            check_in: Check-in date
            check_out: Check-out date
            travelers: Number of travelers
            hotel_category: Hotel category preference
            
        Returns:
            List of hotel options from RapidAPI
        """
        try:
            # Search hotels and Airbnb concurrently
            hotel_task = self.rapidapi_client.search_hotels(destination, check_in, check_out, travelers, hotel_category.value)
            airbnb_task = self.rapidapi_client.search_airbnb(destination, check_in, check_out, travelers)
            
            hotel_data, airbnb_data = await asyncio.gather(hotel_task, airbnb_task, return_exceptions=True)
            
            # Combine results
            all_hotel_data = []
            if isinstance(hotel_data, list):
                all_hotel_data.extend(hotel_data)
            if isinstance(airbnb_data, list):
                all_hotel_data.extend(airbnb_data)
            
            # Convert to HotelOption objects
            hotel_options = []
            for hotel in all_hotel_data:
                try:
                    hotel_option = HotelOption(
                        id=hotel["id"],
                        name=hotel["name"],
                        address=hotel["address"],
                        price_per_night=hotel["price_per_night"],
                        total_price=hotel["total_price"],
                        rating=hotel["rating"],
                        amenities=hotel["amenities"],
                        category=HotelCategory(hotel["category"]),
                        source=hotel["source"],
                        booking_url=hotel["booking_url"],
                        images=hotel["images"] if isinstance(hotel["images"], list) else [hotel["images"]]
                    )
                    hotel_options.append(hotel_option)
                except Exception as e:
                    logger.warning(f"Failed to convert hotel data: {e}")
                    continue
            
            # Sort by price
            hotel_options.sort(key=lambda x: x.total_price)
            
            logger.info(f"Found {len(hotel_options)} accommodations from RapidAPI")
            return hotel_options
            
        except Exception as e:
            logger.error(f"Hotel service search failed: {e}")
            return []
    
    async def close(self):
        """Close client connections"""
        await self.rapidapi_client.close()
