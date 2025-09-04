"""
Test cases for travel planning endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime, timedelta
import json

from app.main import app
from app.schemas.travel import TravelPlanRequest, TravelClass, HotelCategory

client = TestClient(app)


class TestTravelEndpoints:
    """Test cases for travel planning endpoints"""
    
    def test_create_travel_plan_success(self):
        """Test successful travel plan creation"""
        request_data = {
            "destination": "Paris, France",
            "start_date": "2024-06-15",
            "end_date": "2024-06-22",
            "budget": 2000.0,
            "travelers": 2,
            "travel_class": "economy",
            "hotel_category": "standard",
            "preferences": {
                "near_attractions": True,
                "airport_transfer": True
            }
        }
        
        response = client.post("/api/v1/travel/plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "plan_id" in data
        assert "request" in data
        assert "total_cost" in data
        assert "budget_utilization" in data
        assert "flight_options" in data
        assert "hotel_options" in data
        assert "recommendations" in data
        assert "created_at" in data
        assert "expires_at" in data
        
        # Verify request data matches
        assert data["request"]["destination"] == request_data["destination"]
        assert data["request"]["budget"] == request_data["budget"]
        assert data["request"]["travelers"] == request_data["travelers"]
        
        # Verify flight and hotel options are present
        assert len(data["flight_options"]) > 0
        assert len(data["hotel_options"]) > 0
        
        # Verify budget utilization is reasonable
        assert 0 <= data["budget_utilization"] <= 100
    
    def test_create_travel_plan_invalid_dates(self):
        """Test travel plan creation with invalid dates"""
        request_data = {
            "destination": "Paris, France",
            "start_date": "2024-06-22",  # End date before start date
            "end_date": "2024-06-15",
            "budget": 2000.0,
            "travelers": 2
        }
        
        response = client.post("/api/v1/travel/plan", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_travel_plan_invalid_budget(self):
        """Test travel plan creation with invalid budget"""
        request_data = {
            "destination": "Paris, France",
            "start_date": "2024-06-15",
            "end_date": "2024-06-22",
            "budget": -100.0,  # Negative budget
            "travelers": 2
        }
        
        response = client.post("/api/v1/travel/plan", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_create_travel_plan_missing_required_fields(self):
        """Test travel plan creation with missing required fields"""
        request_data = {
            "destination": "Paris, France",
            # Missing start_date, end_date, budget
            "travelers": 2
        }
        
        response = client.post("/api/v1/travel/plan", json=request_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_travel_plan_success(self):
        """Test successful travel plan retrieval"""
        # First create a plan
        request_data = {
            "destination": "Tokyo, Japan",
            "start_date": "2024-07-01",
            "end_date": "2024-07-08",
            "budget": 3000.0,
            "travelers": 1
        }
        
        create_response = client.post("/api/v1/travel/plan", json=request_data)
        assert create_response.status_code == 200
        
        plan_id = create_response.json()["plan_id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/travel/plan/{plan_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["plan_id"] == plan_id
        assert data["request"]["destination"] == request_data["destination"]
    
    def test_get_travel_plan_not_found(self):
        """Test travel plan retrieval with non-existent ID"""
        fake_plan_id = "550e8400-e29b-41d4-a716-446655440000"
        
        response = client.get(f"/api/v1/travel/plan/{fake_plan_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_travel_plans_success(self):
        """Test successful travel plans listing"""
        response = client.get("/api/v1/travel/plans")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "plans" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert isinstance(data["plans"], list)
        assert isinstance(data["total"], int)
    
    def test_list_travel_plans_with_pagination(self):
        """Test travel plans listing with pagination"""
        response = client.get("/api/v1/travel/plans?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["skip"] == 0
        assert data["limit"] == 5
        assert len(data["plans"]) <= 5
    
    def test_delete_travel_plan_success(self):
        """Test successful travel plan deletion"""
        # First create a plan
        request_data = {
            "destination": "London, UK",
            "start_date": "2024-08-01",
            "end_date": "2024-08-05",
            "budget": 1500.0,
            "travelers": 1
        }
        
        create_response = client.post("/api/v1/travel/plan", json=request_data)
        assert create_response.status_code == 200
        
        plan_id = create_response.json()["plan_id"]
        
        # Then delete it
        response = client.delete(f"/api/v1/travel/plan/{plan_id}")
        
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]
        
        # Verify it's deleted
        get_response = client.get(f"/api/v1/travel/plan/{plan_id}")
        assert get_response.status_code == 404
    
    def test_delete_travel_plan_not_found(self):
        """Test travel plan deletion with non-existent ID"""
        fake_plan_id = "550e8400-e29b-41d4-a716-446655440000"
        
        response = client.delete(f"/api/v1/travel/plan/{fake_plan_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_refresh_travel_plan_success(self):
        """Test successful travel plan refresh"""
        # First create a plan
        request_data = {
            "destination": "Barcelona, Spain",
            "start_date": "2024-09-01",
            "end_date": "2024-09-07",
            "budget": 1800.0,
            "travelers": 2
        }
        
        create_response = client.post("/api/v1/travel/plan", json=request_data)
        assert create_response.status_code == 200
        
        plan_id = create_response.json()["plan_id"]
        
        # Then refresh it
        response = client.post(f"/api/v1/travel/plan/{plan_id}/refresh")
        
        assert response.status_code == 200
        assert "refresh initiated" in response.json()["message"]
    
    def test_refresh_travel_plan_not_found(self):
        """Test travel plan refresh with non-existent ID"""
        fake_plan_id = "550e8400-e29b-41d4-a716-446655440000"
        
        response = client.post(f"/api/v1/travel/plan/{fake_plan_id}/refresh")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_travel_plan_with_different_travel_classes(self):
        """Test travel plan creation with different travel classes"""
        travel_classes = ["economy", "premium_economy", "business", "first"]
        
        for travel_class in travel_classes:
            request_data = {
                "destination": "Dubai, UAE",
                "start_date": "2024-10-01",
                "end_date": "2024-10-05",
                "budget": 5000.0,
                "travelers": 1,
                "travel_class": travel_class
            }
            
            response = client.post("/api/v1/travel/plan", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["request"]["travel_class"] == travel_class
    
    def test_travel_plan_with_different_hotel_categories(self):
        """Test travel plan creation with different hotel categories"""
        hotel_categories = ["budget", "standard", "luxury", "resort"]
        
        for hotel_category in hotel_categories:
            request_data = {
                "destination": "Rome, Italy",
                "start_date": "2024-11-01",
                "end_date": "2024-11-05",
                "budget": 2500.0,
                "travelers": 1,
                "hotel_category": hotel_category
            }
            
            response = client.post("/api/v1/travel/plan", json=request_data)
            
            assert response.status_code == 200
            data = response.json()
            assert data["request"]["hotel_category"] == hotel_category
    
    def test_travel_plan_with_multiple_travelers(self):
        """Test travel plan creation with multiple travelers"""
        request_data = {
            "destination": "Sydney, Australia",
            "start_date": "2024-12-01",
            "end_date": "2024-12-10",
            "budget": 8000.0,
            "travelers": 4  # Family trip
        }
        
        response = client.post("/api/v1/travel/plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["request"]["travelers"] == 4
        
        # Verify that prices are calculated for multiple travelers
        for flight in data["flight_options"]:
            assert flight["price"] > 0  # Should be calculated for 4 travelers
    
    def test_travel_plan_edge_case_budget(self):
        """Test travel plan creation with edge case budget values"""
        # Very low budget
        request_data = {
            "destination": "Prague, Czech Republic",
            "start_date": "2024-05-01",
            "end_date": "2024-05-03",
            "budget": 500.0,  # Very low budget
            "travelers": 1
        }
        
        response = client.post("/api/v1/travel/plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should still return options, even if budget utilization is high
        assert data["budget_utilization"] >= 0
    
    def test_travel_plan_long_duration(self):
        """Test travel plan creation for long duration trips"""
        request_data = {
            "destination": "Bangkok, Thailand",
            "start_date": "2024-06-01",
            "end_date": "2024-06-30",  # 30-day trip
            "budget": 10000.0,
            "travelers": 2
        }
        
        response = client.post("/api/v1/travel/plan", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should handle long duration trips
        assert len(data["hotel_options"]) > 0
        # Hotel prices should be calculated for the full duration
        for hotel in data["hotel_options"]:
            assert hotel["total_price"] > hotel["price_per_night"]
