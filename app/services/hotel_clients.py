"""
Hotel booking API clients
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, date
import asyncio

from app.services.base_client import BaseAPIClient
from app.schemas.travel import HotelOption, HotelCategory
from app.core.config import settings

logger = logging.getLogger(__name__)


class BookingComClient(BaseAPIClient):
    """Booking.com API client for hotel search and booking"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.booking_com_base_url,
            api_key=settings.booking_com_api_key
        )
    
    async def search_hotels(self, destination: str, check_in: date, check_out: date,
                           travelers: int = 1, hotel_category: HotelCategory = HotelCategory.STANDARD) -> List[HotelOption]:
        """
        Search for hotels using Booking.com API
        
        Args:
            destination: Destination city
            check_in: Check-in date
            check_out: Check-out date
            travelers: Number of travelers
            hotel_category: Hotel category preference
            
        Returns:
            List of hotel options
        """
        try:
            # Mock implementation for now
            return self._get_mock_hotels(destination, check_in, check_out, travelers, hotel_category)
            
        except Exception as e:
            logger.error(f"Booking.com hotel search failed: {e}")
            return []
    
    def _get_mock_hotels(self, destination: str, check_in: date, check_out: date,
                        travelers: int, hotel_category: HotelCategory) -> List[HotelOption]:
        """Get mock hotel data for Booking.com"""
        hotels = []
        nights = (check_out - check_in).days
        
        mock_data = [
            {
                "name": "Grand Plaza Hotel",
                "address": f"123 Main Street, {destination}",
                "price_per_night": 120.0,
                "rating": 4.5,
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant", "Spa"],
                "category": "luxury"
            },
            {
                "name": "Comfort Inn Central",
                "address": f"456 Business District, {destination}",
                "price_per_night": 85.0,
                "rating": 4.0,
                "amenities": ["WiFi", "Breakfast", "Parking", "Business Center"],
                "category": "standard"
            }
        ]
        
        for i, data in enumerate(mock_data):
            total_price = data["price_per_night"] * nights
            hotel = HotelOption(
                id=f"booking_hotel_{i+1}",
                name=data["name"],
                address=data["address"],
                price_per_night=data["price_per_night"],
                total_price=total_price,
                rating=data["rating"],
                amenities=data["amenities"],
                category=HotelCategory(data["category"]),
                source="booking.com",
                booking_url=f"https://booking.com/hotel_{i+1}",
                images=[f"https://example.com/booking_hotel_{i+1}_1.jpg"]
            )
            hotels.append(hotel)
        
        return hotels
    
    async def book_hotel(self, hotel_id: str, traveler_details: Dict[str, Any],
                        check_in: date, check_out: date) -> Dict[str, Any]:
        """Book a hotel through Booking.com API"""
        try:
            # Mock booking for now
            booking_confirmation = {
                "booking_id": f"BOOKING_{hotel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "confirmation_number": f"BK{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "confirmed",
                "source": "booking.com"
            }
            
            logger.info(f"Hotel booked through Booking.com: {booking_confirmation['booking_id']}")
            return booking_confirmation
            
        except Exception as e:
            logger.error(f"Booking.com booking failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Booking.com API health"""
        try:
            # Mock health check
            return True
        except Exception as e:
            logger.error(f"Booking.com health check failed: {e}")
            return False


class ExpediaClient(BaseAPIClient):
    """Expedia API client for hotel search and booking"""
    
    def __init__(self):
        super().__init__(
            base_url=settings.expedia_base_url,
            api_key=settings.expedia_api_key
        )
    
    async def search_hotels(self, destination: str, check_in: date, check_out: date,
                           travelers: int = 1, hotel_category: HotelCategory = HotelCategory.STANDARD) -> List[HotelOption]:
        """Search for hotels using Expedia API"""
        try:
            # Mock implementation for now
            return self._get_mock_hotels(destination, check_in, check_out, travelers, hotel_category)
            
        except Exception as e:
            logger.error(f"Expedia hotel search failed: {e}")
            return []
    
    def _get_mock_hotels(self, destination: str, check_in: date, check_out: date,
                        travelers: int, hotel_category: HotelCategory) -> List[HotelOption]:
        """Get mock hotel data for Expedia"""
        hotels = []
        nights = (check_out - check_in).days
        
        mock_data = [
            {
                "name": "Hilton Garden Inn",
                "address": f"789 Downtown, {destination}",
                "price_per_night": 95.0,
                "rating": 4.2,
                "amenities": ["WiFi", "Pool", "Restaurant", "Fitness Center"],
                "category": "standard"
            },
            {
                "name": "Budget Stay Hostel",
                "address": f"321 Backpacker Lane, {destination}",
                "price_per_night": 45.0,
                "rating": 3.5,
                "amenities": ["WiFi", "Shared Kitchen", "Laundry"],
                "category": "budget"
            }
        ]
        
        for i, data in enumerate(mock_data):
            total_price = data["price_per_night"] * nights
            hotel = HotelOption(
                id=f"expedia_hotel_{i+1}",
                name=data["name"],
                address=data["address"],
                price_per_night=data["price_per_night"],
                total_price=total_price,
                rating=data["rating"],
                amenities=data["amenities"],
                category=HotelCategory(data["category"]),
                source="expedia",
                booking_url=f"https://expedia.com/hotel_{i+1}",
                images=[f"https://example.com/expedia_hotel_{i+1}_1.jpg"]
            )
            hotels.append(hotel)
        
        return hotels
    
    async def book_hotel(self, hotel_id: str, traveler_details: Dict[str, Any],
                        check_in: date, check_out: date) -> Dict[str, Any]:
        """Book a hotel through Expedia API"""
        try:
            # Mock booking for now
            booking_confirmation = {
                "booking_id": f"EXPEDIA_{hotel_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "confirmation_number": f"EX{datetime.now().strftime('%Y%m%d%H%M%S')}",
                "status": "confirmed",
                "source": "expedia"
            }
            
            logger.info(f"Hotel booked through Expedia: {booking_confirmation['booking_id']}")
            return booking_confirmation
            
        except Exception as e:
            logger.error(f"Expedia booking failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check Expedia API health"""
        try:
            # Mock health check
            return True
        except Exception as e:
            logger.error(f"Expedia health check failed: {e}")
            return False


class AirbnbClient(BaseAPIClient):
    """Airbnb API client for alternative accommodations"""
    
    def __init__(self):
        super().__init__(
            base_url="https://api.airbnb.com",
            api_key=settings.airbnb_api_key
        )
    
    async def search_accommodations(self, destination: str, check_in: date, check_out: date,
                                  travelers: int = 1) -> List[HotelOption]:
        """Search for Airbnb accommodations"""
        try:
            # Mock implementation for now
            return self._get_mock_accommodations(destination, check_in, check_out, travelers)
            
        except Exception as e:
            logger.error(f"Airbnb search failed: {e}")
            return []
    
    def _get_mock_accommodations(self, destination: str, check_in: date, check_out: date,
                               travelers: int) -> List[HotelOption]:
        """Get mock Airbnb data"""
        accommodations = []
        nights = (check_out - check_in).days
        
        mock_data = [
            {
                "name": "Cozy Downtown Apartment",
                "address": f"456 Residential Area, {destination}",
                "price_per_night": 75.0,
                "rating": 4.7,
                "amenities": ["WiFi", "Kitchen", "Washer", "Parking"],
                "category": "standard"
            }
        ]
        
        for i, data in enumerate(mock_data):
            total_price = data["price_per_night"] * nights
            accommodation = HotelOption(
                id=f"airbnb_{i+1}",
                name=data["name"],
                address=data["address"],
                price_per_night=data["price_per_night"],
                total_price=total_price,
                rating=data["rating"],
                amenities=data["amenities"],
                category=HotelCategory(data["category"]),
                source="airbnb",
                booking_url=f"https://airbnb.com/room_{i+1}",
                images=[f"https://example.com/airbnb_{i+1}_1.jpg"]
            )
            accommodations.append(accommodation)
        
        return accommodations
    
    async def health_check(self) -> bool:
        """Check Airbnb API health"""
        try:
            # Mock health check
            return True
        except Exception as e:
            logger.error(f"Airbnb health check failed: {e}")
            return False


class HotelService:
    """Service to aggregate hotel search results from multiple providers"""
    
    def __init__(self):
        self.booking_client = BookingComClient()
        self.expedia_client = ExpediaClient()
        self.airbnb_client = AirbnbClient()
    
    async def search_all_providers(self, destination: str, check_in: date, check_out: date,
                                 travelers: int = 1, hotel_category: HotelCategory = HotelCategory.STANDARD) -> List[HotelOption]:
        """
        Search hotels across all providers
        
        Args:
            destination: Destination city
            check_in: Check-in date
            check_out: Check-out date
            travelers: Number of travelers
            hotel_category: Hotel category preference
            
        Returns:
            Combined list of hotel options from all providers
        """
        try:
            # Search all providers concurrently
            tasks = [
                self.booking_client.search_hotels(destination, check_in, check_out, travelers, hotel_category),
                self.expedia_client.search_hotels(destination, check_in, check_out, travelers, hotel_category),
                self.airbnb_client.search_accommodations(destination, check_in, check_out, travelers)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Combine results and filter out exceptions
            all_hotels = []
            for result in results:
                if isinstance(result, list):
                    all_hotels.extend(result)
                else:
                    logger.warning(f"Hotel search failed: {result}")
            
            # Sort by price
            all_hotels.sort(key=lambda x: x.total_price)
            
            logger.info(f"Found {len(all_hotels)} total accommodations from all providers")
            return all_hotels
            
        except Exception as e:
            logger.error(f"Hotel service search failed: {e}")
            return []
    
    async def close(self):
        """Close all client connections"""
        await self.booking_client.close()
        await self.expedia_client.close()
        await self.airbnb_client.close()
