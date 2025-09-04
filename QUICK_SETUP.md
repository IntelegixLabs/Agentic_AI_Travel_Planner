# Quick Setup Guide - Fix RapidAPI Issues

## Current Status
✅ Database initialized successfully  
✅ Environment variables configured  
❌ RapidAPI subscriptions needed  

## Issue Identified
The diagnostic shows you need to subscribe to the travel APIs on RapidAPI:

- **403 Forbidden**: You haven't subscribed to the APIs yet
- **429 Rate Limited**: You've exceeded quota on some APIs

## Step-by-Step Fix

### 1. Go to RapidAPI Dashboard
Visit: https://rapidapi.com/developer/security

### 2. Subscribe to Required APIs

#### Skyscanner Flight Search
1. Go to: https://rapidapi.com/skyscanner/api/skyscanner-flight-search
2. Click **"Subscribe to Test"**
3. Choose **Basic (Free)** plan:
   - 100 requests/month
   - No credit card required
4. Click **"Subscribe"**

#### Booking.com Hotels
1. Go to: https://rapidapi.com/booking-com/api/booking-com
2. Click **"Subscribe to Test"**
3. Choose **Basic (Free)** plan:
   - 100 requests/month
   - No credit card required
4. Click **"Subscribe"**

#### Airbnb Search (Optional)
1. Go to: https://rapidapi.com/airbnb13/api/airbnb13
2. Click **"Subscribe to Test"**
3. Choose **Basic (Free)** plan:
   - 50 requests/month
   - No credit card required
4. Click **"Subscribe"**

### 3. Wait for Activation
- Subscriptions may take a few minutes to activate
- Check your RapidAPI dashboard to confirm active subscriptions

### 4. Test Again
Run the diagnostic again:
```bash
python diagnose_rapidapi.py
```

### 5. Start the Server
Once APIs are working:
```bash
python -m app.main
```

## Alternative: Use Mock Data

If you want to test the system without subscribing to APIs, the system will automatically fall back to mock data when APIs are unavailable.

## Free Tier Limits

| API | Free Requests/Month | Cost to Upgrade |
|-----|-------------------|-----------------|
| Skyscanner | 100 | $10/month for 10,000 |
| Booking.com | 100 | $15/month for 5,000 |
| Airbnb | 50 | $10/month for 1,000 |

## Troubleshooting

### Still Getting 403 Forbidden?
1. Make sure you clicked "Subscribe" (not just "View Pricing")
2. Check your RapidAPI dashboard shows active subscriptions
3. Wait 5-10 minutes for activation

### Still Getting 429 Rate Limited?
1. You've used your free quota
2. Wait until next month OR upgrade your plan
3. The system will use mock data as fallback

### Need Help?
- Check RapidAPI documentation
- Contact RapidAPI support
- Review the full RAPIDAPI_SETUP.md guide

## Next Steps

Once APIs are working:
1. Test the integration: `python test_rapidapi.py`
2. Start the server: `python -m app.main`
3. Visit: http://localhost:8000/docs
4. Create your first travel plan!
