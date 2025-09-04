"""
Database model for bookings
"""

from sqlalchemy import Column, String, Float, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Booking(Base):
    """Booking database model"""
    __tablename__ = "bookings"
    
    id = Column(String, primary_key=True, index=True)
    plan_id = Column(String, ForeignKey("travel_plans.id"), nullable=False)
    selected_flight_id = Column(String, nullable=False)
    selected_hotel_id = Column(String, nullable=False)
    traveler_details = Column(JSON, nullable=False)
    payment_details = Column(JSON, nullable=True)
    flight_booking = Column(JSON, nullable=False)
    hotel_booking = Column(JSON, nullable=False)
    total_cost = Column(Float, nullable=False)
    status = Column(String, default="pending")
    confirmation_numbers = Column(JSON, nullable=True)
    itinerary = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    # Relationship
    travel_plan = relationship("TravelPlan", back_populates="bookings")


# Add relationship to TravelPlan model
from app.models.travel_plan import TravelPlan
TravelPlan.bookings = relationship("Booking", back_populates="travel_plan")
