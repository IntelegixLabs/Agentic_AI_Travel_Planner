"""
Test cases for status tracking endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import json

from app.main import app

client = TestClient(app)


class TestStatusEndpoints:
    """Test cases for status tracking endpoints"""
    
    def setup_method(self):
        """Setup method to create a booking for status tests"""
        # Create a travel plan first
        plan_data = {
            "destination": "Tokyo, Japan",
            "start_date": "2024-07-01",
            "end_date": "2024-07-08",
            "budget": 3000.0,
            "travelers": 1
        }
        
        plan_response = client.post("/api/v1/travel/plan", json=plan_data)
        assert plan_response.status_code == 200
        
        self.plan_data = plan_response.json()
        self.plan_id = self.plan_data["plan_id"]
        self.flight_id = self.plan_data["flight_options"][0]["id"]
        self.hotel_id = self.plan_data["hotel_options"][0]["id"]
        
        # Create a booking
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "Test",
                    "last_name": "User",
                    "email": "test.user@example.com",
                    "phone": "+1234567890",
                    "date_of_birth": "1990-01-01",
                    "passport_number": "A1234567"
                }
            }
        }
        
        booking_response = client.post("/api/v1/booking/book", json=booking_data)
        assert booking_response.status_code == 200
        
        self.booking_data = booking_response.json()
        self.booking_id = self.booking_data["booking_id"]
    
    def test_get_booking_status_success(self):
        """Test successful booking status retrieval"""
        response = client.get(f"/api/v1/status/booking/{self.booking_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "booking_id" in data
        assert "status" in data
        assert "last_updated" in data
        assert "details" in data
        assert "next_steps" in data
        
        # Verify booking details
        assert data["booking_id"] == self.booking_id
        assert data["status"] in ["pending", "confirmed", "paid", "cancelled", "completed"]
        
        # Verify details structure
        details = data["details"]
        assert "confirmation_numbers" in details
        assert "total_cost" in details
        assert "created_at" in details
        
        # Verify next steps
        assert isinstance(data["next_steps"], list)
        assert len(data["next_steps"]) > 0
    
    def test_get_booking_status_not_found(self):
        """Test booking status retrieval with non-existent ID"""
        fake_booking_id = "booking_550e8400-e29b-41d4-a716-446655440000"
        
        response = client.get(f"/api/v1/status/booking/{fake_booking_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_health_check_success(self):
        """Test successful health check"""
        response = client.get("/api/v1/status/health")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "status" in data
        assert "timestamp" in data
        assert "version" in data
        
        # Verify health status
        assert data["status"] == "healthy"
        assert data["version"] == "1.0.0"
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(data["timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Invalid timestamp format")
    
    def test_metrics_success(self):
        """Test successful metrics retrieval"""
        response = client.get("/api/v1/status/metrics")
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "timestamp" in data
        assert "bookings" in data
        assert "travel_plans" in data
        assert "system_health" in data
        
        # Verify bookings metrics
        bookings = data["bookings"]
        assert "total" in bookings
        assert "by_status" in bookings
        assert "recent_24h" in bookings
        assert "average_value" in bookings
        
        assert isinstance(bookings["total"], int)
        assert isinstance(bookings["by_status"], dict)
        assert isinstance(bookings["recent_24h"], int)
        assert isinstance(bookings["average_value"], (int, float))
        
        # Verify travel plans metrics
        travel_plans = data["travel_plans"]
        assert "total" in travel_plans
        assert "active" in travel_plans
        assert "top_destinations" in travel_plans
        
        assert isinstance(travel_plans["total"], int)
        assert isinstance(travel_plans["active"], int)
        assert isinstance(travel_plans["top_destinations"], dict)
        
        # Verify system health
        system_health = data["system_health"]
        assert "database" in system_health
        assert "external_apis" in system_health
        assert "overall_status" in system_health
        
        # Verify database health
        database = system_health["database"]
        assert "status" in database
        assert "response_time_ms" in database
        assert "last_check" in database
        
        assert database["status"] in ["healthy", "unhealthy"]
        assert isinstance(database["response_time_ms"], int)
        
        # Verify external APIs health
        external_apis = system_health["external_apis"]
        expected_apis = ["amadeus", "booking_com", "expedia", "skyscanner"]
        
        for api in expected_apis:
            assert api in external_apis
            api_health = external_apis[api]
            assert "status" in api_health
            assert "response_time_ms" in api_health
            assert api_health["status"] in ["healthy", "unhealthy"]
            assert isinstance(api_health["response_time_ms"], int)
        
        # Verify overall status
        assert system_health["overall_status"] in ["healthy", "degraded", "unhealthy"]
    
    def test_booking_status_different_states(self):
        """Test booking status for different booking states"""
        # Create multiple bookings to test different statuses
        bookings = []
        
        for i in range(3):
            booking_data = {
                "plan_id": self.plan_id,
                "selected_flight_id": self.flight_id,
                "selected_hotel_id": self.hotel_id,
                "traveler_details": {
                    "primary_traveler": {
                        "first_name": f"Test{i}",
                        "last_name": "User",
                        "email": f"test{i}.user@example.com",
                        "phone": f"+123456789{i}",
                        "date_of_birth": "1990-01-01",
                        "passport_number": f"A123456{i}"
                    }
                }
            }
            
            response = client.post("/api/v1/booking/book", json=booking_data)
            assert response.status_code == 200
            
            booking_id = response.json()["booking_id"]
            bookings.append(booking_id)
        
        # Test status for each booking
        for booking_id in bookings:
            response = client.get(f"/api/v1/status/booking/{booking_id}")
            assert response.status_code == 200
            
            data = response.json()
            assert data["booking_id"] == booking_id
            assert data["status"] in ["pending", "confirmed", "paid", "cancelled", "completed"]
    
    def test_metrics_with_data(self):
        """Test metrics with actual data"""
        # Create some test data
        for i in range(2):
            plan_data = {
                "destination": f"Test City {i}",
                "start_date": "2024-08-01",
                "end_date": "2024-08-05",
                "budget": 1500.0,
                "travelers": 1
            }
            
            plan_response = client.post("/api/v1/travel/plan", json=plan_data)
            assert plan_response.status_code == 200
            
            plan_id = plan_response.json()["plan_id"]
            flight_id = plan_response.json()["flight_options"][0]["id"]
            hotel_id = plan_response.json()["hotel_options"][0]["id"]
            
            booking_data = {
                "plan_id": plan_id,
                "selected_flight_id": flight_id,
                "selected_hotel_id": hotel_id,
                "traveler_details": {
                    "primary_traveler": {
                        "first_name": f"Metrics{i}",
                        "last_name": "Test",
                        "email": f"metrics{i}.test@example.com",
                        "phone": f"+155512345{i}",
                        "date_of_birth": "1990-01-01",
                        "passport_number": f"M123456{i}"
                    }
                }
            }
            
            booking_response = client.post("/api/v1/booking/book", json=booking_data)
            assert booking_response.status_code == 200
        
        # Get metrics
        response = client.get("/api/v1/status/metrics")
        assert response.status_code == 200
        
        data = response.json()
        
        # Verify that metrics reflect the created data
        assert data["bookings"]["total"] >= 3  # At least our test bookings
        assert data["travel_plans"]["total"] >= 3  # At least our test plans
        
        # Verify top destinations includes our test data
        top_destinations = data["travel_plans"]["top_destinations"]
        assert len(top_destinations) > 0
    
    def test_health_check_consistency(self):
        """Test health check consistency across multiple calls"""
        responses = []
        
        # Make multiple health check calls
        for _ in range(5):
            response = client.get("/api/v1/status/health")
            assert response.status_code == 200
            responses.append(response.json())
        
        # Verify all responses are consistent
        for response in responses:
            assert response["status"] == "healthy"
            assert response["version"] == "1.0.0"
    
    def test_metrics_consistency(self):
        """Test metrics consistency across multiple calls"""
        responses = []
        
        # Make multiple metrics calls
        for _ in range(3):
            response = client.get("/api/v1/status/metrics")
            assert response.status_code == 200
            responses.append(response.json())
        
        # Verify all responses have consistent structure
        for response in responses:
            assert "timestamp" in response
            assert "bookings" in response
            assert "travel_plans" in response
            assert "system_health" in response
            
            # Verify bookings structure
            bookings = response["bookings"]
            assert "total" in bookings
            assert "by_status" in bookings
            assert "recent_24h" in bookings
            assert "average_value" in bookings
            
            # Verify travel plans structure
            travel_plans = response["travel_plans"]
            assert "total" in travel_plans
            assert "active" in travel_plans
            assert "top_destinations" in travel_plans
            
            # Verify system health structure
            system_health = response["system_health"]
            assert "database" in system_health
            assert "external_apis" in system_health
            assert "overall_status" in system_health
    
    def test_booking_status_next_steps(self):
        """Test that booking status provides appropriate next steps"""
        response = client.get(f"/api/v1/status/booking/{self.booking_id}")
        assert response.status_code == 200
        
        data = response.json()
        status = data["status"]
        next_steps = data["next_steps"]
        
        # Verify that next steps are provided for any status
        assert isinstance(next_steps, list)
        assert len(next_steps) > 0
        
        # Verify that next steps are relevant to the status
        if status == "confirmed":
            assert any("check-in" in step.lower() for step in next_steps)
        elif status == "pending":
            assert any("payment" in step.lower() for step in next_steps)
        elif status == "cancelled":
            assert any("refund" in step.lower() for step in next_steps)
    
    def test_metrics_timestamp_format(self):
        """Test that metrics timestamp is in correct format"""
        response = client.get("/api/v1/status/metrics")
        assert response.status_code == 200
        
        data = response.json()
        timestamp = data["timestamp"]
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Invalid timestamp format in metrics")
    
    def test_health_check_timestamp_format(self):
        """Test that health check timestamp is in correct format"""
        response = client.get("/api/v1/status/health")
        assert response.status_code == 200
        
        data = response.json()
        timestamp = data["timestamp"]
        
        # Verify timestamp format
        try:
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            pytest.fail("Invalid timestamp format in health check")
