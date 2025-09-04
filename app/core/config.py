"""
Configuration settings for the Travel Planner MCP Server
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    rapidapi_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # RapidAPI Travel API Endpoints
    rapidapi_flight_search_host: str = "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
    rapidapi_hotel_search_host: str = "booking-com.p.rapidapi.com"
    rapidapi_airbnb_host: str = "airbnb13.p.rapidapi.com"
    rapidapi_amadeus_host: str = "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
    
    # Database
    database_url: str = "sqlite:///./travel_planner.db"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # RapidAPI Configuration
    rapidapi_base_url: str = "https://rapidapi.com"
    rapidapi_timeout: int = 30
    
    # CrewAI Configuration
    crewai_model: str = "gpt-3.5-turbo"
    crewai_temperature: float = 0.7
    crewai_max_tokens: int = 2000
    
    # Booking Configuration
    booking_timeout: int = 30  # seconds
    max_retry_attempts: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
