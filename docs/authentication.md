# Authentication API Documentation

## Overview

The Opportunity Access Platform uses **Clerk** for authentication to secure API endpoints. Clerk provides enterprise-grade authentication with built-in security features, automatic token management, and session handling. This document describes how authentication works in the platform.

## Authentication Flow

1. **User Registration/Login**: Handled by Clerk's frontend components (embedded in the web/mobile app)
2. **Token Generation**: Clerk automatically generates secure session tokens
3. **Token Verification**: Backend verifies Clerk tokens on protected endpoints using Clerk's SDK
4. **User Identification**: Clerk tokens contain user ID (`sub` claim) for database operations

## Why Clerk?

Clerk was chosen to replace the previous JWT implementation because it provides:
- ✅ Automatic token rotation and refresh
- ✅ Built-in security best practices
- ✅ Session management across devices
- ✅ Social login support (Google, GitHub, etc.)
- ✅ Email verification and password reset flows
- ✅ No need to manage JWT secrets or token expiration logic

## Endpoints

### Get Current User

**Endpoint:** `GET /api/auth/me`

**Description:** Get the authenticated user's profile information.

**Headers:**
```
Authorization: Bearer <clerk_session_token>
```

**Response (200 OK):**
```json
{
  "id": "user_2abc123xyz",
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
- `404 Not Found`: User profile not found
- `500 Internal Server Error`: Clerk configuration error

---

## Using Authentication in Requests

### Frontend Integration

The frontend uses Clerk's React components for authentication:

```javascript
import { SignIn, SignUp, useAuth } from '@clerk/clerk-react';

// In your app
function App() {
  const { getToken } = useAuth();
  
  // Get token for API requests
  const token = await getToken();
  
  // Use token in API calls
  const response = await fetch('/api/auth/me', {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
}
```

### API Requests

Include the Clerk session token in the `Authorization` header for protected endpoints:

```bash
curl -X GET http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer <clerk_session_token>"
```

---

## Security Features

1. **Clerk Token Verification**: All tokens are verified using Clerk's SDK
2. **Automatic Token Rotation**: Clerk handles token refresh automatically
3. **Session Management**: Clerk manages sessions across devices
4. **HTTPS Required**: In production, always use HTTPS to protect tokens in transit
5. **Password Hashing**: Passwords are managed securely by Clerk

---

## Protected Endpoints

The following endpoints require authentication (include `Authorization: Bearer <token>` header):

- `GET /api/auth/me` - Get current user profile
- All profile management endpoints
- All opportunity tracking endpoints
- All recommendation endpoints

---

## Configuration

### Backend Configuration

Set the Clerk secret key in your environment:

```bash
CLERK_SECRET_KEY=sk_test_...
```

### Frontend Configuration

Configure Clerk in your frontend app:

```javascript
import { ClerkProvider } from '@clerk/clerk-react';

const clerkPubKey = process.env.REACT_APP_CLERK_PUBLISHABLE_KEY;

<ClerkProvider publishableKey={clerkPubKey}>
  <App />
</ClerkProvider>
```

---

## Migration from JWT

The platform previously used JWT-based authentication. Key changes:

- ❌ **Removed**: Manual JWT token creation and verification
- ❌ **Removed**: `/api/auth/register` and `/api/auth/login` endpoints
- ❌ **Removed**: JWT configuration (`SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES`)
- ✅ **Added**: Clerk SDK integration
- ✅ **Added**: Automatic token management
- ✅ **Kept**: User lookup methods in `AuthService` for backward compatibility

---

## Troubleshooting

### "CLERK_SECRET_KEY not configured"
- Ensure `CLERK_SECRET_KEY` is set in your `.env` file
- Restart the backend server after adding the key

### "Could not validate credentials"
- Check that the frontend is using the correct Clerk publishable key
- Verify the token is being sent in the `Authorization` header
- Ensure the token hasn't expired (Clerk handles this automatically)

### "User profile not found"
- The user exists in Clerk but not in the local database
- Ensure the profile creation flow runs after Clerk authentication
- Check that the user ID from Clerk matches the database user ID

---

## Resources

- [Clerk Documentation](https://clerk.com/docs)
- [Clerk Backend SDK](https://clerk.com/docs/backend-requests/handling/python)
- [Clerk React SDK](https://clerk.com/docs/references/react/overview)
