# Opportunity Access Platform - Mobile App

React Native mobile application for iOS and Android built with Expo.

## Features

- User authentication (register/login)
- Personalized opportunity recommendations
- Search and filter opportunities
- Save opportunities to tracker
- Track application deadlines
- Push notifications for deadline reminders
- User profile management

## Prerequisites

- Node.js (v14 or higher)
- npm or yarn
- Expo CLI (`npm install -g expo-cli`)
- iOS Simulator (for Mac) or Android Studio (for Android development)
- Physical device with Expo Go app (optional)

## Installation

1. Install dependencies:
```bash
cd mobile
npm install
```

2. Create assets folder and add placeholder images:
```bash
mkdir -p assets
```

You'll need to add the following image files to the `assets` folder:
- `icon.png` (1024x1024) - App icon
- `splash.png` (1242x2436) - Splash screen
- `adaptive-icon.png` (1024x1024) - Android adaptive icon
- `favicon.png` (48x48) - Web favicon
- `notification-icon.png` (96x96) - Notification icon

## Running the App

1. Make sure the backend API is running at `http://localhost:8000`

2. Start the Expo development server:
```bash
npm start
```

3. Run on specific platform:
```bash
npm run ios      # Run on iOS simulator
npm run android  # Run on Android emulator
npm run web      # Run in web browser
```

4. Or scan the QR code with Expo Go app on your physical device

## API Configuration

The app connects to the backend API at `http://localhost:8000/api` by default.

To change the API URL, edit `src/services/apiService.js`:
```javascript
const API_BASE_URL = 'YOUR_API_URL';
```

For physical device testing, replace `localhost` with your computer's local IP address.

## Project Structure

```
mobile/
├── App.js                          # Main app component with navigation
├── app.json                        # Expo configuration
├── package.json                    # Dependencies
├── assets/                         # Images and icons
├── src/
│   ├── components/
│   │   └── OpportunityCard.js     # Reusable opportunity card component
│   ├── screens/
│   │   ├── LoginScreen.js         # Login screen
│   │   ├── RegisterScreen.js      # Registration screen
│   │   ├── HomeScreen.js          # Home with recommendations
│   │   ├── OpportunitiesScreen.js # Search opportunities
│   │   ├── OpportunityDetailScreen.js # Opportunity details
│   │   ├── TrackedScreen.js       # Saved opportunities
│   │   └── ProfileScreen.js       # User profile
│   └── services/
│       ├── apiService.js          # API client
│       └── notificationService.js # Push notifications
```

## Push Notifications

Push notifications are configured for both iOS and Android. To enable them:

1. For development, notifications work in the Expo Go app
2. For production, you'll need to:
   - Set up Firebase Cloud Messaging (FCM) for Android
   - Set up Apple Push Notification service (APNs) for iOS
   - Configure credentials in Expo

## Building for Production

1. Install EAS CLI:
```bash
npm install -g eas-cli
```

2. Configure EAS:
```bash
eas build:configure
```

3. Build for iOS:
```bash
eas build --platform ios
```

4. Build for Android:
```bash
eas build --platform android
```

## Troubleshooting

### Cannot connect to API
- Make sure the backend is running
- For physical devices, use your computer's IP instead of localhost
- Check that CORS is enabled in the backend

### Push notifications not working
- Ensure you're using a physical device (notifications don't work in simulators)
- Check notification permissions in device settings
- Verify Expo push token is being generated

### Build errors
- Clear cache: `expo start -c`
- Reinstall dependencies: `rm -rf node_modules && npm install`
- Update Expo: `expo upgrade`

## License

MIT
