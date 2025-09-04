#!/usr/bin/env python3
"""
Setup verification script for AI Travel Planner
"""

import os
import sys
from dotenv import load_dotenv

def check_environment():
    """Check environment setup"""
    print("🔍 Checking Environment Setup...")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Check Python version
    python_version = sys.version_info
    print(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    if python_version >= (3, 8):
        print("✅ Python version is compatible")
    else:
        print("❌ Python 3.8+ required")
        return False
    
    # Check required environment variables
    required_vars = ["RAPIDAPI_KEY", "OPENAI_API_KEY"]
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {value[:10]}...")
        else:
            print(f"❌ {var}: Not set")
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n❌ Missing environment variables: {', '.join(missing_vars)}")
        print("\nTo fix this:")
        print("1. Copy env.example to .env:")
        print("   cp env.example .env")
        print("2. Edit .env and add your API keys:")
        print("   RAPIDAPI_KEY=your_rapidapi_key_here")
        print("   OPENAI_API_KEY=your_openai_api_key_here")
        return False
    
    # Check if .env file exists
    if os.path.exists(".env"):
        print("✅ .env file found")
    else:
        print("❌ .env file not found")
        print("Create .env file with your API keys")
        return False
    
    return True

def check_dependencies():
    """Check if required packages are installed"""
    print("\n📦 Checking Dependencies...")
    print("=" * 40)
    
    required_packages = [
        "fastapi",
        "uvicorn",
        "crewai",
        "pydantic",
        "httpx",
        "python-dotenv",
        "sqlalchemy"
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n❌ Missing packages: {', '.join(missing_packages)}")
        print("\nTo fix this:")
        print("pip install -r requirements.txt")
        return False
    
    return True

def check_rapidapi_subscription():
    """Check RapidAPI subscription status"""
    print("\n🔌 Checking RapidAPI Setup...")
    print("=" * 40)
    
    api_key = os.getenv("RAPIDAPI_KEY")
    if not api_key:
        print("❌ RAPIDAPI_KEY not set")
        return False
    
    print("✅ RAPIDAPI_KEY is set")
    print("\n📋 Required API Subscriptions:")
    print("1. Skyscanner Flight Search")
    print("   URL: https://rapidapi.com/skyscanner/api/skyscanner-flight-search")
    print("   Free tier: 100 requests/month")
    print()
    print("2. Booking.com Hotels")
    print("   URL: https://rapidapi.com/booking-com/api/booking-com")
    print("   Free tier: 100 requests/month")
    print()
    print("3. Airbnb Search (Optional)")
    print("   URL: https://rapidapi.com/airbnb13/api/airbnb13")
    print("   Free tier: 50 requests/month")
    print()
    print("⚠️ Make sure you have subscribed to at least the first two APIs")
    
    return True

def main():
    """Main verification function"""
    print("🚀 AI Travel Planner - Setup Verification")
    print("=" * 50)
    
    checks = [
        check_environment(),
        check_dependencies(),
        check_rapidapi_subscription()
    ]
    
    print("\n" + "=" * 50)
    if all(checks):
        print("✅ All checks passed! Your setup looks good.")
        print("\nNext steps:")
        print("1. Run: python diagnose_rapidapi.py")
        print("2. Run: python test_rapidapi.py")
        print("3. Start server: python -m app.main")
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        print("\nFor help:")
        print("- Read RAPIDAPI_SETUP.md for detailed setup instructions")
        print("- Check the troubleshooting section in README.md")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
