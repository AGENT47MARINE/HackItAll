# Test Migration Guide: JWT to Clerk Authentication

## Overview

This guide explains how to update test files to use mocked Clerk authentication instead of JWT tokens.

## Changes Made

### 1. Created Test Utilities (`tests/test_utils.py`)

New helper functions for mocking Clerk authentication:

```python
from tests.test_utils import mock_clerk_auth, create_auth_header

# Mock Clerk authentication
with mock_clerk_auth("user-id-123"):
    response = client.get("/api/profile", headers=create_auth_header())
```

### 2. Updated Test Files

#### ✅ `tests/test_auth_service.py` - COMPLETE
- Removed JWT token creation/verification tests
- Kept user lookup and authentication tests
- No JWT dependencies remain

#### ✅ `tests/test_profile_api.py` - COMPLETE
- Removed `auth_token` fixture
- Updated all tests to use `mock_clerk_auth()`
- All authentication now mocked via Clerk

#### ✅ `tests/test_opportunity_api.py` - COMPLETE
- Removed JWT token fixtures
- Updated to use `mock_clerk_auth()` and `create_auth_header()`
- Admin tests now mock admin claims

#### ⚠️ `tests/test_tracking_api.py` - PARTIALLY COMPLETE
- Removed `auth_token` fixture
- Updated `TestSaveOpportunity` class
- **REMAINING**: Need to update remaining test classes

## How to Complete test_tracking_api.py Migration

### Pattern to Replace

**OLD (JWT-based):**
```python
def test_example(self, client, test_user, test_opportunity, auth_token):
    response = client.post(
        "/api/tracked",
        json={"opportunity_id": test_opportunity["id"]},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
```

**NEW (Clerk-mocked):**
```python
def test_example(self, client, test_user, test_opportunity):
    with mock_clerk_auth(test_user["id"]):
        response = client.post(
            "/api/tracked",
            json={"opportunity_id": test_opportunity["id"]},
            headers=create_auth_header()
        )
```

### Steps to Complete

1. **Remove `auth_token` parameter** from all test method signatures
2. **Wrap authenticated requests** with `mock_clerk_auth(test_user["id"]):`
3. **Replace header creation** with `create_auth_header()`

### Test Classes Needing Updates in test_tracking_api.py

- ✅ `TestSaveOpportunity` - DONE
- ⚠️ `TestGetTrackedOpportunities` - TODO
- ⚠️ `TestRemoveTrackedOpportunity` - TODO
- ⚠️ `TestAddParticipation` - TODO
- ⚠️ `TestUpdateParticipation` - TODO
- ⚠️ `TestGetParticipationHistory` - TODO
- ⚠️ `TestTrackingIntegration` - TODO

## Running Tests

After migration, tests should run without JWT dependencies:

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_auth_service.py
pytest tests/test_profile_api.py
pytest tests/test_opportunity_api.py
pytest tests/test_tracking_api.py

# Run with verbose output
pytest -v tests/
```

## Verification

To verify JWT dependencies are removed:

```bash
# Check for JWT imports in test files
grep -r "from jose" tests/
grep -r "import jwt" tests/
grep -r "create_access_token" tests/
grep -r "verify_token" tests/

# Should return no results (except in comments/docstrings)
```

## Benefits of Clerk Mocking

1. **Simpler Tests**: No need to create real JWT tokens
2. **Faster Execution**: Mocking is faster than token generation
3. **Better Isolation**: Tests don't depend on JWT library
4. **Easier Maintenance**: Centralized auth mocking in `test_utils.py`
5. **Realistic**: Mirrors production Clerk authentication flow

## Troubleshooting

### Import Errors
If you see `ImportError: cannot import name 'mock_clerk_auth'`:
- Ensure `tests/test_utils.py` exists
- Check that `tests/__init__.py` exists (can be empty)

### Mock Not Working
If authentication still fails:
- Verify you're patching the correct function: `'api.auth.get_current_user'`
- Ensure the mock is active during the request (use `with` statement)
- Check that headers are being sent: `headers=create_auth_header()`

### Test Failures
If tests fail after migration:
- Verify user IDs match between test fixtures and mocks
- Check that the mocked user exists in the test database
- Ensure the mock returns a string user ID, not a dict

## Next Steps

1. Complete migration of `test_tracking_api.py`
2. Run full test suite to verify all tests pass
3. Remove any remaining JWT-related test utilities
4. Update test documentation to reflect Clerk authentication
