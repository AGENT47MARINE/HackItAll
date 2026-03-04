# New Features Guide (Tasks 14.4-17)

## Educational Content API

### Get Glossary Term
```bash
GET /api/glossary/{term}

# Example
curl http://localhost:8000/api/glossary/hackathon

# Response
{
  "term": "hackathon",
  "definition": "A hackathon is an event where programmers, designers, and other tech enthusiasts collaborate intensively on software projects over a short period, typically 24-48 hours."
}
```

### Get All Glossary Terms
```bash
GET /api/glossary

# Example
curl http://localhost:8000/api/glossary
```

### Get Application Guide
```bash
GET /api/guides/{guide_type}

# Example
curl http://localhost:8000/api/guides/scholarship

# Response
{
  "type": "scholarship",
  "title": "How to Apply for Scholarships",
  "steps": [...],
  "tips": [...]
}
```

### Mark Content as Viewed
```bash
POST /api/content/viewed?content_id={content_id}
Authorization: Bearer {token}

# Example
curl -X POST "http://localhost:8000/api/content/viewed?content_id=glossary_hackathon" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Check if Content Viewed
```bash
GET /api/content/viewed/{content_id}
Authorization: Bearer {token}

# Example
curl http://localhost:8000/api/content/viewed/glossary_hackathon \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response
{
  "content_id": "glossary_hackathon",
  "has_viewed": true
}
```

## Utility API

### Update Preferences
```bash
PUT /api/preferences
Authorization: Bearer {token}
Content-Type: application/json

{
  "notification_email": true,
  "notification_sms": false,
  "low_bandwidth_mode": false
}

# Example
curl -X PUT http://localhost:8000/api/preferences \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notification_email": true, "notification_sms": false}'
```

### Get Preferences
```bash
GET /api/preferences
Authorization: Bearer {token}

# Example
curl http://localhost:8000/api/preferences \
  -H "Authorization: Bearer YOUR_TOKEN"

# Response
{
  "notification_email": true,
  "notification_sms": false,
  "low_bandwidth_mode": false
}
```

### Export User Data
```bash
GET /api/export
Authorization: Bearer {token}

# Example
curl http://localhost:8000/api/export \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -o user_data.json

# Response (JSON file download)
{
  "user": {...},
  "profile": {...},
  "tracked_opportunities": [...],
  "participation_history": [...],
  "reminders": [...],
  "export_date": "2026-03-02T01:50:00.000000"
}
```

## Scheduled Jobs

The following jobs run automatically in the background:

### 1. Deadline Reminders (Every Hour)
- Checks for upcoming deadlines
- Sends 7-day and 24-hour reminders
- Marks reminders as sent

### 2. Opportunity Archival (Daily at Midnight)
- Archives expired opportunities
- Marks tracked opportunities as expired

### 3. Recommendation Updates (Every 6 Hours)
- Recalculates recommendations for all users
- Updates cache with fresh data

### 4. Reminder Cleanup (Daily at 2 AM)
- Removes old sent reminders (>30 days)
- Prevents database bloat

### Starting the Scheduler
The scheduler starts automatically with the FastAPI application. No manual intervention needed.

To run the scheduler standalone:
```bash
python scheduler.py
```

## Input Validation

### Using Validators in Code
```python
from utils.validators import InputValidator

# Email validation
is_valid = InputValidator.validate_email("test@example.com")

# Phone validation
is_valid = InputValidator.validate_phone("+1234567890")

# URL validation
is_valid = InputValidator.validate_url("https://example.com")

# Search query sanitization
safe_query = InputValidator.sanitize_search_query(user_input)

# Date validation
date_obj = InputValidator.validate_date("2026-12-31")

# Deadline validation (must be future)
is_valid = InputValidator.validate_deadline(deadline_datetime)

# Education level validation
is_valid = InputValidator.validate_education_level("bachelor")

