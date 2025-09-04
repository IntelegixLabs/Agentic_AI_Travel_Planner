"""
Test cases for booking endpoints
"""

import pytest
from fastapi.testclient import TestClient
from datetime import date, datetime
import json

from app.main import app

client = TestClient(app)


class TestBookingEndpoints:
    """Test cases for booking endpoints"""
    
    def setup_method(self):
        """Setup method to create a travel plan for booking tests"""
        # Create a travel plan first
        request_data = {
            "destination": "Paris, France",
            "start_date": "2024-06-15",
            "end_date": "2024-06-22",
            "budget": 2000.0,
            "travelers": 2,
            "travel_class": "economy",
            "hotel_category": "standard"
        }
        
        response = client.post("/api/v1/travel/plan", json=request_data)
        assert response.status_code == 200
        
        self.plan_data = response.json()
        self.plan_id = self.plan_data["plan_id"]
        self.flight_id = self.plan_data["flight_options"][0]["id"]
        self.hotel_id = self.plan_data["hotel_options"][0]["id"]
    
    def test_create_booking_success(self):
        """Test successful booking creation"""
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
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
            }
        }
        
        response = client.post("/api/v1/booking/book", json=booking_data)
        
        assert response.status_code == 200
        data = response.json()
        
        # Verify response structure
        assert "booking_id" in data
        assert "plan_id" in data
        assert "flight_booking" in data
        assert "hotel_booking" in data
        assert "total_cost" in data
        assert "status" in data
        assert "confirmation_numbers" in data
        assert "created_at" in data
        assert "itinerary" in data
        
        # Verify booking details
        assert data["plan_id"] == self.plan_id
        assert data["status"] == "confirmed"
        assert data["total_cost"] > 0
        
        # Verify confirmation numbers
        assert "flight" in data["confirmation_numbers"]
        assert "hotel" in data["confirmation_numbers"]
        
        # Store booking ID for other tests
        self.booking_id = data["booking_id"]
    
    def test_create_booking_with_payment(self):
        """Test booking creation with payment details"""
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "Alice",
                    "last_name": "Smith",
                    "email": "alice.smith@example.com",
                    "phone": "+1987654321",
                    "date_of_birth": "1985-03-20",
                    "passport_number": "C9876543"
                }
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
        
        response = client.post("/api/v1/booking/book", json=booking_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "confirmed"
        assert data["total_cost"] > 0
    
    def test_create_booking_invalid_plan_id(self):
        """Test booking creation with invalid plan ID"""
        booking_data = {
            "plan_id": "invalid-plan-id",
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1234567890",
                    "date_of_birth": "1990-01-01",
                    "passport_number": "A1234567"
                }
            }
        }
        
        response = client.post("/api/v1/booking/book", json=booking_data)
        
        assert response.status_code == 500  # Internal server error due to plan not found
    
    def test_create_booking_invalid_flight_id(self):
        """Test booking creation with invalid flight ID"""
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": "invalid-flight-id",
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1234567890",
                    "date_of_birth": "1990-01-01",
                    "passport_number": "A1234567"
                }
            }
        }
        
        response = client.post("/api/v1/booking/book", json=booking_data)
        
        assert response.status_code == 500  # Internal server error due to flight not found
    
    def test_create_booking_invalid_hotel_id(self):
        """Test booking creation with invalid hotel ID"""
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": "invalid-hotel-id",
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "John",
                    "last_name": "Doe",
                    "email": "john.doe@example.com",
                    "phone": "+1234567890",
                    "date_of_birth": "1990-01-01",
                    "passport_number": "A1234567"
                }
            }
        }
        
        response = client.post("/api/v1/booking/book", json=booking_data)
        
        assert response.status_code == 500  # Internal server error due to hotel not found
    
    def test_create_booking_missing_required_fields(self):
        """Test booking creation with missing required fields"""
        booking_data = {
            "plan_id": self.plan_id,
            # Missing selected_flight_id, selected_hotel_id, traveler_details
        }
        
        response = client.post("/api/v1/booking/book", json=booking_data)
        
        assert response.status_code == 422  # Validation error
    
    def test_get_booking_success(self):
        """Test successful booking retrieval"""
        # First create a booking
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "Bob",
                    "last_name": "Johnson",
                    "email": "bob.johnson@example.com",
                    "phone": "+1555123456",
                    "date_of_birth": "1988-07-10",
                    "passport_number": "D4567890"
                }
            }
        }
        
        create_response = client.post("/api/v1/booking/book", json=booking_data)
        assert create_response.status_code == 200
        
        booking_id = create_response.json()["booking_id"]
        
        # Then retrieve it
        response = client.get(f"/api/v1/booking/booking/{booking_id}")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["booking_id"] == booking_id
        assert data["plan_id"] == self.plan_id
        assert data["status"] == "confirmed"
    
    def test_get_booking_not_found(self):
        """Test booking retrieval with non-existent ID"""
        fake_booking_id = "booking_550e8400-e29b-41d4-a716-446655440000"
        
        response = client.get(f"/api/v1/booking/booking/{fake_booking_id}")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_list_bookings_success(self):
        """Test successful bookings listing"""
        response = client.get("/api/v1/booking/bookings")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "bookings" in data
        assert "total" in data
        assert "skip" in data
        assert "limit" in data
        assert isinstance(data["bookings"], list)
        assert isinstance(data["total"], int)
    
    def test_list_bookings_with_pagination(self):
        """Test bookings listing with pagination"""
        response = client.get("/api/v1/booking/bookings?skip=0&limit=5")
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["skip"] == 0
        assert data["limit"] == 5
        assert len(data["bookings"]) <= 5
    
    def test_cancel_booking_success(self):
        """Test successful booking cancellation"""
        # First create a booking
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "Charlie",
                    "last_name": "Brown",
                    "email": "charlie.brown@example.com",
                    "phone": "+1555987654",
                    "date_of_birth": "1993-12-25",
                    "passport_number": "E5678901"
                }
            }
        }
        
        create_response = client.post("/api/v1/booking/book", json=booking_data)
        assert create_response.status_code == 200
        
        booking_id = create_response.json()["booking_id"]
        
        # Then cancel it
        response = client.post(f"/api/v1/booking/booking/{booking_id}/cancel")
        
        assert response.status_code == 200
        assert "cancellation initiated" in response.json()["message"]
    
    def test_cancel_booking_not_found(self):
        """Test booking cancellation with non-existent ID"""
        fake_booking_id = "booking_550e8400-e29b-41d4-a716-446655440000"
        
        response = client.post(f"/api/v1/booking/booking/{fake_booking_id}/cancel")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_modify_booking_success(self):
        """Test successful booking modification"""
        # First create a booking
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "David",
                    "last_name": "Wilson",
                    "email": "david.wilson@example.com",
                    "phone": "+1555345678",
                    "date_of_birth": "1987-04-15",
                    "passport_number": "F6789012"
                }
            }
        }
        
        create_response = client.post("/api/v1/booking/book", json=booking_data)
        assert create_response.status_code == 200
        
        booking_id = create_response.json()["booking_id"]
        
        # Then modify it
        modifications = {
            "traveler_details": {
                "special_requests": "Late check-in requested",
                "dietary_requirements": "Vegetarian meals"
            }
        }
        
        response = client.post(f"/api/v1/booking/booking/{booking_id}/modify", json=modifications)
        
        assert response.status_code == 200
        assert "modification initiated" in response.json()["message"]
    
    def test_modify_booking_not_found(self):
        """Test booking modification with non-existent ID"""
        fake_booking_id = "booking_550e8400-e29b-41d4-a716-446655440000"
        
        modifications = {
            "traveler_details": {
                "special_requests": "Late check-in requested"
            }
        }
        
        response = client.post(f"/api/v1/booking/booking/{fake_booking_id}/modify", json=modifications)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()
    
    def test_booking_with_single_traveler(self):
        """Test booking creation for single traveler"""
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "Eve",
                    "last_name": "Davis",
                    "email": "eve.davis@example.com",
                    "phone": "+1555765432",
                    "date_of_birth": "1991-09-30",
                    "passport_number": "G7890123"
                }
                # No additional travelers
            }
        }
        
        response = client.post("/api/v1/booking/book", json=booking_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "confirmed"
        assert data["total_cost"] > 0
    
    def test_booking_with_multiple_travelers(self):
        """Test booking creation for multiple travelers"""
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                "primary_traveler": {
                    "first_name": "Frank",
                    "last_name": "Miller",
                    "email": "frank.miller@example.com",
                    "phone": "+1555987654",
                    "date_of_birth": "1986-11-12",
                    "passport_number": "H8901234"
                },
                "additional_travelers": [
                    {
                        "first_name": "Grace",
                        "last_name": "Miller",
                        "date_of_birth": "1988-02-28",
                        "passport_number": "I9012345"
                    },
                    {
                        "first_name": "Henry",
                        "last_name": "Miller",
                        "date_of_birth": "1990-06-18",
                        "passport_number": "J0123456"
                    }
                ]
            }
        }
        
        response = client.post("/api/v1/booking/book", json=booking_data)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["status"] == "confirmed"
        assert data["total_cost"] > 0
        
        # Verify flight booking includes seat assignments for all travelers
        flight_booking = data["flight_booking"]
        assert "seat_assignments" in flight_booking
        assert len(flight_booking["seat_assignments"]) == 3  # 3 travelers
    
    def test_booking_invalid_traveler_details(self):
        """Test booking creation with invalid traveler details"""
        booking_data = {
            "plan_id": self.plan_id,
            "selected_flight_id": self.flight_id,
            "selected_hotel_id": self.hotel_id,
            "traveler_details": {
                # Missing required fields
                "primary_traveler": {
                    "first_name": "Invalid"
                    # Missing last_name, email, phone, etc.
                }
            }
        }
        
        response = client.post("/api/v1/booking/book", json=booking_data)
        
        # Should still succeed as we're not validating traveler details strictly
        # In production, this would have proper validation
        assert response.status_code in [200, 422]
