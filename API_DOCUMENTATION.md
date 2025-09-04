# AI Travel Planner MCP Server - API Documentation

## Overview

The AI Travel Planner MCP Server provides a comprehensive REST API for intelligent travel planning and booking. The API is built with FastAPI and follows RESTful principles with automatic OpenAPI documentation.

## Base URL

```
http://localhost:8000/api/v1
```

## Authentication

The API uses RapidAPI for external travel services. You need to provide a RapidAPI key in your environment variables:

```bash
RAPIDAPI_KEY=your_rapidapi_key_here
```

For production deployment, implement additional API key authentication or OAuth2 for client access.

## Content Type

All requests and responses use `application/json` content type.

## Error Handling

The API uses standard HTTP status codes and returns error responses in the following format:

```json
{
    "error": "Error message",
    "details": {
        "field": "Additional error details"
    },
    "timestamp": "2024-01-01T00:00:00Z"
}
```

## Travel Planning Endpoints

### Create Travel Plan

**POST** `/travel/plan`

Creates a comprehensive travel plan using AI agents to search for flights and hotels.

#### Request Body

```json
{
    "destination": "Paris, France",
    "start_date": "2024-06-15",
    "end_date": "2024-06-22",
    "budget": 2000.0,
    "travelers": 2,
    "travel_class": "economy",
    "hotel_category": "standard",
    "preferences": {
        "near_attractions": true,
        "airport_transfer": true,
        "breakfast_included": false
    }
}
```

#### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| destination | string | Yes | Destination city or country |
| start_date | date | Yes | Travel start date (YYYY-MM-DD) |
| end_date | date | Yes | Travel end date (YYYY-MM-DD) |
| budget | float | Yes | Total budget in USD (must be > 0) |
| travelers | integer | Yes | Number of travelers (1-10) |
| travel_class | enum | No | Flight class: economy, premium_economy, business, first |
| hotel_category | enum | No | Hotel category: budget, standard, luxury, resort |
| preferences | object | No | Additional preferences |

#### Response

```json
{
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "request": {
        "destination": "Paris, France",
        "start_date": "2024-06-15",
        "end_date": "2024-06-22",
        "budget": 2000.0,
        "travelers": 2,
        "travel_class": "economy",
        "hotel_category": "standard",
        "preferences": {
            "near_attractions": true,
            "airport_transfer": true,
            "breakfast_included": false
        }
    },
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
}
```

### Get Travel Plan

**GET** `/travel/plan/{plan_id}`

Retrieves a specific travel plan by ID.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| plan_id | string | Yes | Travel plan UUID |

#### Response

Returns the same structure as the create travel plan response.

### List Travel Plans

**GET** `/travel/plans`

Lists travel plans with pagination.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of plans to skip |
| limit | integer | No | 10 | Maximum number of plans to return |

#### Response

```json
{
    "plans": [
        {
            "plan_id": "550e8400-e29b-41d4-a716-446655440000",
            "destination": "Paris, France",
            "total_cost": 1850.0,
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
}
```

### Delete Travel Plan

**DELETE** `/travel/plan/{plan_id}`

Deletes a travel plan.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| plan_id | string | Yes | Travel plan UUID |

#### Response

```json
{
    "message": "Travel plan 550e8400-e29b-41d4-a716-446655440000 deleted successfully"
}
```

### Refresh Travel Plan

**POST** `/travel/plan/{plan_id}/refresh`

Refreshes a travel plan with updated prices and availability.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| plan_id | string | Yes | Travel plan UUID |

#### Response

```json
{
    "message": "Travel plan 550e8400-e29b-41d4-a716-446655440000 refresh initiated"
}
```

## Booking Endpoints

### Create Booking

**POST** `/booking/book`

Creates a booking for selected flight and hotel options.

#### Request Body

```json
{
    "plan_id": "550e8400-e29b-41d4-a716-446655440000",
    "selected_flight_id": "flight_1",
    "selected_hotel_id": "hotel_1",
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
```

#### Request Parameters

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| plan_id | string | Yes | Travel plan ID |
| selected_flight_id | string | Yes | Selected flight option ID |
| selected_hotel_id | string | Yes | Selected hotel option ID |
| traveler_details | object | Yes | Traveler information |
| payment_details | object | No | Payment information |

#### Response

```json
{
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
```

### Get Booking

**GET** `/booking/booking/{booking_id}`

Retrieves booking details by ID.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| booking_id | string | Yes | Booking UUID |

#### Response

Returns the same structure as the create booking response.

### List Bookings

**GET** `/booking/bookings`

Lists bookings with pagination.

#### Query Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| skip | integer | No | 0 | Number of bookings to skip |
| limit | integer | No | 10 | Maximum number of bookings to return |

#### Response

```json
{
    "bookings": [
        {
            "booking_id": "booking_550e8400-e29b-41d4-a716-446655440000",
            "plan_id": "550e8400-e29b-41d4-a716-446655440000",
            "total_cost": 1850.0,
            "status": "confirmed",
            "created_at": "2024-01-01T00:00:00Z"
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
}
```

