# Quick Start Guide

## 🚀 Get Running in 3 Steps

### Step 1: Start Backend
```bash
# In root directory
python -m uvicorn main:app --reload --port 8000
```

### Step 2: Start Mobile App
```bash
# In mobile directory
cd mobile
npm install
npx expo start
```

### Step 3: Open in Emulator
```bash
# Press 'a' in the Expo terminal
# Or scan QR code with Expo Go app
```

---

## 🔑 Demo Login

```
Email: demo@test.com
Password: demo123
```

---

## 📱 Common Commands

### Development
```bash
# Start with cache clear
npx expo start -c

# Start with tunnel (for physical device)
npx expo start --tunnel

# Run on Android
npx expo run:android

# View logs
npx react-native log-android
```

### Building
```bash
# Generate native project
npx expo prebuild --platform android

# Build debug APK
cd android && ./gradlew assembleDebug

# Build release APK
cd android && ./gradlew assembleRelease

# Install on device
adb install android/app/build/outputs/apk/release/app-release.apk
```

### Troubleshooting
```bash
# Clear cache
npx expo start -c

# Clear Metro bundler cache
npx react-native start --reset-cache

# Clean Android build
cd android && ./gradlew clean

# Reinstall dependencies
rm -rf node_modules && npm install

# Clear watchman (if installed)
watchman watch-del-all
```

---

## 🎯 Quick Test Flow

1. **Launch app** → See Welcome screen
2. **Tap "Login"** → Enter demo credentials
3. **Navigate tabs**:
   - Home → See personalized feed
   - Search → Find opportunities
   - Tracked → View saved items
   - Leagues → Check XP and badges
   - Profile → View/edit profile
4. **Test AI features**:
   - Open any opportunity
   - Scroll to see AI Fit Analysis
   - View AI Project Ideas
5. **Test tracking**:
   - Save an opportunity
   - Go to Tracked tab
   - Update status
   - View timeline

---

## 🔧 Configuration

### Change API URL
Edit `mobile/src/services/apiService.js`:
```javascript
// For Android emulator
const API_BASE_URL = 'http://10.0.2.2:8000/api';

// For physical device (replace with your IP)
const API_BASE_URL = 'http://192.168.1.X:8000/api';

// For production
const API_BASE_URL = 'https://api.hackitall.com/api';
```

---

## 📊 Feature Checklist

- [x] Authentication (Login/Register)
- [x] Onboarding Flow
- [x] Discover Feed
- [x] Search & Filter
- [x] Opportunity Details
- [x] AI Fit Analysis
- [x] AI Project Ideas
- [x] Save to Tracker
- [x] URL Scraper
- [x] Status Timeline
- [x] Participation Tracking
- [x] Leagues/Gamification
- [x] Profile View/Edit
- [x] Push Notifications
- [x] Browse Without Account

---

## 🆘 Need Help?

- Check [TESTING_GUIDE.md](./TESTING_GUIDE.md) for detailed scenarios
- Check [README.md](./README.md) for full documentation
- Check [IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md) for features

---

**Status**: ✅ Ready to Run
