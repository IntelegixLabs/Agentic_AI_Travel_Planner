# AI Travel Planner MCP Server - Architecture Documentation

## Overview

The AI Travel Planner MCP Server is a comprehensive travel planning system built with FastAPI and CrewAI that provides intelligent travel recommendations and booking capabilities. The system integrates with multiple external APIs to search for flights and hotels, optimizes options within user budgets, and handles the complete booking process.

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Client Applications                          │
│  (Web App, Mobile App, API Clients, MCP Clients)              │
└─────────────────────┬───────────────────────────────────────────┘
                      │ HTTP/HTTPS
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FastAPI MCP Server                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │   API Gateway   │  │  Authentication │  │   Rate Limiting │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Business Logic Layer                        │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Travel Service  │  │ Booking Service │  │ Status Service  │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    CrewAI Agents Layer                         │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Planner Agent   │  │ Flight Agent    │  │ Hotel Agent     │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Budget Agent    │  │ Coordination    │  │ Task Management │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External API Layer                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ Flight APIs     │  │ Hotel APIs      │  │ Payment APIs    │ │
│  │ • Amadeus       │  │ • Booking.com   │  │ • Stripe        │ │
│  │ • Skyscanner    │  │ • Expedia       │  │ • Razorpay      │ │
│  │ • Google Flights│  │ • Airbnb        │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────┬───────────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Data Layer                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐ │
│  │ SQLite Database │  │ Redis Cache     │  │ File Storage    │ │
│  │ • Travel Plans  │  │ • Session Data  │  │ • Logs          │ │
│  │ • Bookings      │  │ • API Responses │  │ • Configs       │ │
│  │ • Users         │  │ • Rate Limits   │  │                 │ │
│  └─────────────────┘  └─────────────────┘  └─────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. FastAPI MCP Server

**Location**: `app/main.py`

The main FastAPI application that serves as the MCP (Model Context Protocol) server entry point.

**Key Features**:
- RESTful API endpoints
- Automatic OpenAPI documentation
- CORS middleware for cross-origin requests
- Request/response validation with Pydantic
- Async/await support for high performance
- Health check endpoints

**Configuration**:
- Host: 0.0.0.0 (configurable)
- Port: 8000 (configurable)
- Debug mode support
- Logging configuration

### 2. CrewAI Agents

#### Planner Agent (`app/agents/planner_agent.py`)
- **Role**: Senior Travel Planning Coordinator
- **Responsibilities**:
  - Analyze user requirements
  - Coordinate with other agents
  - Create comprehensive travel plans
  - Provide destination-specific recommendations
  - Handle budget allocation

#### Flight Agent (`app/agents/flight_agent.py`)
- **Role**: Flight Search and Booking Specialist
- **Responsibilities**:
  - Search multiple flight providers
  - Compare flight options
  - Handle flight bookings
  - Provide flight-specific recommendations
  - Manage flight modifications

#### Hotel Agent (`app/agents/hotel_agent.py`)
- **Role**: Hotel Search and Booking Specialist
- **Responsibilities**:
  - Search multiple hotel providers
  - Compare accommodation options
  - Handle hotel bookings
  - Provide location-specific recommendations
  - Manage hotel modifications

#### Budget Agent (`app/agents/budget_agent.py`)
- **Role**: Travel Budget Optimization Specialist
- **Responsibilities**:
  - Optimize budget allocation
  - Analyze cost-effectiveness
  - Provide value recommendations
  - Handle budget constraints
  - Generate cost analysis

### 3. External API Clients

#### Flight APIs (`app/services/flight_clients.py`)

**Amadeus Client**:
- Official airline industry API
- Comprehensive flight search
- Real-time pricing
- Booking capabilities
- OAuth2 authentication

**Skyscanner Client**:
- Travel search engine API
- Price comparison
- Alternative routes
- Travel insights

#### Hotel APIs (`app/services/hotel_clients.py`)

**Booking.com Client**:
- Global hotel inventory
- Real-time availability
- Competitive pricing
- Guest reviews integration

**Expedia Client**:
- Hotel and package deals
- Loyalty program integration
- Group booking support

**Airbnb Client**:
- Alternative accommodations
- Unique stays
- Local experiences

### 4. Data Models

#### Pydantic Schemas (`app/schemas/travel.py`)

**TravelPlanRequest**:
```python
{
    "destination": "string",
    "start_date": "date",
    "end_date": "date",
    "budget": "float",
    "travelers": "integer",
    "travel_class": "enum",
    "hotel_category": "enum",
    "preferences": "object"
}
```

**TravelPlan**:
```python
{
    "plan_id": "string",
    "request": "TravelPlanRequest",
    "total_cost": "float",
    "budget_utilization": "float",
    "flight_options": "List[FlightOption]",
    "hotel_options": "List[HotelOption]",
    "recommendations": "List[string]",
    "created_at": "datetime",
    "expires_at": "datetime"
}
```

