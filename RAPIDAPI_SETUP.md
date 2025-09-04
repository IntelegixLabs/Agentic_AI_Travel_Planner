# RapidAPI Setup Guide for AI Travel Planner

## Overview

This guide will help you set up RapidAPI integration for the AI Travel Planner MCP Server. RapidAPI provides access to multiple travel APIs through a single platform, making it perfect for individual developers.

## Why RapidAPI?

- **Single API Key**: Access multiple travel APIs with one key
- **No Direct Partnerships**: No need to negotiate with individual travel companies
- **Cost Effective**: Pay-per-use pricing starting from free tiers
- **Easy Integration**: Unified API structure across providers
- **Reliable**: Managed infrastructure with high availability

## Step 1: Create RapidAPI Account

1. **Visit RapidAPI**: Go to [https://rapidapi.com](https://rapidapi.com)
2. **Sign Up**: Create a free account using your email or GitHub
3. **Verify Email**: Check your email and verify your account
4. **Complete Profile**: Fill in your profile information

## Step 2: Subscribe to Travel APIs

### Flight Search APIs

#### Skyscanner Flight Search
1. **Visit API Page**: [Skyscanner Flight Search](https://rapidapi.com/skyscanner/api/skyscanner-flight-search)
2. **Subscribe**: Click "Subscribe to Test" (Free tier available)
3. **Choose Plan**: 
   - **Basic (Free)**: 100 requests/month
   - **Pro**: $10/month for 10,000 requests
   - **Ultra**: $25/month for 50,000 requests
4. **Test Endpoint**: Use the test endpoint to verify connection

#### Alternative Flight APIs
- **Amadeus Flight Search**: [Amadeus API](https://rapidapi.com/amadeus/api/amadeus-flight-search)
- **Google Flights**: [Google Flights API](https://rapidapi.com/googlecloud/api/google-flights)

### Hotel Search APIs

#### Booking.com Hotels
1. **Visit API Page**: [Booking.com Hotels](https://rapidapi.com/booking-com/api/booking-com)
2. **Subscribe**: Click "Subscribe to Test"
3. **Choose Plan**:
   - **Basic (Free)**: 100 requests/month
   - **Pro**: $15/month for 5,000 requests
   - **Ultra**: $50/month for 25,000 requests

#### Airbnb Search
1. **Visit API Page**: [Airbnb Search](https://rapidapi.com/airbnb13/api/airbnb13)
2. **Subscribe**: Click "Subscribe to Test"
3. **Choose Plan**:
   - **Basic (Free)**: 50 requests/month
   - **Pro**: $10/month for 1,000 requests

## Step 3: Get Your API Key

1. **Go to Dashboard**: Click on your profile and select "Dashboard"
2. **Find API Key**: Look for "X-RapidAPI-Key" in the header
3. **Copy Key**: Copy your unique API key (starts with your username)

## Step 4: Configure Environment

1. **Create .env file**: Copy `env.example` to `.env`
2. **Add API Key**: Set your RapidAPI key:
   ```bash
   RAPIDAPI_KEY=your_rapidapi_key_here
   ```
3. **Add OpenAI Key**: Set your OpenAI API key for CrewAI:
   ```bash
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Step 5: Test the Integration

1. **Start the Server**:
   ```bash
   python -m app.main
   ```

2. **Test Health Check**:
   ```bash
   curl http://localhost:8000/api/v1/status/health
   ```

3. **Test Travel Planning**:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/travel/plan" \
        -H "Content-Type: application/json" \
        -d '{
          "destination": "Paris, France",
          "start_date": "2024-06-15",
          "end_date": "2024-06-22",
          "budget": 2000.0,
          "travelers": 2
        }'
   ```

## API Usage and Limits

### Free Tier Limits
- **Skyscanner**: 100 requests/month
- **Booking.com**: 100 requests/month
- **Airbnb**: 50 requests/month

### Monitoring Usage
1. **RapidAPI Dashboard**: Monitor your usage in real-time
2. **API Analytics**: View detailed usage statistics
3. **Billing**: Track costs and upgrade plans as needed

### Best Practices
- **Cache Results**: Implement caching to reduce API calls
- **Batch Requests**: Combine multiple searches when possible
- **Error Handling**: Implement proper error handling for rate limits
- **Fallback Data**: Use mock data when APIs are unavailable

## Troubleshooting

### Common Issues

#### 1. API Key Not Working
```bash
# Check if API key is set correctly
echo $RAPIDAPI_KEY

# Verify in .env file
cat .env | grep RAPIDAPI_KEY
```

#### 2. Rate Limit Exceeded
```json
{
  "error": "Rate limit exceeded",
  "details": "You have exceeded your monthly quota"
}
```
**Solution**: Upgrade your plan or wait for the next billing cycle

#### 3. API Not Responding
```json
{
  "error": "API service unavailable",
  "details": "The requested API is temporarily unavailable"
}
```
**Solution**: Check RapidAPI status page or try again later

#### 4. Invalid Parameters
```json
{
  "error": "Invalid parameters",
  "details": "Check your request parameters"
}
```
**Solution**: Verify date formats, airport codes, and other parameters

### Debug Mode

Enable debug mode for detailed logging:
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python -m app.main
```

## Cost Optimization

### Free Tier Strategy
1. **Start Small**: Use free tiers for development and testing
2. **Cache Aggressively**: Implement 24-hour caching for search results
3. **Mock Data**: Use mock data for non-critical features
4. **Selective APIs**: Use only the most essential APIs initially

### Paid Tier Benefits
1. **Higher Limits**: More requests per month
2. **Better Performance**: Faster response times
3. **Priority Support**: Direct support from API providers
4. **Advanced Features**: Access to premium endpoints

## Alternative APIs

If you need additional travel APIs, consider these alternatives:

### Flight APIs
- **Google Flights**: [Google Flights API](https://rapidapi.com/googlecloud/api/google-flights)
- **Kayak**: [Kayak Flight Search](https://rapidapi.com/skyscanner/api/kayak)
- **Expedia**: [Expedia Flights](https://rapidapi.com/expedia/api/expedia)

### Hotel APIs
- **Hotels.com**: [Hotels.com API](https://rapidapi.com/hotels-com/api/hotels-com)
- **Trivago**: [Trivago Hotels](https://rapidapi.com/trivago/api/trivago)
- **Priceline**: [Priceline Hotels](https://rapidapi.com/priceline/api/priceline)

### Car Rental APIs
- **Rentalcars**: [Rentalcars API](https://rapidapi.com/rentalcars/api/rentalcars)
- **Hertz**: [Hertz API](https://rapidapi.com/hertz/api/hertz)

## Security Best Practices

1. **Environment Variables**: Never commit API keys to version control
2. **Key Rotation**: Regularly rotate your API keys
3. **Access Control**: Use different keys for different environments
4. **Monitoring**: Monitor API usage for unusual patterns
5. **Backup Keys**: Keep backup API keys for critical services

## Support and Resources

### RapidAPI Support
- **Documentation**: [RapidAPI Docs](https://docs.rapidapi.com)
- **Community**: [RapidAPI Community](https://community.rapidapi.com)
- **Support**: Contact through RapidAPI dashboard

### API-Specific Support
- **Skyscanner**: [Skyscanner Developer Portal](https://developers.skyscanner.net)
- **Booking.com**: [Booking.com Partner Hub](https://partner.booking.com)
- **Airbnb**: [Airbnb Developer Portal](https://developer.airbnb.com)

### Project Support
- **GitHub Issues**: [Project Issues](https://github.com/your-username/ai-travel-planner/issues)
- **Documentation**: [Project Docs](https://docs.travelplanner.com)
- **Email**: support@travelplanner.com

## Next Steps

1. **Test All APIs**: Verify all subscribed APIs are working
2. **Implement Caching**: Add Redis or in-memory caching
3. **Add Error Handling**: Implement comprehensive error handling
4. **Monitor Usage**: Set up usage monitoring and alerts
5. **Scale Up**: Upgrade plans as your usage grows

This setup will give you access to comprehensive travel data through a single, easy-to-use API platform. The RapidAPI integration makes it much easier for individual developers to build travel applications without needing direct partnerships with travel companies.
