# AI Travel Planner MCP Server - Deployment Guide

## Overview

This guide provides comprehensive instructions for deploying the AI Travel Planner MCP Server in various environments, from development to production.

## Prerequisites

- Python 3.8 or higher
- Docker and Docker Compose (for containerized deployment)
- API keys for external services (Amadeus, Booking.com, etc.)
- OpenAI API key for CrewAI agents

## Environment Setup

### 1. Development Environment

#### Local Development

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
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**
   ```bash
   python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
   ```

6. **Run the application**
   ```bash
   python -m app.main
   ```

#### Docker Development

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build
   ```

2. **Access the application**
   - API: http://localhost:8000
   - Documentation: http://localhost:8000/docs

### 2. Production Environment

#### Docker Production Deployment

1. **Create production environment file**
   ```bash
   cp env.example .env.production
   # Edit .env.production with production values
   ```

2. **Build production image**
   ```bash
   docker build -t ai-travel-planner:latest .
   ```

3. **Run production container**
   ```bash
   docker run -d \
     --name travel-planner \
     -p 8000:8000 \
     --env-file .env.production \
     -v /path/to/data:/app/data \
     -v /path/to/logs:/app/logs \
     ai-travel-planner:latest
   ```

#### Kubernetes Deployment

1. **Create Kubernetes manifests**

   **namespace.yaml**
   ```yaml
   apiVersion: v1
   kind: Namespace
   metadata:
     name: travel-planner
   ```

   **deployment.yaml**
   ```yaml
   apiVersion: apps/v1
   kind: Deployment
   metadata:
     name: travel-planner
     namespace: travel-planner
   spec:
     replicas: 3
     selector:
       matchLabels:
         app: travel-planner
     template:
       metadata:
         labels:
           app: travel-planner
       spec:
         containers:
         - name: travel-planner
           image: ai-travel-planner:latest
           ports:
           - containerPort: 8000
           env:
           - name: HOST
             value: "0.0.0.0"
           - name: PORT
             value: "8000"
           - name: DEBUG
             value: "false"
           envFrom:
           - secretRef:
               name: travel-planner-secrets
           resources:
             requests:
               memory: "256Mi"
               cpu: "250m"
             limits:
               memory: "512Mi"
               cpu: "500m"
           livenessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 30
             periodSeconds: 10
           readinessProbe:
             httpGet:
               path: /health
               port: 8000
             initialDelaySeconds: 5
             periodSeconds: 5
   ```

   **service.yaml**
   ```yaml
   apiVersion: v1
   kind: Service
   metadata:
     name: travel-planner-service
     namespace: travel-planner
   spec:
     selector:
       app: travel-planner
     ports:
     - protocol: TCP
       port: 80
       targetPort: 8000
     type: LoadBalancer
   ```

   **secret.yaml**
   ```yaml
   apiVersion: v1
   kind: Secret
   metadata:
     name: travel-planner-secrets
     namespace: travel-planner
   type: Opaque
   data:
     OPENAI_API_KEY: <base64-encoded-key>
     AMADEUS_API_KEY: <base64-encoded-key>
     AMADEUS_API_SECRET: <base64-encoded-secret>
     # Add other secrets as needed
   ```

2. **Deploy to Kubernetes**
   ```bash
   kubectl apply -f namespace.yaml
   kubectl apply -f secret.yaml
   kubectl apply -f deployment.yaml
   kubectl apply -f service.yaml
   ```

#### Cloud Platform Deployment

##### AWS ECS

1. **Create ECS task definition**
   ```json
   {
     "family": "travel-planner",
     "networkMode": "awsvpc",
     "requiresCompatibilities": ["FARGATE"],
     "cpu": "256",
     "memory": "512",
     "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
     "containerDefinitions": [
       {
         "name": "travel-planner",
         "image": "your-account.dkr.ecr.region.amazonaws.com/ai-travel-planner:latest",
         "portMappings": [
           {
             "containerPort": 8000,
             "protocol": "tcp"
           }
         ],
         "environment": [
           {
             "name": "HOST",
             "value": "0.0.0.0"
           },
           {
             "name": "PORT",
             "value": "8000"
           }
         ],
         "secrets": [
           {
             "name": "OPENAI_API_KEY",
             "valueFrom": "arn:aws:secretsmanager:region:account:secret:travel-planner/openai-key"
           }
         ],
         "logConfiguration": {
           "logDriver": "awslogs",
           "options": {
             "awslogs-group": "/ecs/travel-planner",
             "awslogs-region": "us-west-2",
             "awslogs-stream-prefix": "ecs"
           }
         }
       }
     ]
   }
   ```

2. **Create ECS service**
   ```bash
   aws ecs create-service \
     --cluster your-cluster \
     --service-name travel-planner \
     --task-definition travel-planner:1 \
     --desired-count 3 \
     --launch-type FARGATE \
     --network-configuration "awsvpcConfiguration={subnets=[subnet-12345],securityGroups=[sg-12345],assignPublicIp=ENABLED}"
   ```

##### Google Cloud Run

1. **Deploy to Cloud Run**
   ```bash
   gcloud run deploy travel-planner \
     --image gcr.io/your-project/ai-travel-planner:latest \
     --platform managed \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars HOST=0.0.0.0,PORT=8080 \
     --set-secrets OPENAI_API_KEY=openai-key:latest
   ```

##### Azure Container Instances

1. **Deploy to Azure Container Instances**
   ```bash
   az container create \
     --resource-group myResourceGroup \
     --name travel-planner \
     --image your-registry.azurecr.io/ai-travel-planner:latest \
     --cpu 1 \
     --memory 1 \
     --ports 8000 \
     --environment-variables HOST=0.0.0.0 PORT=8000 \
     --secure-environment-variables OPENAI_API_KEY=your-key
   ```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `HOST` | Server host | `0.0.0.0` | No |
| `PORT` | Server port | `8000` | No |
| `DEBUG` | Debug mode | `False` | No |
| `LOG_LEVEL` | Logging level | `INFO` | No |
| `DATABASE_URL` | Database connection string | `sqlite:///./travel_planner.db` | No |
| `OPENAI_API_KEY` | OpenAI API key for CrewAI | - | Yes |
| `AMADEUS_API_KEY` | Amadeus API key | - | No |
| `AMADEUS_API_SECRET` | Amadeus API secret | - | No |
| `BOOKING_COM_API_KEY` | Booking.com API key | - | No |
| `EXPEDIA_API_KEY` | Expedia API key | - | No |
| `AIRBNB_API_KEY` | Airbnb API key | - | No |
| `SKYSCANNER_API_KEY` | Skyscanner API key | - | No |

