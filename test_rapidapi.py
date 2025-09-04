#!/usr/bin/env python3
"""
Test script for RapidAPI integration
"""

import asyncio
import os
from datetime import date, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from app.services.rapidapi_client import RapidAPIClient


async def test_rapidapi_integration():
    """Test RapidAPI integration"""
    print("🚀 Testing RapidAPI Integration...")
    
    # Check if API key is set
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("❌ RAPIDAPI_KEY not found in environment variables")
        print("Please set RAPIDAPI_KEY in your .env file")
        return False
    
    print(f"✅ RapidAPI Key found: {api_key[:10]}...")
    
    # Initialize client
    client = RapidAPIClient()
    
    try:
        # Test health check
        print("\n🔍 Testing health check...")
        health = await client.health_check()
        if health:
            print("✅ RapidAPI health check passed")
        else:
            print("❌ RapidAPI health check failed")
            return False
        
        # Test flight search
        print("\n✈️ Testing flight search...")
        departure_date = date.today() + timedelta(days=30)
        return_date = departure_date + timedelta(days=7)
        
        flights = await client.search_flights(
            origin="NYC",
            destination="LAX",
            departure_date=departure_date,
            return_date=return_date,
            travelers=1,
            travel_class="economy"
        )
        
        print(f"✅ Found {len(flights)} flight options")
        for i, flight in enumerate(flights[:3]):  # Show first 3
            print(f"  {i+1}. {flight['airline']} - ${flight['price']} - {flight['duration']}")
        
        # Test hotel search
        print("\n🏨 Testing hotel search...")
        check_in = date.today() + timedelta(days=30)
        check_out = check_in + timedelta(days=3)
        
        hotels = await client.search_hotels(
            destination="New York",
            check_in=check_in,
            check_out=check_out,
            travelers=1,
            hotel_category="standard"
        )
        
        print(f"✅ Found {len(hotels)} hotel options")
        for i, hotel in enumerate(hotels[:3]):  # Show first 3
            print(f"  {i+1}. {hotel['name']} - ${hotel['price_per_night']}/night - Rating: {hotel['rating']}")
        
        # Test Airbnb search
        print("\n🏠 Testing Airbnb search...")
        airbnb = await client.search_airbnb(
            destination="New York",
            check_in=check_in,
            check_out=check_out,
            travelers=1
        )
        
        print(f"✅ Found {len(airbnb)} Airbnb options")
        for i, listing in enumerate(airbnb[:3]):  # Show first 3
            print(f"  {i+1}. {listing['name']} - ${listing['price_per_night']}/night - Rating: {listing['rating']}")
        
        print("\n🎉 All tests passed! RapidAPI integration is working correctly.")
        return True
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        return False
    
    finally:
        await client.close()


async def main():
    """Main test function"""
    print("=" * 60)
    print("AI Travel Planner - RapidAPI Integration Test")
    print("=" * 60)
    
    success = await test_rapidapi_integration()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Integration test completed successfully!")
        print("\nNext steps:")
        print("1. Start the server: python -m app.main")
        print("2. Test the API: curl http://localhost:8000/docs")
        print("3. Create a travel plan using the API")
    else:
        print("❌ Integration test failed!")
        print("\nTroubleshooting:")
        print("1. Check your RAPIDAPI_KEY in .env file")
        print("2. Verify you have subscribed to the required APIs")
        print("3. Check your internet connection")
        print("4. Review the RAPIDAPI_SETUP.md guide")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())
