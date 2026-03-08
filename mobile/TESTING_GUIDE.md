# Android Mobile App - Testing Guide

## Quick Start

### 1. Start Backend API
```bash
# In the root directory
python -m uvicorn main:app --reload --port 8000
```

### 2. Start Mobile App
```bash
# In the mobile directory
cd mobile
npm install
npx expo start
```

### 3. Open in Android Emulator
- Press `a` in the Expo CLI terminal
- Or scan QR code with Expo Go app on physical device

---

## Test Scenarios

### Scenario 1: New User Registration & Onboarding
1. Launch app → See Welcome screen
2. Tap "Create Account"
3. Enter email: `test@example.com`, password: `test123`
4. Tap "Register"
5. **Expected**: Redirected to Onboarding screen
6. Enter phone number (optional)
7. Select education level (e.g., "Undergraduate")
8. Select 2-3 interests
9. Tap "Complete Onboarding"
10. **Expected**: Redirected to Home screen with bottom tabs

### Scenario 2: Existing User Login
1. Launch app → See Welcome screen
2. Tap "Login"
3. Enter demo credentials:
   - Email: `demo@test.com`
   - Password: `demo123`
4. Tap "Login"
5. **Expected**: Redirected directly to Home screen (skip onboarding)

### Scenario 3: Browse Without Account
1. Launch app → See Welcome screen
2. Tap "Browse Without Account"
3. **Expected**: Access to Home and Opportunities tabs
4. Try to save an opportunity
5. **Expected**: Prompt to register

### Scenario 4: Discover Feed
1. Login with demo account
2. Navigate to Home tab
3. **Expected**: See "For You" section with personalized recommendations
4. **Expected**: See "Trending Now" section with popular opportunities
5. Scroll through opportunities
6. Tap on an opportunity card
7. **Expected**: Navigate to Opportunity Detail screen

### Scenario 5: Search & Filter
1. Navigate to Opportunities tab (Search icon)
2. Enter search term: "hackathon"
3. **Expected**: See filtered results
4. Tap filter chips (Hackathon, Scholarship, etc.)
5. **Expected**: Results update based on filter
6. Clear search
7. **Expected**: See all opportunities

### Scenario 6: Opportunity Detail with AI Features
1. Navigate to any opportunity
2. **Expected**: See opportunity details (title, description, deadline)
3. Scroll down to see:
   - **AI Fit Analysis** section (if authenticated)
     - Recommendation text
     - Matching skills (green tags)
     - Missing skills (yellow tags)
   - **AI Project Ideas** section (if authenticated)
     - 3-5 project suggestions with titles and descriptions
4. Tap "Save to Tracker"
5. **Expected**: Success alert, opportunity saved
6. Tap "Apply Now"
7. **Expected**: Opens external application link

### Scenario 7: Tracked Dashboard
1. Navigate to Tracked tab (Pin icon)
2. **Expected**: See saved opportunities with:
   - Type badge
   - Countdown timer
   - Status timeline
3. Paste a hackathon URL in the scraper bar
4. Tap "Track"
5. **Expected**: Opportunity added to tracker
6. Tap "Update Status" on any tracked item
7. Select new status (e.g., "Applied")
8. **Expected**: Timeline updates, status changes
9. Tap "Details" to view full opportunity
10. Tap "✕" to remove from tracker
11. **Expected**: Confirmation dialog, then removed

### Scenario 8: Leagues/Gamification
1. Navigate to Leagues tab (Trophy icon)
2. **Expected**: See:
   - Current tier badge and name
   - Total XP and progress bar
   - Streak days counter
   - Global rank
3. Scroll to Achievements section
4. **Expected**: See badge grid with locked/unlocked badges
5. Scroll to Leaderboard section
6. **Expected**: See top players with XP and streaks
7. Pull down to refresh
8. **Expected**: Data updates

### Scenario 9: Profile Management
1. Navigate to Profile tab (Person icon)
2. **Expected**: See:
   - Avatar with initial
   - Email address
   - Notification settings toggles
   - Education level
   - Interests tags
3. Tap "Edit Profile"
4. Change education level
5. Add/remove interests
6. Tap "Save Changes"
7. **Expected**: Success alert, navigate back to profile
8. **Expected**: Changes reflected in profile

### Scenario 10: Notifications
1. In Profile tab, toggle "Push Notifications" ON
2. **Expected**: Permission request (if first time)
3. Grant permission
4. Toggle "Deadline Reminders" ON
5. Toggle "New Opportunities" ON
6. **Expected**: Settings saved
7. Toggle "Push Notifications" OFF
8. **Expected**: All notification settings disabled

