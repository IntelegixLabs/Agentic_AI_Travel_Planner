"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_async_session
from app.core.config import settings


# Create test database
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test_travel_planner.db"

# Create async engine for testing
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestSessionLocal = sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def test_db():
    """Create test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="function")
async def test_session(test_db):
    """Create test database session."""
    async with TestSessionLocal() as session:
        yield session


@pytest.fixture(scope="function")
def client(test_session):
    """Create test client with database session override."""
    
    async def override_get_async_session():
        yield test_session
    
    app.dependency_overrides[get_async_session] = override_get_async_session
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def sample_travel_plan_request():
    """Sample travel plan request data."""
    return {
        "destination": "Paris, France",
        "start_date": "2024-06-15",
        "end_date": "2024-06-22",
        "budget": 2000.0,
        "travelers": 2,
        "travel_class": "economy",
        "hotel_category": "standard",
        "preferences": {
            "near_attractions": True,
            "airport_transfer": True,
            "breakfast_included": False
        }
    }


@pytest.fixture
def sample_booking_request():
    """Sample booking request data."""
    return {
        "traveler_details": {
            "primary_traveler": {
                "first_name": "John",
                "last_name": "Doe",
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "date_of_birth": "1990-01-01",
                "passport_number": "A1234567"
            },
            "additional_travelers": [
                {
                    "first_name": "Jane",
                    "last_name": "Doe",
                    "date_of_birth": "1992-05-15",
                    "passport_number": "B7654321"
                }
            ]
        },
        "payment_details": {
            "payment_method": "credit_card",
            "card_number": "4111111111111111",
            "expiry_date": "12/25",
            "cvv": "123",
            "billing_address": {
                "street": "123 Main St",
                "city": "New York",
                "state": "NY",
                "zip_code": "10001",
                "country": "USA"
            }
        }
    }


@pytest.fixture
def mock_flight_options():
    """Mock flight options data."""
    return [
        {
            "id": "flight_1",
            "airline": "Air France",
            "flight_number": "AF1234",
            "departure_time": "2024-06-15T08:00:00Z",
            "arrival_time": "2024-06-15T14:30:00Z",
            "duration": "6h 30m",
            "price": 800.0,
            "travel_class": "economy",
            "layovers": [],
            "source": "amadeus",
            "booking_url": "https://amadeus.com/book/AF1234"
        },
        {
            "id": "flight_2",
            "airline": "Delta Airlines",
            "flight_number": "DL5678",
            "departure_time": "2024-06-15T10:00:00Z",
            "arrival_time": "2024-06-15T16:45:00Z",
            "duration": "6h 45m",
            "price": 750.0,
            "travel_class": "economy",
            "layovers": ["Atlanta"],
            "source": "skyscanner",
            "booking_url": "https://skyscanner.com/book/DL5678"
        }
    ]


@pytest.fixture
def mock_hotel_options():
    """Mock hotel options data."""
    return [
        {
            "id": "hotel_1",
            "name": "Hotel des Invalides",
            "address": "123 Rue de Rivoli, Paris",
            "price_per_night": 150.0,
            "total_price": 1050.0,
            "rating": 4.5,
            "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
            "category": "standard",
            "source": "booking.com",
            "booking_url": "https://booking.com/hotel_1",
            "images": ["https://example.com/hotel_1_1.jpg"]
        },
        {
            "id": "hotel_2",
            "name": "Comfort Inn Central",
            "address": "456 Business District, Paris",
            "price_per_night": 100.0,
            "total_price": 700.0,
            "rating": 4.0,
            "amenities": ["WiFi", "Breakfast", "Parking"],
            "category": "budget",
            "source": "expedia",
            "booking_url": "https://expedia.com/hotel_2",
            "images": ["https://example.com/hotel_2_1.jpg"]
        }
    ]


@pytest.fixture
def mock_travel_plan():
    """Mock travel plan data."""
    return {
        "plan_id": "550e8400-e29b-41d4-a716-446655440000",
        "destination": "Paris, France",
        "start_date": "2024-06-15",
        "end_date": "2024-06-22",
        "budget": 2000.0,
        "travelers": 2,
        "total_cost": 1850.0,
        "budget_utilization": 92.5,
        "flight_options": [
            {
                "id": "flight_1",
                "airline": "Air France",
                "flight_number": "AF1234",
                "departure_time": "2024-06-15T08:00:00Z",
                "arrival_time": "2024-06-15T14:30:00Z",
                "duration": "6h 30m",
                "price": 800.0,
                "travel_class": "economy",
                "layovers": [],
                "source": "amadeus",
                "booking_url": "https://amadeus.com/book/AF1234"
            }
        ],
        "hotel_options": [
            {
                "id": "hotel_1",
                "name": "Hotel des Invalides",
                "address": "123 Rue de Rivoli, Paris",
                "price_per_night": 150.0,
                "total_price": 1050.0,
                "rating": 4.5,
                "amenities": ["WiFi", "Pool", "Gym", "Restaurant"],
                "category": "standard",
                "source": "booking.com",
                "booking_url": "https://booking.com/hotel_1",
                "images": ["https://example.com/hotel_1_1.jpg"]
            }
        ],
        "recommendations": [
            "Book flights 2-3 weeks in advance for best prices",
            "Consider flexible dates for better deals",
            "Check for seasonal events that might affect pricing",
            "Verify visa requirements for the destination"
        ],
        "created_at": "2024-01-01T00:00:00Z",
        "expires_at": "2024-01-02T00:00:00Z"
    }


@pytest.fixture
def mock_booking_confirmation():
    """Mock booking confirmation data."""
    return {
        "booking_id": "booking_550e8400-e29b-41d4-a716-446655440000",
        "plan_id": "550e8400-e29b-41d4-a716-446655440000",
        "flight_booking": {
            "booking_id": "FLT_flight_1_20240101000000",
            "confirmation_number": "ABC20240101000000",
            "status": "confirmed",
            "seat_assignments": ["12A", "12B"],
            "check_in_time": "24 hours before departure",
            "baggage_allowance": "1 carry-on + 1 personal item",
            "cancellation_policy": "Free cancellation within 24 hours"
        },
        "hotel_booking": {
            "booking_id": "HTL_hotel_1_20240101000000",
            "confirmation_number": "HTL20240101000000",
            "status": "confirmed",
            "room_type": "Standard Double Room",
            "check_in_time": "3:00 PM",
            "check_out_time": "11:00 AM",
            "cancellation_policy": "Free cancellation until 24 hours before check-in"
        },
        "total_cost": 1850.0,
        "status": "confirmed",
        "confirmation_numbers": {
            "flight": "ABC20240101000000",
            "hotel": "HTL20240101000000"
        },
        "created_at": "2024-01-01T00:00:00Z",
        "itinerary": {
            "destination": "Paris, France",
            "dates": {
                "start": "2024-06-15",
                "end": "2024-06-22"
            },
            "flight": {
                "airline": "Air France",
                "flight_number": "AF1234",
                "departure": "2024-06-15T08:00:00Z",
                "arrival": "2024-06-15T14:30:00Z",
                "duration": "6h 30m"
            },
            "hotel": {
                "name": "Hotel des Invalides",
                "address": "123 Rue de Rivoli, Paris",
                "check_in": "2024-06-15",
                "check_out": "2024-06-22"
            },
            "total_cost": 1850.0
        }
    }


@pytest.fixture
def mock_booking_status():
    """Mock booking status data."""
    return {
        "booking_id": "booking_550e8400-e29b-41d4-a716-446655440000",
        "status": "confirmed",
        "last_updated": "2024-01-01T00:00:00Z",
        "details": {
            "confirmation_numbers": {
                "flight": "ABC20240101000000",
                "hotel": "HTL20240101000000"
            },
            "total_cost": 1850.0,
            "created_at": "2024-01-01T00:00:00Z"
        },
        "next_steps": [
            "Check-in online 24 hours before departure",
            "Print boarding passes",
            "Arrive at airport 2 hours early"
        ]
    }


@pytest.fixture
def mock_service_metrics():
    """Mock service metrics data."""
    return {
        "timestamp": "2024-01-01T00:00:00Z",
        "bookings": {
            "total": 150,
            "by_status": {
                "confirmed": 120,
                "pending": 20,
                "cancelled": 10
            },
            "recent_24h": 5,
            "average_value": 1850.0
        },
        "travel_plans": {
            "total": 300,
            "active": 250,
            "top_destinations": {
                "Paris, France": 45,
                "Tokyo, Japan": 38,
                "New York, USA": 32
            }
        },
        "system_health": {
            "database": {
                "status": "healthy",
                "response_time_ms": 10,
                "last_check": "2024-01-01T00:00:00Z"
            },
            "external_apis": {
                "amadeus": {
                    "status": "healthy",
                    "response_time_ms": 150
                },
                "booking_com": {
                    "status": "healthy",
                    "response_time_ms": 200
                },
                "expedia": {
                    "status": "healthy",
                    "response_time_ms": 180
                },
                "skyscanner": {
                    "status": "healthy",
                    "response_time_ms": 120
                }
            },
            "overall_status": "healthy"
        }
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection."""
    for item in items:
        # Add slow marker to tests that take more than 1 second
        if "test_" in item.name and "slow" not in item.name:
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker to tests that test multiple components
        if "integration" in item.name:
            item.add_marker(pytest.mark.integration)
