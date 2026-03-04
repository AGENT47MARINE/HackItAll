# Admin User Setup Guide

## Overview

The Opportunity Access Platform uses an environment variable whitelist approach for admin user management. This allows you to designate specific users as administrators who can create and update opportunity listings.

## Configuration

### Setting Admin Users

Add admin user IDs to your `.env` file:

```bash
# Comma-separated list of Clerk user IDs that have admin privileges
ADMIN_USER_IDS=user_2abc123xyz,user_2def456uvw,user_2ghi789rst
```

### Getting User IDs

User IDs are Clerk user identifiers. You can find them:

1. **From Clerk Dashboard**:
   - Go to your Clerk dashboard
   - Navigate to Users
   - Click on a user to see their User ID (starts with `user_`)

2. **From API Response**:
   - When a user logs in, their user ID is included in the profile response
   - Call `GET /api/auth/me` to get the current user's ID

3. **From Logs**:
   - User IDs appear in server logs when users authenticate

## Admin-Protected Endpoints

The following endpoints require admin privileges:

### Create Opportunity
```
POST /api/admin/opportunities
```
Creates a new opportunity listing. Only accessible to admin users.

**Response Codes**:
- `201 Created` - Opportunity created successfully
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Not an admin user

### Update Opportunity
```
PUT /api/admin/opportunities/{opportunity_id}
```
Updates an existing opportunity. Only accessible to admin users.

**Response Codes**:
- `200 OK` - Opportunity updated successfully
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Not authenticated
- `403 Forbidden` - Not an admin user
- `404 Not Found` - Opportunity doesn't exist

## Testing Admin Access

### Test as Admin

1. Set your user ID in `.env`:
   ```bash
   ADMIN_USER_IDS=your_clerk_user_id
   ```

2. Restart the server

3. Make a request with your authentication token:
   ```bash
   curl -X POST http://localhost:8000/api/admin/opportunities \
     -H "Authorization: Bearer YOUR_CLERK_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Hackathon",
       "description": "A test event",
       "type": "hackathon",
       "deadline": "2024-12-31T23:59:59",
       "application_link": "https://example.com",
       "tags": ["tech"],
       "required_skills": [],
       "eligibility": "undergraduate"
     }'
   ```

### Test as Non-Admin

1. Use a user ID that's NOT in `ADMIN_USER_IDS`

2. Attempt to create an opportunity:
   ```bash
   curl -X POST http://localhost:8000/api/admin/opportunities \
     -H "Authorization: Bearer NON_ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{ ... }'
   ```

3. Expected response:
   ```json
   {
     "detail": "Admin privileges required for this operation"
   }
   ```
   Status code: `403 Forbidden`

## Security Considerations

### Environment Variable Approach

**Pros**:
- Simple to implement and configure
- No database changes required
- Easy to add/remove admins
- Works with Clerk authentication

**Cons**:
- Requires server restart to update admin list
- Admin list is in plain text (though not exposed to clients)
- Not suitable for large numbers of admins

### Alternative Approaches

For production systems with many admins, consider:

1. **Clerk Metadata**:
   - Store admin role in Clerk user metadata
   - Check metadata in `get_current_admin_user()`
   - Allows dynamic admin management through Clerk dashboard

2. **Database Flag**:
   - Add `is_admin` column to User model
   - Check database in `get_current_admin_user()`
   - Requires admin management UI

3. **Role-Based Access Control (RBAC)**:
   - Implement full RBAC system with roles and permissions
   - More flexible but more complex

## Troubleshooting

### "Admin privileges required" Error

**Problem**: Getting 403 error when trying to access admin endpoints

**Solutions**:
1. Verify your user ID is in `ADMIN_USER_IDS`
2. Check for typos in the user ID
3. Ensure no extra spaces in the comma-separated list
4. Restart the server after updating `.env`
5. Verify you're using the correct authentication token

### User ID Not Found

**Problem**: Don't know your Clerk user ID

**Solution**:
```bash
# Get your user ID from the /me endpoint
curl http://localhost:8000/api/auth/me \
  -H "Authorization: Bearer YOUR_TOKEN"
```

The response will include your `id` field.

### Server Not Reading Environment Variable

**Problem**: Admin check not working even with correct user ID

**Solutions**:
1. Verify `.env` file is in the project root
2. Check that `python-dotenv` is installed
3. Restart the server completely
4. Check server logs for environment variable loading

## Example Configuration

### Development `.env`
```bash
# Database
DATABASE_URL=sqlite:///./opportunity_platform.db

# Clerk Authentication
CLERK_SECRET_KEY=sk_test_your_secret_key_here

# Admin Users (development team)
ADMIN_USER_IDS=user_2abc123xyz,user_2def456uvw

# Other settings
DEBUG=True
```

### Production `.env`
```bash
# Database
DATABASE_URL=postgresql://user:pass@host:5432/dbname

# Clerk Authentication
CLERK_SECRET_KEY=sk_live_your_production_key_here

# Admin Users (production admins only)
ADMIN_USER_IDS=user_2prod1admin,user_2prod2admin

# Other settings
DEBUG=False
```

## Best Practices

1. **Limit Admin Access**: Only give admin privileges to trusted users
2. **Use Production Keys**: Never use test Clerk keys in production
3. **Rotate Regularly**: Review and update admin list periodically
4. **Log Admin Actions**: Consider adding logging for admin operations
5. **Separate Environments**: Use different admin lists for dev/staging/prod
6. **Document Admins**: Keep a record of who has admin access and why

## Future Enhancements

Consider implementing:
- Admin activity logging
- Admin invitation system
- Role hierarchy (super admin, content admin, etc.)
- Admin dashboard UI
- Audit trail for opportunity changes
- Temporary admin access (time-limited)
