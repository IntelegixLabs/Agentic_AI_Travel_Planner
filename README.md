# AI Travel Planner MCP Server

An intelligent travel planning system built with FastAPI and CrewAI that provides comprehensive travel recommendations and booking capabilities. The system integrates with multiple external APIs to search for flights and hotels, optimizes options within user budgets, and handles the complete booking process.

## 🚀 Features

- **AI-Powered Travel Planning**: Uses CrewAI agents for intelligent travel recommendations
- **Multi-Provider Integration**: Searches flights and hotels across multiple platforms
- **Budget Optimization**: Automatically optimizes travel options within user budget constraints
- **Real-time Booking**: Handles flight and hotel bookings with confirmation tracking
- **Status Tracking**: Provides real-time booking status and next steps
- **RESTful API**: Clean, well-documented API with automatic OpenAPI documentation
- **Async Processing**: High-performance async operations for better scalability
- **Comprehensive Testing**: Full test suite with unit and integration tests

## 🏗️ Architecture

The system follows a modular architecture with clear separation of concerns:

- **FastAPI MCP Server**: Main application server with REST endpoints
- **CrewAI Agents**: Specialized AI agents for different aspects of travel planning
- **External API Clients**: Integration with flight and hotel booking platforms
- **Database Layer**: SQLite database for data persistence
- **Service Layer**: Business logic and orchestration

For detailed architecture information, see [ARCHITECTURE.md](ARCHITECTURE.md).

## 📋 Prerequisites

- Python 3.8+
- pip or poetry for dependency management
- SQLite (included with Python)
- OpenAI API key (for CrewAI agents)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-username/ai-travel-planner.git
   cd ai-travel-planner
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   uv pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your API keys and configuration
   ```

5. **Initialize database**
   ```bash
   python -m app.core.database
   ```

## 🚀 Quick Start

1. **Start the server**
   ```bash
   python -m app.main
   ```

2. **Access the API documentation**
   - OpenAPI docs: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

3. **Create your first travel plan**
   ```bash
   curl -X POST "http://localhost:8000/api/v1/travel/plan" \
        -H "Content-Type: application/json" \
        -d '{
          "destination": "Paris, France",
          "start_date": "2024-06-15",
          "end_date": "2024-06-22",
          "budget": 2000.0,
          "travelers": 2,
          "travel_class": "economy",
          "hotel_category": "standard"
        }'
   ```

## 📚 API Documentation

The API provides comprehensive endpoints for travel planning and booking:

### Travel Planning
- `POST /api/v1/travel/plan` - Create travel plan
- `GET /api/v1/travel/plan/{plan_id}` - Get travel plan
- `GET /api/v1/travel/plans` - List travel plans
- `DELETE /api/v1/travel/plan/{plan_id}` - Delete travel plan
- `POST /api/v1/travel/plan/{plan_id}/refresh` - Refresh plan

### Booking
- `POST /api/v1/booking/book` - Create booking
- `GET /api/v1/booking/booking/{booking_id}` - Get booking
- `GET /api/v1/booking/bookings` - List bookings
- `POST /api/v1/booking/booking/{booking_id}/cancel` - Cancel booking
- `POST /api/v1/booking/booking/{booking_id}/modify` - Modify booking

### Status Tracking
- `GET /api/v1/status/booking/{booking_id}` - Get booking status
- `GET /api/v1/status/health` - Health check
- `GET /api/v1/status/metrics` - Service metrics

For detailed API documentation, see [API_DOCUMENTATION.md](API_DOCUMENTATION.md).

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test categories
pytest -m unit          # Unit tests only
pytest -m integration   # Integration tests only
pytest -m "not slow"    # Skip slow tests
```

## 🔧 Configuration

The application can be configured through environment variables:

```bash
# API Keys
RAPIDAPI_KEY=your_rapidapi_key
OPENAI_API_KEY=your_openai_api_key

# Database
DATABASE_URL=sqlite:///./travel_planner.db

# Server Configuration
HOST=0.0.0.0
PORT=8000
DEBUG=True
LOG_LEVEL=INFO
```

### Getting RapidAPI Key

1. **Sign up for RapidAPI**: Visit [RapidAPI](https://rapidapi.com) and create an account
2. **Subscribe to Travel APIs**: Subscribe to these APIs:
   - [Skyscanner Flight Search](https://rapidapi.com/skyscanner/api/skyscanner-flight-search)
   - [Booking.com Hotels](https://rapidapi.com/booking-com/api/booking-com)
   - [Airbnb Search](https://rapidapi.com/airbnb13/api/airbnb13)
3. **Get your API Key**: Copy your RapidAPI key from the dashboard
4. **Set environment variable**: Add `RAPIDAPI_KEY=your_key_here` to your `.env` file

## 🤖 CrewAI Agents

The system uses specialized AI agents for different aspects of travel planning:

- **Travel Planner Agent**: Coordinates overall travel planning
- **Flight Agent**: Searches and books flights
- **Hotel Agent**: Searches and books hotels
- **Budget Agent**: Optimizes budget allocation

Each agent is configured with specific roles, goals, and backstories to provide expert-level recommendations.

## 🔌 External API Integration

The system integrates with multiple travel APIs through RapidAPI:

### Flight APIs
- **Skyscanner Flight Search**: Comprehensive flight search and comparison
- **Amadeus**: Alternative flight search (when available)

### Hotel APIs
- **Booking.com**: Global hotel inventory and booking
- **Airbnb**: Alternative accommodations and unique stays

### Benefits of RapidAPI Integration
- **Single API Key**: Access multiple travel APIs with one key
- **Unified Interface**: Consistent API structure across providers
- **Cost Effective**: Pay-per-use pricing for individual developers
- **Easy Setup**: No need for direct partnerships with travel companies
- **Reliable**: Managed infrastructure with high availability

## 📊 Monitoring and Logging

The application includes comprehensive monitoring and logging:

- **Structured Logging**: JSON-formatted logs with different levels
- **Health Checks**: Endpoint for service health monitoring
- **Metrics**: Detailed service metrics and statistics
- **Error Tracking**: Comprehensive error handling and reporting

## 🚀 Deployment

### Development
```bash
python -m app.main
```

### Production
```bash
# Using Gunicorn
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker

# Using Docker
docker build -t ai-travel-planner .
docker run -p 8000:8000 ai-travel-planner
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["python", "-m", "app.main"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- **Issues**: [GitHub Issues](https://github.com/your-username/ai-travel-planner/issues)
- **Email**: support@travelplanner.com

## 🗺️ Roadmap

- [ ] Payment gateway integration
- [ ] Mobile app SDK
- [ ] Advanced personalization
- [ ] Real-time price alerts
- [ ] Social travel features
- [ ] Car rental integration
- [ ] Travel insurance
- [ ] Local activity booking

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [CrewAI](https://www.crewai.com/) for AI agent orchestration
- [Pydantic](https://pydantic-docs.helpmanual.io/) for data validation
- [SQLAlchemy](https://www.sqlalchemy.org/) for database ORM
- [Pytest](https://pytest.org/) for testing framework