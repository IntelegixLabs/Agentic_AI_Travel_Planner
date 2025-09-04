"""
Base client for external API services
"""

import httpx
import logging
from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
import asyncio
from datetime import datetime

from app.core.config import settings

logger = logging.getLogger(__name__)


class BaseAPIClient(ABC):
    """Base class for external API clients"""
    
    def __init__(self, base_url: str, api_key: Optional[str] = None, 
                 api_secret: Optional[str] = None, timeout: int = 30):
        """
        Initialize API client
        
        Args:
            base_url: Base URL for the API
            api_key: API key for authentication
            api_secret: API secret for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url
        self.api_key = api_key
        self.api_secret = api_secret
        self.timeout = timeout
        self.client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=self._get_default_headers()
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "TravelPlanner-MCP-Server/1.0"
        }
        
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        
        return headers
    
    async def _make_request(self, method: str, endpoint: str, 
                           params: Optional[Dict] = None, 
                           data: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request to API
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            params: Query parameters
            data: Request body data
            
        Returns:
            API response data
        """
        try:
            logger.info(f"Making {method} request to {endpoint}")
            
            response = await self.client.request(
                method=method,
                url=endpoint,
                params=params,
                json=data
            )
            
            response.raise_for_status()
            result = response.json()
            
            logger.info(f"Request successful: {method} {endpoint}")
            return result
            
        except httpx.HTTPStatusError as e:
            logger.error(f"HTTP error {e.response.status_code}: {e.response.text}")
            raise
        except httpx.RequestError as e:
            logger.error(f"Request error: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise
    
    async def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        return await self._make_request("GET", endpoint, params=params)
    
    async def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        return await self._make_request("POST", endpoint, data=data)
    
    async def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make PUT request"""
        return await self._make_request("PUT", endpoint, data=data)
    
    async def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        return await self._make_request("DELETE", endpoint)
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()
    
    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the API service is healthy"""
        pass
