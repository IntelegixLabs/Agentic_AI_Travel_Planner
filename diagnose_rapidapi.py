#!/usr/bin/env python3
"""
Diagnostic script for RapidAPI issues
"""

import os
import asyncio
import httpx
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


async def diagnose_rapidapi():
    """Diagnose RapidAPI connection issues"""
    print("🔍 RapidAPI Diagnostic Tool")
    print("=" * 50)
    
    # Check environment variables
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("❌ RAPIDAPI_KEY not found in environment variables")
        print("\nTo fix this:")
        print("1. Create a .env file in your project root")
        print("2. Add: RAPIDAPI_KEY=your_rapidapi_key_here")
        print("3. Get your key from: https://rapidapi.com/developer/security")
        return False
    
    print(f"✅ RAPIDAPI_KEY found: {api_key[:10]}...")
    
    # Test basic connectivity
    print("\n🌐 Testing basic connectivity...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("https://rapidapi.com", timeout=10.0)
            if response.status_code == 200:
                print("✅ Can reach RapidAPI website")
            else:
                print(f"⚠️ RapidAPI website returned status {response.status_code}")
    except Exception as e:
        print(f"❌ Cannot reach RapidAPI website: {e}")
        print("Check your internet connection")
        return False
    
    # Test API endpoints
    print("\n🔌 Testing API endpoints...")
    
    # Test Skyscanner API
    print("Testing Skyscanner API...")
    headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "skyscanner-skyscanner-flight-search-v1.p.rapidapi.com"
    }
    
    test_urls = [
        "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/browsequotes/v1.0/US/USD/en-US/NYC/LAX/2024-06-15",
        "https://skyscanner-skyscanner-flight-search-v1.p.rapidapi.com/autosuggest/v1.0/UK/GBP/en-GB/?query=New York"
    ]
    
    async with httpx.AsyncClient() as client:
        for i, url in enumerate(test_urls):
            try:
                print(f"  Test {i+1}: {url.split('/')[-1] if '/' in url else url}")
                response = await client.get(url, headers=headers, timeout=30.0)
                
                print(f"    Status: {response.status_code}")
                
                if response.status_code == 200:
                    print("    ✅ Success!")
                    data = response.json()
                    if 'Quotes' in data:
                        print(f"    Found {len(data['Quotes'])} flight quotes")
                elif response.status_code == 400:
                    print("    ⚠️ Bad Request (normal for test data)")
                elif response.status_code == 401:
                    print("    ❌ Unauthorized - check your API key")
                elif response.status_code == 403:
                    print("    ❌ Forbidden - check your subscription")
                    print("    Make sure you have subscribed to the Skyscanner API")
                elif response.status_code == 429:
                    print("    ❌ Rate Limited - you've exceeded your quota")
                else:
                    print(f"    ❌ Unexpected status: {response.status_code}")
                    print(f"    Response: {response.text[:100]}...")
                    
            except httpx.TimeoutException:
                print("    ❌ Request timed out")
            except Exception as e:
                print(f"    ❌ Error: {e}")
    
    # Test Booking.com API
    print("\nTesting Booking.com API...")
    booking_headers = {
        "X-RapidAPI-Key": api_key,
        "X-RapidAPI-Host": "booking-com.p.rapidapi.com"
    }
    
    booking_url = "https://booking-com.p.rapidapi.com/v1/hotels/search?dest_type=city&dest_id=-1456928&checkin=2024-06-15&checkout=2024-06-18&adults=1&room_qty=1&page_number=1"
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(booking_url, headers=booking_headers, timeout=30.0)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                print("  ✅ Booking.com API working!")
            elif response.status_code == 401:
                print("  ❌ Unauthorized - check your API key")
            elif response.status_code == 403:
                print("  ❌ Forbidden - check your subscription")
                print("  Make sure you have subscribed to the Booking.com API")
            else:
                print(f"  ⚠️ Status {response.status_code}: {response.text[:100]}...")
                
    except Exception as e:
        print(f"  ❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("📋 Common Issues and Solutions:")
    print("=" * 50)
    print("1. 401 Unauthorized:")
    print("   - Check your RAPIDAPI_KEY is correct")
    print("   - Get your key from: https://rapidapi.com/developer/security")
    print()
    print("2. 403 Forbidden:")
    print("   - Subscribe to the required APIs on RapidAPI")
    print("   - Skyscanner: https://rapidapi.com/skyscanner/api/skyscanner-flight-search")
    print("   - Booking.com: https://rapidapi.com/booking-com/api/booking-com")
    print()
    print("3. 429 Rate Limited:")
    print("   - You've exceeded your monthly quota")
    print("   - Upgrade your plan or wait for next month")
    print()
    print("4. Connection Issues:")
    print("   - Check your internet connection")
    print("   - Try again in a few minutes")
    print("   - Check if RapidAPI is experiencing issues")
    
    return True


async def main():
    """Main diagnostic function"""
    await diagnose_rapidapi()


if __name__ == "__main__":
    asyncio.run(main())