# Required fields validation
is_valid, error = InputValidator.validate_required_fields(
    data={"name": "John", "email": "john@example.com"},
    required_fields=["name", "email", "phone"]
)
```

## Error Handling

### Error Response Format
All errors follow a consistent format:

```json
{
  "error": "Error Type",
  "message": "Human-readable error message",
  "details": []  // Optional, for validation errors
}
```

### HTTP Status Codes
- `400 Bad Request` - Validation errors
- `401 Unauthorized` - Authentication errors
- `403 Forbidden` - Authorization errors
- `404 Not Found` - Resource not found
- `429 Too Many Requests` - Rate limit exceeded
- `500 Internal Server Error` - Server errors

### Rate Limiting
- Limit: 100 requests per minute per user/IP
- Headers in response:
  - `X-RateLimit-Limit`: Maximum requests allowed
  - `X-RateLimit-Remaining`: Requests remaining
  - `X-RateLimit-Reset`: Unix timestamp when limit resets

## Caching

### Cache Configuration
The application uses Redis for caching with the following TTLs:

- User Profiles: 15 minutes
- Opportunity Listings: 5 minutes
- Recommendations: 1 hour
- Educational Content: Indefinite

### Using Cache in Code
```python
from services.cache_service import cache, CacheKeys, CacheTTL

# Set cache
cache.set(
    CacheKeys.user_profile(user_id),
    profile_data,
    ttl=CacheTTL.PROFILE
)

# Get cache
cached_data = cache.get(CacheKeys.user_profile(user_id))

# Delete cache
cache.delete(CacheKeys.user_profile(user_id))

# Delete pattern
cache.delete_pattern("profile:*")
```

### Cache Keys
- `profile:{user_id}` - User profile
- `opportunities:list:{hash}` - Opportunity listings
- `opportunity:{id}` - Opportunity details
- `recommendations:{user_id}` - User recommendations
- `content:{type}:{id}` - Educational content

### Graceful Degradation
If Redis is unavailable, the application continues to work without caching. All cache operations fail silently and return None.

## Environment Setup

### Required Environment Variables
```bash
# Redis (optional, but recommended)
REDIS_URL=redis://localhost:6379/0

# Already configured
CLERK_SECRET_KEY=your_clerk_secret
DATABASE_URL=sqlite:///./opportunity_platform.db
```

### Starting Redis
```bash
# Using Docker
docker run -d -p 6379:6379 redis:latest

# Or install locally
# Windows: Download from https://github.com/microsoftarchive/redis/releases
# Mac: brew install redis && redis-server
# Linux: sudo apt-get install redis-server && redis-server
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Running the Application
```bash
# Start the FastAPI application (includes scheduler)
python main.py

# Or with uvicorn
uvicorn main:app --reload
```

## Testing

### Run Feature Tests
```bash
python test_new_features.py
```

### Manual API Testing
Use the interactive API docs at `http://localhost:8000/docs` to test all endpoints.

## Monitoring

### Logs
All scheduled jobs and errors are logged. Check the console output for:
- Job execution status
- Cache operations
- Rate limiting events
- Error details

### Health Check
```bash
GET /health

# Response
{
  "status": "healthy"
}
```

## Troubleshooting

### Redis Connection Issues
If you see "Redis not available" warnings:
1. Check if Redis is running: `redis-cli ping`
2. Verify REDIS_URL in .env
3. Application will work without Redis (no caching)

### Scheduler Not Running
1. Check logs for scheduler startup message
2. Verify APScheduler is installed: `pip show APScheduler`
3. Check for errors in scheduler.py

### Rate Limiting Issues
If you're being rate limited:
1. Wait 60 seconds for the limit to reset
2. Check X-RateLimit-* headers in response
3. Reduce request frequency

### Validation Errors
If you get validation errors:
1. Check the error details in the response
2. Verify input format matches requirements
3. Use the validators module to pre-validate data

## Best Practices

1. **Always validate user input** before processing
2. **Use cache keys consistently** via CacheKeys class
3. **Handle cache misses gracefully** (cache may be empty)
4. **Monitor rate limit headers** to avoid hitting limits
5. **Log errors appropriately** for debugging
6. **Test with Redis disabled** to ensure graceful degradation
7. **Keep educational content updated** in JSON files
8. **Monitor scheduled job logs** for failures

## Next Steps

1. Implement property tests for validation
2. Add integration tests for complete flows
3. Monitor cache hit rates
4. Optimize cache TTLs based on usage
5. Add more educational content
6. Implement cache warming strategies
7. Add metrics and monitoring
