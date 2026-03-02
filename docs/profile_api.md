# Profile Management API

This document describes the profile management endpoints for the Opportunity Access Platform.

## Authentication

All profile management endpoints require authentication using a Clerk session token. Include the token in the `Authorization` header:

```
Authorization: Bearer <clerk_session_token>
```

The token is automatically managed by Clerk's frontend SDK.

## Endpoints

### 1. Get Profile

**GET** `/api/profile`

Retrieves the current authenticated user's profile information.

**Authentication:** Required

**Response:** `200 OK`

```json
{
  "id": "user-uuid",
  "email": "user@example.com",
  "phone": "+1234567890",
  "interests": ["AI", "Machine Learning"],
  "skills": ["Python", "JavaScript"],
  "education_level": "undergraduate",
  "notification_email": true,
  "notification_sms": false,
  "low_bandwidth_mode": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00",
  "participation_history": []
}
```

**Error Responses:**
- `401 Unauthorized` - Invalid or missing authentication token
- `404 Not Found` - Profile not found

---

### 2. Update Profile

**PUT** `/api/profile`

Updates the current authenticated user's profile. All fields are optional - only include the fields you want to update.

**Authentication:** Required

**Request Body:**

```json
{
  "interests": ["Data Science", "Web Development"],
  "skills": ["React", "Node.js"],
  "education_level": "graduate",
  "phone": "+1234567890",
  "notification_email": false,
  "notification_sms": true,
  "low_bandwidth_mode": true
}
```

**Response:** `200 OK`

Returns the updated profile (same format as GET /api/profile).

**Error Responses:**
- `400 Bad Request` - Validation error (e.g., empty education_level)
- `401 Unauthorized` - Invalid or missing authentication token
- `404 Not Found` - Profile not found

**Validation Rules:**
- `education_level` cannot be empty if provided
- `interests` and `skills` must be arrays if provided

---

### 3. Delete Profile

**DELETE** `/api/profile`

Deletes the current authenticated user's account and profile. This action is permanent and cannot be undone.

**Authentication:** Required

**Response:** `204 No Content`

**Error Responses:**
- `401 Unauthorized` - Invalid or missing authentication token
- `404 Not Found` - Profile not found

**Note:** This endpoint also deletes the associated user account and all related data (cascade delete).

---

## Authentication Endpoints

For completeness, here are the authentication endpoints (already implemented in `api/auth.py`):

### Register

**POST** `/api/auth/register`

Creates a new user account and profile.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "password123",
  "education_level": "undergraduate",
  "interests": ["AI", "Machine Learning"],
  "skills": ["Python", "JavaScript"],
  "phone": "+1234567890",
  "notification_email": true,
  "notification_sms": false,
  "low_bandwidth_mode": false
}
```
---

## Note on Authentication Endpoints

User registration and login are now handled by Clerk's authentication system. The platform no longer provides `/api/auth/register` or `/api/auth/login` endpoints. 

For authentication:
- Use Clerk's frontend components for sign-up and sign-in
- Clerk automatically manages session tokens
- See the [Authentication Documentation](./authentication.md) for details

---

## Example Usage

### Complete Profile Management Flow

```bash
# 1. Register a new user
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "newuser@example.com",
    "password": "securepassword123",
    "education_level": "undergraduate",
    "interests": ["AI", "Web Development"],
    "skills": ["Python", "JavaScript"]
  }'

# Response: { "access_token": "...", "user_id": "...", "email": "..." }

# 2. Get profile (use token from registration)
curl -X GET http://localhost:8000/api/profile \
  -H "Authorization: Bearer <your_token>"

# 3. Update profile
curl -X PUT http://localhost:8000/api/profile \
  -H "Authorization: Bearer <your_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "interests": ["Machine Learning", "Cloud Computing"],
    "skills": ["TensorFlow", "AWS"],
    "education_level": "graduate"
  }'

# 4. Delete profile
curl -X DELETE http://localhost:8000/api/profile \
  -H "Authorization: Bearer <your_token>"
```

---

## Requirements Validation

This implementation satisfies the following requirements:

- **Requirement 1.1**: Profile creation with interests, skills, education level, and participation history
- **Requirement 1.2**: Profile updates persist immediately
- **Requirement 1.3**: Profile display shows all current information
- **Requirement 1.4**: Required field validation (education level)
- **Requirement 1.5**: Skills and interests stored as searchable lists
- **Requirement 10.2**: Authentication required for all profile operations
- **Requirement 10.3**: Account deletion capability

---

## Testing

Comprehensive tests are available in `tests/test_profile_api.py`, including:

- Profile retrieval with authentication
- Profile updates (single and multiple fields)
- Profile deletion with cascade
- Authentication requirement validation
- Required field validation
- Complete profile lifecycle integration tests

Run tests with:

```bash
pytest tests/test_profile_api.py -v
```
