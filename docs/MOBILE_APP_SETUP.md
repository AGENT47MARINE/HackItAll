# 📱 Mobile App Setup Guide

## Quick Start - View Your Mobile App

### Option 1: Run on Web Browser (Easiest - No Phone Needed)

1. Open a new terminal and navigate to mobile folder:
```bash
cd mobile
```

2. Start the Expo development server:
```bash
npm start
```

3. Press `w` to open in web browser
   - The app will open at `http://localhost:8081`
   - You can test all features in the browser

### Option 2: Run on Your Phone (Recommended for Full Experience)

#### Prerequisites:
- Install **Expo Go** app on your phone:
  - iOS: https://apps.apple.com/app/expo-go/id982107779
  - Android: https://play.google.com/store/apps/details?id=host.exp.exponent

#### Steps:

1. **Update API URL for your network:**
   
   Find your computer's IP address:
   - Windows: Run `ipconfig` and look for "IPv4 Address"
   - Mac/Linux: Run `ifconfig` and look for "inet"
   
   Edit `mobile/src/services/apiService.js` line 4:
   ```javascript
   const API_BASE_URL = 'http://YOUR_IP_ADDRESS:8000/api';
   // Example: 'http://192.168.1.100:8000/api'
   ```

2. **Make sure backend is running:**
   ```bash
   # In the main project folder
   venv\Scripts\python.exe main.py
   ```

3. **Start the mobile app:**
   ```bash
   cd mobile
   npm start
   ```

4. **Scan QR code:**
   - A QR code will appear in the terminal
   - Open Expo Go app on your phone
   - Tap "Scan QR code" and scan it
   - The app will load on your phone!

### Option 3: Run on iOS Simulator (Mac Only)

```bash
cd mobile
npm run ios
```

### Option 4: Run on Android Emulator

1. Install Android Studio and set up an emulator
2. Start the emulator
3. Run:
```bash
cd mobile
npm run android
```

## Current Status

✅ **Fully Implemented Features:**
- User Registration & Login
- Home screen with personalized recommendations
- Search & filter opportunities
- Opportunity details view
- Save opportunities to tracker
- View saved opportunities
- User profile display
- Push notification setup

✅ **Backend API:** Running on http://localhost:8000

✅ **Web App:** Running on http://localhost:3000

## Troubleshooting

### "Cannot connect to API"
- Make sure backend is running: `venv\Scripts\python.exe main.py`
- For phone: Use your computer's IP address, not localhost
- Check that your phone and computer are on the same WiFi network

### "Expo Go not loading"
- Make sure you're on the same WiFi network
- Try restarting the Expo server: Press `r` in terminal
- Clear cache: `npm start -- --clear`

### "Module not found" errors
- Reinstall dependencies: `npm install`
- Clear cache: `npm start -- --clear`

## Testing the App

1. **Register a new account** (or use existing credentials)
2. **Browse recommendations** on the home screen
3. **Search opportunities** in the Opportunities tab
4. **Save an opportunity** to your tracker
5. **View your profile** in the Profile tab

## Next Steps

Once you verify the mobile app works:
1. Add proper app icons to `mobile/assets/`
2. Configure push notifications for production
3. Build production APK/IPA files using EAS Build
4. Submit to App Store and Google Play

## Need Help?

The mobile app is fully functional and ready to test. All screens are implemented and connected to the backend API.
