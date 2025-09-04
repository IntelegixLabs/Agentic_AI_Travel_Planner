"""
Database model for travel plans
"""

from sqlalchemy import Column, String, Float, DateTime, Integer, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base


class TravelPlan(Base):
    """Travel plan database model"""
    __tablename__ = "travel_plans"
    
    id = Column(String, primary_key=True, index=True)
    destination = Column(String, nullable=False)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    budget = Column(Float, nullable=False)
    travelers = Column(Integer, default=1)
    travel_class = Column(String, default="economy")
    hotel_category = Column(String, default="standard")
    preferences = Column(JSON, nullable=True)
    total_cost = Column(Float, nullable=False)
    budget_utilization = Column(Float, nullable=False)
    flight_options = Column(JSON, nullable=False)
    hotel_options = Column(JSON, nullable=False)
    recommendations = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    expires_at = Column(DateTime, nullable=False)
    status = Column(String, default="active")