### Scenario 11: Logout
1. In Profile tab, scroll to bottom
2. Tap "Logout"
3. **Expected**: Confirmation dialog
4. Confirm logout
5. **Expected**: Redirected to Welcome screen
6. **Expected**: Auth token cleared

---

## API Endpoint Testing

### Test Backend Connectivity
```bash
# Test if backend is running
curl http://localhost:8000/api/opportunities

# For Android emulator, use:
# http://10.0.2.2:8000/api
```

### Expected API Responses

#### Get Opportunities
```bash
GET /api/opportunities
Response: Array of opportunity objects
```

#### Get Gamification Stats
```bash
GET /api/gamification/stats
Headers: Authorization: Bearer <token>
Response: { total_xp, league_tier, tier_name, streak_days, ... }
```

#### Analyze Fit
```bash
GET /api/opportunities/:id/analyze-fit
Headers: Authorization: Bearer <token>
Response: { recommendation_text, matching_skills, missing_skills, is_ready }
```

#### Get Project Ideas
```bash
GET /api/opportunities/:id/ideas
Headers: Authorization: Bearer <token>
Response: { ideas: [{ title, description }, ...] }
```

---

## Common Issues & Solutions

### Issue: "Network request failed"
**Solution**: 
- Ensure backend is running at `http://localhost:8000`
- For Android emulator, API base URL should be `http://10.0.2.2:8000/api`
- Check `mobile/src/services/apiService.js` line 4

### Issue: "Cannot connect to Expo"
**Solution**:
- Ensure phone/emulator and computer are on same network
- Try running `npx expo start --tunnel`
- Clear Expo cache: `npx expo start -c`

### Issue: "App crashes on launch"
**Solution**:
- Clear app data in emulator
- Reinstall app
- Check for JavaScript errors in Metro bundler

### Issue: "AI features not showing"
**Solution**:
- Ensure you're logged in (not browsing without account)
- Check backend logs for AI endpoint errors
- Verify token is being sent in request headers

### Issue: "Onboarding shows every time"
**Solution**:
- Check AsyncStorage for `onboardingComplete` key
- Complete onboarding flow fully
- Restart app after completing onboarding

---

## Performance Testing

### Load Testing
1. Navigate to Opportunities tab
2. Scroll through 50+ opportunities
3. **Expected**: Smooth scrolling, no lag
4. Open and close 10 opportunity details
5. **Expected**: No memory leaks, smooth transitions

### Network Testing
1. Enable airplane mode
2. Try to load opportunities
3. **Expected**: Graceful error handling
4. Disable airplane mode
5. Pull to refresh
6. **Expected**: Data loads successfully

---

## Accessibility Testing

### Screen Reader
1. Enable TalkBack (Android)
2. Navigate through app
3. **Expected**: All buttons and text are readable
4. **Expected**: Proper focus order

### Font Scaling
1. Increase system font size to 200%
2. Navigate through app
3. **Expected**: Text scales properly, no overflow

---

## Build Testing

### Debug Build
```bash
cd mobile
npx expo run:android
```

### Release Build
```bash
cd mobile
npx expo prebuild --platform android
cd android
./gradlew assembleRelease
```

### Install APK
```bash
adb install android/app/build/outputs/apk/release/app-release.apk
```

---

## Test Checklist

- [ ] New user registration works
- [ ] Existing user login works
- [ ] Browse without account works
- [ ] Onboarding flow completes
- [ ] Home feed loads recommendations
- [ ] Search and filter work
- [ ] Opportunity detail shows all info
- [ ] AI fit analysis displays
- [ ] AI project ideas display
- [ ] Save to tracker works
- [ ] URL scraper works
- [ ] Status timeline updates
- [ ] Participation status changes
- [ ] Leagues screen loads stats
- [ ] Leaderboard displays
- [ ] Profile displays correctly
- [ ] Edit profile saves changes
- [ ] Notifications toggle works
- [ ] Logout works
- [ ] App handles network errors
- [ ] App handles auth errors
- [ ] Pull-to-refresh works
- [ ] Navigation flows correctly
- [ ] Back button works properly

---

## Reporting Issues

When reporting issues, include:
1. Device/Emulator details (Android version, device model)
2. Steps to reproduce
3. Expected behavior
4. Actual behavior
5. Screenshots/screen recording
6. Console logs from Metro bundler
7. Backend API logs (if relevant)

---

**Happy Testing! 🚀**
