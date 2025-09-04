"""
Configuration settings for the Travel Planner MCP Server
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # API Keys
    amadeus_api_key: Optional[str] = None
    amadeus_api_secret: Optional[str] = None
    booking_com_api_key: Optional[str] = None
    expedia_api_key: Optional[str] = None
    airbnb_api_key: Optional[str] = None
    skyscanner_api_key: Optional[str] = None
    openai_api_key: Optional[str] = None
    
    # Database
    database_url: str = "sqlite:///./travel_planner.db"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = True
    
    # Logging
    log_level: str = "INFO"
    
    # External API Configuration
    amadeus_base_url: str = "https://test.api.amadeus.com"
    booking_com_base_url: str = "https://distribution-xml.booking.com"
    expedia_base_url: str = "https://api.expedia.com"
    skyscanner_base_url: str = "https://partners.api.skyscanner.net"
    
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
