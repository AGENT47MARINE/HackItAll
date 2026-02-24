# Authentication API Documentation

## Overview

The Opportunity Access Platform uses JWT (JSON Web Token) based authentication to secure API endpoints. This document describes how to register, login, and authenticate requests.

## Endpoints

### 1. Register a New User

**Endpoint:** `POST /api/auth/register`

**Description:** Create a new user account and receive an access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "education_level": "undergraduate",
  "interests": ["technology", "science"],
  "skills": ["python", "javascript"],
  "phone": "+1234567890",
  "notification_email": true,
  "notification_sms": false,
  "low_bandwidth_mode": false
}
```

**Required Fields:**
- `email`: Valid email address
- `password`: Minimum 8 characters
- `education_level`: User's education level (cannot be empty)

**Optional Fields:**
- `interests`: Array of interest strings (default: [])
- `skills`: Array of skill strings (default: [])
- `phone`: Phone number for SMS notifications
- `notification_email`: Enable email notifications (default: true)
- `notification_sms`: Enable SMS notifications (default: false)
- `low_bandwidth_mode`: Enable low bandwidth mode (default: false)

**Response (201 Created):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```

**Error Responses:**
- `400 Bad Request`: Validation error (invalid email, short password, missing required fields)
- `409 Conflict`: Email already registered
- `422 Unprocessable Entity`: Invalid request format

---

### 2. Login

**Endpoint:** `POST /api/auth/login`

**Description:** Authenticate with email and password to receive an access token.

**Request Body:**
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid email or password

---

### 3. Get Current User

**Endpoint:** `GET /api/auth/me`

**Description:** Get the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "user@example.com",
  "phone": "+1234567890",
  "interests": ["technology", "science"],
  "skills": ["python", "javascript"],
  "education_level": "undergraduate",
  "notification_email": true,
  "notification_sms": false,
  "low_bandwidth_mode": false,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Error Responses:**
- `401 Unauthorized`: Invalid or expired token
- `403 Forbidden`: No authentication token provided
- `404 Not Found`: User profile not found

---

## Using Authentication in Requests

### Step 1: Register or Login

First, obtain an access token by registering a new account or logging in:

```bash
# Register
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123",
    "education_level": "undergraduate"
  }'

# Or Login
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepassword123"
  }'
```

### Step 2: Use the Token

Include the access token in the `Authorization` header for protected endpoints:

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

### Token Expiration

Access tokens expire after 30 minutes (configurable via `ACCESS_TOKEN_EXPIRE_MINUTES` in config). When a token expires, you'll receive a `401 Unauthorized` response. Simply login again to get a new token.

---

## Security Features

1. **Password Hashing**: All passwords are hashed using bcrypt before storage
2. **JWT Tokens**: Secure token-based authentication with expiration
3. **HTTPS Required**: In production, always use HTTPS to protect tokens in transit
4. **Token Validation**: All protected endpoints verify token authenticity and expiration

---

## Protected Endpoints

The following endpoints require authentication (include `Authorization: Bearer <token>` header):

- `GET /api/auth/me` - Get current user profile
- All profile management endpoints (future)
- All opportunity tracking endpoints (future)
- All recommendation endpoints (future)

---

## Example: Complete Authentication Flow

```python
import requests

BASE_URL = "http://localhost:8000"

# 1. Register a new user
register_response = requests.post(
    f"{BASE_URL}/api/auth/register",
    json={
        "email": "newuser@example.com",
        "password": "securepass123",
        "education_level": "undergraduate",
        "interests": ["ai", "ml"],
        "skills": ["python"]
    }
)

token = register_response.json()["access_token"]

# 2. Use the token to access protected endpoints
headers = {"Authorization": f"Bearer {token}"}

profile_response = requests.get(
    f"{BASE_URL}/api/auth/me",
    headers=headers
)

print(profile_response.json())
```

---

## Configuration

Authentication settings can be configured via environment variables:

- `SECRET_KEY`: Secret key for JWT signing (change in production!)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration time (default: 30)

Example `.env` file:
```
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```
