"""
Pydantic schemas for travel planning and booking
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime, date
from enum import Enum


class TravelClass(str, Enum):
    """Flight travel class options"""
    ECONOMY = "economy"
    PREMIUM_ECONOMY = "premium_economy"
    BUSINESS = "business"
    FIRST = "first"


class HotelCategory(str, Enum):
    """Hotel category options"""
    BUDGET = "budget"
    STANDARD = "standard"
    LUXURY = "luxury"
    RESORT = "resort"


class TravelPlanRequest(BaseModel):
    """Request schema for travel planning"""
    destination: str = Field(..., description="Destination city or country")
    start_date: date = Field(..., description="Travel start date")
    end_date: date = Field(..., description="Travel end date")
    budget: float = Field(..., gt=0, description="Total budget in USD")
    travelers: int = Field(1, ge=1, le=10, description="Number of travelers")
    travel_class: TravelClass = Field(TravelClass.ECONOMY, description="Preferred travel class")
    hotel_category: HotelCategory = Field(HotelCategory.STANDARD, description="Preferred hotel category")
    preferences: Optional[Dict[str, Any]] = Field(None, description="Additional preferences")
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """Validate that end date is after start date"""
        if 'start_date' in values and v <= values['start_date']:
            raise ValueError('End date must be after start date')
        return v


class FlightOption(BaseModel):
    """Flight option schema"""
    id: str = Field(..., description="Unique flight option ID")
    airline: str = Field(..., description="Airline name")
    flight_number: str = Field(..., description="Flight number")
    departure_time: datetime = Field(..., description="Departure time")
    arrival_time: datetime = Field(..., description="Arrival time")
    duration: str = Field(..., description="Flight duration")
    price: float = Field(..., gt=0, description="Price in USD")
    travel_class: TravelClass = Field(..., description="Travel class")
    layovers: List[str] = Field(default_factory=list, description="Layover cities")
    source: str = Field(..., description="Source platform (amadeus, skyscanner, etc.)")
    booking_url: Optional[str] = Field(None, description="Direct booking URL")


class HotelOption(BaseModel):
    """Hotel option schema"""
    id: str = Field(..., description="Unique hotel option ID")
    name: str = Field(..., description="Hotel name")
    address: str = Field(..., description="Hotel address")
    price_per_night: float = Field(..., gt=0, description="Price per night in USD")
    total_price: float = Field(..., gt=0, description="Total price for stay")
    rating: float = Field(..., ge=0, le=5, description="Hotel rating")
    amenities: List[str] = Field(default_factory=list, description="Available amenities")
    category: HotelCategory = Field(..., description="Hotel category")
    source: str = Field(..., description="Source platform (booking.com, expedia, etc.)")
    booking_url: Optional[str] = Field(None, description="Direct booking URL")
    images: List[str] = Field(default_factory=list, description="Hotel images")


class TravelPlan(BaseModel):
    """Complete travel plan schema"""
    plan_id: str = Field(..., description="Unique plan ID")
    request: TravelPlanRequest = Field(..., description="Original request")
    total_cost: float = Field(..., description="Total estimated cost")
    budget_utilization: float = Field(..., description="Budget utilization percentage")
    flight_options: List[FlightOption] = Field(..., description="Available flight options")
    hotel_options: List[HotelOption] = Field(..., description="Available hotel options")
    recommendations: List[str] = Field(..., description="AI recommendations")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Plan creation time")
    expires_at: datetime = Field(..., description="Plan expiration time")


class BookingRequest(BaseModel):
    """Request schema for booking"""
    plan_id: str = Field(..., description="Travel plan ID")
    selected_flight_id: str = Field(..., description="Selected flight option ID")
    selected_hotel_id: str = Field(..., description="Selected hotel option ID")
    traveler_details: Dict[str, Any] = Field(..., description="Traveler information")
    payment_details: Optional[Dict[str, Any]] = Field(None, description="Payment information")


class BookingConfirmation(BaseModel):
    """Booking confirmation schema"""
    booking_id: str = Field(..., description="Unique booking ID")
    plan_id: str = Field(..., description="Travel plan ID")
    flight_booking: Dict[str, Any] = Field(..., description="Flight booking details")
    hotel_booking: Dict[str, Any] = Field(..., description="Hotel booking details")
    total_cost: float = Field(..., description="Total booking cost")
    status: str = Field(..., description="Booking status")
    confirmation_numbers: Dict[str, str] = Field(..., description="Confirmation numbers")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Booking time")
    itinerary: Dict[str, Any] = Field(..., description="Complete itinerary")


class BookingStatus(BaseModel):
    """Booking status schema"""
    booking_id: str = Field(..., description="Booking ID")
    status: str = Field(..., description="Current status")
    last_updated: datetime = Field(..., description="Last status update")
    details: Dict[str, Any] = Field(..., description="Status details")
    next_steps: List[str] = Field(default_factory=list, description="Next steps")


class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Error details")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")