### Database Configuration

#### SQLite (Development)
```bash
DATABASE_URL=sqlite:///./travel_planner.db
```

#### PostgreSQL (Production)
```bash
DATABASE_URL=postgresql://username:password@localhost:5432/travel_planner
```

#### MySQL (Production)
```bash
DATABASE_URL=mysql://username:password@localhost:3306/travel_planner
```

## Monitoring and Logging

### Application Logs

The application uses structured logging with the following levels:
- `DEBUG`: Detailed information for debugging
- `INFO`: General information about application flow
- `WARNING`: Warning messages for potential issues
- `ERROR`: Error messages for failed operations
- `CRITICAL`: Critical errors that may cause application failure

### Health Checks

The application provides health check endpoints:
- `/health`: Basic health check
- `/api/v1/status/health`: Detailed health information
- `/api/v1/status/metrics`: Service metrics and statistics

### Monitoring Integration

#### Prometheus Metrics

Add Prometheus metrics collection:

```python
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def prometheus_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    REQUEST_COUNT.labels(method=request.method, endpoint=request.url.path).inc()
    REQUEST_DURATION.observe(time.time() - start_time)
    return response

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

#### Grafana Dashboard

Create a Grafana dashboard to visualize:
- Request rates and response times
- Error rates
- Database performance
- External API response times
- Agent performance metrics

## Security Considerations

### API Security

1. **Authentication**
   ```python
   from fastapi import Depends, HTTPException, status
   from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
   
   security = HTTPBearer()
   
   async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
       if credentials.credentials != "your-secret-token":
           raise HTTPException(
               status_code=status.HTTP_401_UNAUTHORIZED,
               detail="Invalid authentication credentials"
           )
       return credentials.credentials
   ```

2. **Rate Limiting**
   ```python
   from slowapi import Limiter, _rate_limit_exceeded_handler
   from slowapi.util import get_remote_address
   from slowapi.errors import RateLimitExceeded
   
   limiter = Limiter(key_func=get_remote_address)
   app.state.limiter = limiter
   app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
   
   @app.post("/api/v1/travel/plan")
   @limiter.limit("10/minute")
   async def create_travel_plan(request: Request, ...):
       # Implementation
   ```

3. **CORS Configuration**
   ```python
   from fastapi.middleware.cors import CORSMiddleware
   
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["https://yourdomain.com"],
       allow_credentials=True,
       allow_methods=["GET", "POST", "PUT", "DELETE"],
       allow_headers=["*"],
   )
   ```

### Data Security

1. **Encryption at Rest**
   - Use encrypted database connections
   - Encrypt sensitive data in the database
   - Use secure file storage for logs and data

2. **Encryption in Transit**
   - Use HTTPS/TLS for all API communications
   - Use secure connections for database access
   - Implement certificate pinning for mobile apps

3. **Secrets Management**
   - Use environment variables for sensitive configuration
   - Implement secrets rotation
   - Use cloud-native secrets management services

## Performance Optimization

### Caching

1. **Redis Caching**
   ```python
   import redis
   from functools import wraps
   
   redis_client = redis.Redis(host='localhost', port=6379, db=0)
   
   def cache_result(expiration=300):
       def decorator(func):
           @wraps(func)
           async def wrapper(*args, **kwargs):
               cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
               cached_result = redis_client.get(cache_key)
               if cached_result:
                   return json.loads(cached_result)
               
               result = await func(*args, **kwargs)
               redis_client.setex(cache_key, expiration, json.dumps(result))
               return result
           return wrapper
       return decorator
   ```

2. **Database Query Optimization**
   - Use database indexes
   - Implement query result caching
   - Use connection pooling
   - Optimize N+1 query problems

### Load Balancing

1. **Nginx Configuration**
   ```nginx
   upstream travel_planner {
       server 127.0.0.1:8000;
       server 127.0.0.1:8001;
       server 127.0.0.1:8002;
   }
   
   server {
       listen 80;
       server_name yourdomain.com;
       
       location / {
           proxy_pass http://travel_planner;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```

## Backup and Recovery

### Database Backup

1. **Automated Backups**
   ```bash
   #!/bin/bash
   # backup.sh
   DATE=$(date +%Y%m%d_%H%M%S)
   BACKUP_FILE="travel_planner_backup_$DATE.sql"
   
   pg_dump $DATABASE_URL > $BACKUP_FILE
   gzip $BACKUP_FILE
   
   # Upload to cloud storage
   aws s3 cp $BACKUP_FILE.gz s3://your-backup-bucket/
   ```

2. **Backup Schedule**
   ```bash
   # Add to crontab
   0 2 * * * /path/to/backup.sh
   ```

### Disaster Recovery

1. **Recovery Procedures**
   - Document recovery steps
   - Test recovery procedures regularly
   - Maintain backup verification
   - Implement monitoring for backup failures

2. **High Availability**
   - Deploy across multiple availability zones
   - Implement database replication
   - Use load balancers for redundancy
   - Implement circuit breakers for external services

## Troubleshooting

### Common Issues

1. **Database Connection Issues**
   - Check database URL configuration
   - Verify database server is running
   - Check network connectivity
   - Verify credentials

2. **External API Issues**
   - Check API key validity
   - Verify rate limits
   - Check network connectivity
   - Review API documentation for changes

3. **Performance Issues**
   - Monitor resource usage
   - Check database query performance
   - Review external API response times
   - Analyze application logs

### Debug Mode

Enable debug mode for troubleshooting:
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
python -m app.main
```

### Log Analysis

Use log analysis tools:
```bash
# View recent errors
tail -f logs/travel_planner.log | grep ERROR

# Analyze request patterns
grep "POST /api/v1/travel/plan" logs/travel_planner.log | wc -l

# Check response times
grep "Request completed" logs/travel_planner.log | awk '{print $NF}' | sort -n
```

## Maintenance

### Regular Maintenance Tasks

1. **Database Maintenance**
   - Vacuum and analyze database
   - Update database statistics
   - Clean up old data
   - Monitor database size

2. **Application Maintenance**
   - Update dependencies
   - Review and rotate logs
   - Monitor disk space
   - Update SSL certificates

3. **Security Maintenance**
   - Update API keys
   - Review access logs
   - Update security patches
   - Conduct security audits

### Updates and Upgrades

1. **Application Updates**
   ```bash
   # Pull latest changes
   git pull origin main
   
   # Update dependencies
   pip install -r requirements.txt
   
   # Run database migrations
   alembic upgrade head
   
   # Restart application
   systemctl restart travel-planner
   ```

2. **Rollback Procedures**
   ```bash
   # Rollback to previous version
   git checkout previous-version
   pip install -r requirements.txt
   alembic downgrade -1
   systemctl restart travel-planner
   ```

This deployment guide provides comprehensive instructions for deploying the AI Travel Planner MCP Server in various environments. Follow the appropriate section based on your deployment requirements and infrastructure setup.