### Cancel Booking

**POST** `/booking/booking/{booking_id}/cancel`

Cancels an existing booking.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| booking_id | string | Yes | Booking UUID |

#### Response

```json
{
    "message": "Booking booking_550e8400-e29b-41d4-a716-446655440000 cancellation initiated"
}
```

### Modify Booking

**POST** `/booking/booking/{booking_id}/modify`

Modifies an existing booking.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| booking_id | string | Yes | Booking UUID |

#### Request Body

```json
{
    "traveler_details": {
        "special_requests": "Late check-in requested",
        "dietary_requirements": "Vegetarian meals"
    }
}
```

#### Response

```json
{
    "message": "Booking booking_550e8400-e29b-41d4-a716-446655440000 modification initiated"
}
```

## Status Tracking Endpoints

### Get Booking Status

**GET** `/status/booking/{booking_id}`

Gets the current status of a booking.

#### Path Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| booking_id | string | Yes | Booking UUID |

#### Response

```json
{
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
```

### Health Check

**GET** `/status/health`

Checks the health of the service.

#### Response

```json
{
    "status": "healthy",
    "timestamp": "2024-01-01T00:00:00Z",
    "version": "1.0.0"
}
```

### Service Metrics

**GET** `/status/metrics`

Gets service metrics and statistics.

#### Response

```json
{
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
            "response_time_ms": 10
        },
        "external_apis": {
            "amadeus": {
                "status": "healthy",
                "response_time_ms": 150
            },
            "booking_com": {
                "status": "healthy",
                "response_time_ms": 200
            }
        },
        "overall_status": "healthy"
    }
}
```

## Data Types

### Enums

#### TravelClass
- `economy`
- `premium_economy`
- `business`
- `first`

#### HotelCategory
- `budget`
- `standard`
- `luxury`
- `resort`

#### BookingStatus
- `pending`
- `confirmed`
- `paid`
- `cancelled`
- `completed`

### Date Formats

All dates are in ISO 8601 format: `YYYY-MM-DD` or `YYYY-MM-DDTHH:MM:SSZ`

### Currency

All monetary values are in USD and represented as floating-point numbers.

## Rate Limiting

The API implements rate limiting to prevent abuse:

- **Travel Planning**: 10 requests per minute per IP
- **Booking**: 5 requests per minute per IP
- **Status Checks**: 30 requests per minute per IP

Rate limit headers are included in responses:
- `X-RateLimit-Limit`: Maximum requests allowed
- `X-RateLimit-Remaining`: Remaining requests in current window
- `X-RateLimit-Reset`: Time when the rate limit resets

## Webhooks

The API supports webhooks for booking status updates:

### Webhook Events

- `booking.confirmed`
- `booking.cancelled`
- `booking.modified`
- `payment.processed`
- `payment.failed`

### Webhook Payload

```json
{
    "event": "booking.confirmed",
    "booking_id": "booking_550e8400-e29b-41d4-a716-446655440000",
    "timestamp": "2024-01-01T00:00:00Z",
    "data": {
        "status": "confirmed",
        "total_cost": 1850.0,
        "confirmation_numbers": {
            "flight": "ABC20240101000000",
            "hotel": "HTL20240101000000"
        }
    }
}
```

## SDKs and Libraries

### Python SDK

```python
from travel_planner_sdk import TravelPlannerClient

client = TravelPlannerClient(api_key="your_api_key")

# Create travel plan
plan = client.create_travel_plan({
    "destination": "Paris, France",
    "start_date": "2024-06-15",
    "end_date": "2024-06-22",
    "budget": 2000.0,
    "travelers": 2
})

# Create booking
booking = client.create_booking({
    "plan_id": plan.plan_id,
    "selected_flight_id": "flight_1",
    "selected_hotel_id": "hotel_1",
    "traveler_details": {...}
})
```

### JavaScript SDK

```javascript
import { TravelPlannerClient } from 'travel-planner-sdk';

const client = new TravelPlannerClient('your_api_key');

// Create travel plan
const plan = await client.createTravelPlan({
    destination: 'Paris, France',
    startDate: '2024-06-15',
    endDate: '2024-06-22',
    budget: 2000.0,
    travelers: 2
});

// Create booking
const booking = await client.createBooking({
    planId: plan.planId,
    selectedFlightId: 'flight_1',
    selectedHotelId: 'hotel_1',
    travelerDetails: {...}
});
```

## Testing

### Test Environment

Use the test environment for development and testing:
- Base URL: `https://test-api.travelplanner.com/api/v1`
- Test API keys are provided for development
- Mock data is used for external API calls

### Postman Collection

A Postman collection is available for testing all endpoints:
- Import the collection from the repository
- Set environment variables for API keys
- Run individual requests or the full test suite

## Support

For API support and questions:
- Documentation: [https://docs.travelplanner.com](https://docs.travelplanner.com)
- Email: api-support@travelplanner.com
- GitHub Issues: [https://github.com/travelplanner/api-issues](https://github.com/travelplanner/api-issues)