#### Database Models (`app/models/`)

**TravelPlan Model**:
- Stores travel plan details
- Flight and hotel options as JSON
- Budget and cost information
- Expiration tracking

**Booking Model**:
- Booking confirmations
- Traveler details
- Payment information
- Status tracking

**User Model**:
- User preferences
- Booking history
- Personalization data

### 5. API Endpoints

#### Travel Planning (`/api/v1/travel/`)

**POST /plan**
- Create comprehensive travel plan
- Input: TravelPlanRequest
- Output: TravelPlan
- Process: Multi-agent coordination

**GET /plan/{plan_id}**
- Retrieve specific travel plan
- Input: Plan ID
- Output: TravelPlan

**GET /plans**
- List travel plans with pagination
- Input: skip, limit parameters
- Output: Paginated list

**DELETE /plan/{plan_id}**
- Delete travel plan
- Input: Plan ID
- Output: Success message

**POST /plan/{plan_id}/refresh**
- Refresh plan with updated prices
- Input: Plan ID
- Output: Success message
- Process: Background task

#### Booking (`/api/v1/booking/`)

**POST /book**
- Create booking for selected options
- Input: BookingRequest
- Output: BookingConfirmation
- Process: Concurrent flight and hotel booking

**GET /booking/{booking_id}**
- Retrieve booking details
- Input: Booking ID
- Output: BookingConfirmation

**GET /bookings**
- List bookings with pagination
- Input: skip, limit parameters
- Output: Paginated list

**POST /booking/{booking_id}/cancel**
- Cancel existing booking
- Input: Booking ID
- Output: Success message
- Process: Background task

**POST /booking/{booking_id}/modify**
- Modify existing booking
- Input: Booking ID, modifications
- Output: Success message
- Process: Background task

#### Status Tracking (`/api/v1/status/`)

**GET /booking/{booking_id}**
- Get booking status
- Input: Booking ID
- Output: BookingStatus

**GET /health**
- Service health check
- Output: Health status

**GET /metrics**
- Service metrics and statistics
- Output: Performance metrics

## Data Flow

### 1. Travel Plan Creation Flow

```
User Request → API Gateway → Travel Service → Planner Agent
                    ↓
            Flight Agent ← → Hotel Agent
                    ↓
            Budget Agent → Optimization → Response
```

### 2. Booking Flow

```
Booking Request → Booking Service → Flight Agent
                        ↓
                Hotel Agent → Payment Processing
                        ↓
                Database Storage → Confirmation
```

### 3. Status Tracking Flow

```
Status Request → Status Service → Database Query
                        ↓
                Status Aggregation → Response
```

## Security Considerations

### 1. Authentication & Authorization
- API key management for external services
- User session management
- Role-based access control

### 2. Data Protection
- PII encryption
- Secure payment processing
- GDPR compliance

### 3. API Security
- Rate limiting
- Input validation
- SQL injection prevention
- CORS configuration

## Performance Optimization

### 1. Caching Strategy
- Redis for session data
- API response caching
- Database query optimization

### 2. Async Processing
- Background tasks for heavy operations
- Concurrent API calls
- Non-blocking I/O

### 3. Database Optimization
- Connection pooling
- Query optimization
- Indexing strategy

## Monitoring & Logging

### 1. Application Logging
- Structured logging with JSON format
- Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
- Request/response logging
- Agent action logging

### 2. Metrics Collection
- API response times
- Error rates
- Booking success rates
- Agent performance metrics

### 3. Health Monitoring
- Database connectivity
- External API health
- System resource usage
- Service availability

## Deployment Architecture

### 1. Development Environment
- Local SQLite database
- Mock external APIs
- Debug logging enabled
- Hot reload support

### 2. Production Environment
- PostgreSQL database
- Redis cache
- Load balancer
- Container orchestration
- Monitoring stack

### 3. Scaling Considerations
- Horizontal scaling with load balancers
- Database read replicas
- CDN for static assets
- Microservices architecture potential

## Error Handling

### 1. API Error Responses
- Standardized error format
- HTTP status codes
- Error categorization
- User-friendly messages

### 2. Agent Error Handling
- Graceful degradation
- Fallback mechanisms
- Retry logic
- Error recovery

### 3. External API Failures
- Circuit breaker pattern
- Timeout handling
- Fallback to alternative providers
- Error logging and alerting

## Future Enhancements

### 1. Advanced Features
- Machine learning for personalization
- Real-time price alerts
- Social travel features
- Mobile app integration

### 2. Integration Expansions
- Additional booking providers
- Car rental services
- Travel insurance
- Local activity booking

### 3. Performance Improvements
- GraphQL API
- WebSocket support
- Advanced caching
- Edge computing

This architecture provides a robust, scalable foundation for the AI Travel Planner MCP Server while maintaining flexibility for future enhancements and integrations.
