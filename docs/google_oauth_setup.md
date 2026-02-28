# Google OAuth Setup Guide

This guide will help you set up Google OAuth authentication for the HackItAll platform.

## Prerequisites

- Google account
- Access to Google Cloud Console

## Step 1: Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" → "New Project"
3. Name your project (e.g., "HackItAll")
4. Click "Create"

## Step 2: Enable Google+ API

1. In your project, go to "APIs & Services" → "Library"
2. Search for "Google+ API"
3. Click on it and press "Enable"

## Step 3: Create OAuth Credentials

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "OAuth client ID"
3. If prompted, configure the OAuth consent screen:
   - User Type: External (for testing) or Internal (for organization)
   - App name: HackItAll
   - User support email: Your email
   - Developer contact: Your email
   - Click "Save and Continue"
   - Scopes: Add `email` and `profile` scopes
   - Click "Save and Continue"
   - Test users: Add your email for testing
   - Click "Save and Continue"

4. Create OAuth Client ID:
   - Application type: Web application
   - Name: HackItAll Web Client
   - Authorized JavaScript origins:
     - `http://localhost:3000` (for development)
     - Your production domain (e.g., `https://hackitall.com`)
   - Authorized redirect URIs:
     - `http://localhost:3000` (for development)
     - Your production domain
   - Click "Create"

5. Copy your Client ID (looks like: `xxxxx.apps.googleusercontent.com`)

## Step 4: Configure Backend

1. Add to your `.env` file:
   ```
   GOOGLE_CLIENT_ID=your-client-id-here.apps.googleusercontent.com
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Step 5: Configure Frontend

1. Install the Google OAuth package:
   ```bash
   cd web
   npm install @react-oauth/google
   ```

2. The frontend is already configured to use Google OAuth!

## Step 6: Test the Integration

1. Start the backend:
   ```bash
   python main.py
   ```

2. Start the frontend:
   ```bash
   cd web
   npm run dev
   ```

3. Navigate to `http://localhost:3000/login`
4. Click "Continue with Google"
5. Sign in with your Google account
6. You should be logged in!

## How It Works

1. User clicks "Continue with Google" button
2. Google OAuth popup opens
3. User signs in and grants permissions
4. Frontend receives Google ID token
5. Frontend sends token to backend `/api/auth/google`
6. Backend verifies token with Google
7. Backend creates/logs in user and returns JWT token
8. User is authenticated!

## Security Notes

- Never commit your `.env` file with real credentials
- Use environment variables in production
- Keep your Client Secret secure (not needed for frontend-only flow)
- Regularly rotate your credentials
- Use HTTPS in production

## Troubleshooting

### "Invalid token" error
- Check that your GOOGLE_CLIENT_ID is correct
- Ensure the token hasn't expired
- Verify your Google Cloud project is active

### "Redirect URI mismatch"
- Add your domain to Authorized JavaScript origins
- Check for typos in the URI
- Include both http and https if needed

### "Access blocked" error
- Add test users in OAuth consent screen
- Verify your app is not in production mode without verification

## Next Steps

Once Google OAuth is working:
- Add more OAuth providers (GitHub, Microsoft, etc.)
- Implement account linking for multiple auth methods
- Add profile completion flow for new Google users
- Set up production OAuth credentials
