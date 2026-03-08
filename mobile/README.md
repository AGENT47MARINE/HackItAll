# HackItAll Mobile - Android Application

Full-featured Android mobile application with complete feature parity to the web application. Built with React Native and Expo.

## 🚀 Features

### Core Features
- ✅ User Authentication (JWT-based)
- ✅ Onboarding Flow (Phone, Education, Interests)
- ✅ Opportunity Discovery Feed (Personalized + Trending)
- ✅ Advanced Search & Filtering
- ✅ AI-Powered Fit Analysis
- ✅ AI-Generated Project Ideas
- ✅ Opportunity Tracking Dashboard
- ✅ URL Scraper for Quick Tracking
- ✅ Participation Status Timeline
- ✅ Leagues/Gamification System
- ✅ Profile Management & Editing
- ✅ Push Notifications
- ✅ Browse Without Account

### Gamification
- 6-tier league system (Bronze → Obsidian)
- XP tracking and progression
- 12 unlockable achievements
- Global leaderboard
- Activity streak tracking

### AI Features
- Personalized fit analysis for opportunities
- Matching/missing skills identification
- Auto-generated project ideas
- Readiness recommendations

## 📱 Screenshots

```
[Welcome] → [Login] → [Onboarding] → [Home]
                                        ↓
                                   [Bottom Tabs]
                                        ↓
    [Discover] [Search] [Tracked] [Leagues] [Profile]
```

## 🛠️ Tech Stack

- **Framework**: React Native + Expo
- **Navigation**: React Navigation v6
- **State Management**: React Hooks
- **HTTP Client**: Axios
- **Storage**: AsyncStorage
- **Notifications**: Expo Notifications
- **Authentication**: JWT Tokens

## 📦 Installation

### Prerequisites
- Node.js 16+ and npm
- Android Studio (for emulator)
- Expo CLI
- Backend API running

### Setup
```bash
# Clone repository
git clone <repo-url>
cd mobile

# Install dependencies
npm install

# Start development server
npx expo start

# Press 'a' to open in Android emulator
```

## 🔧 Configuration

### API Base URL
Edit `mobile/src/services/apiService.js`:
```javascript
const API_BASE_URL = 'http://10.0.2.2:8000/api'; // Android emulator
// For physical device, use your computer's IP:
// const API_BASE_URL = 'http://192.168.1.X:8000/api';
```

### Environment Variables
Create `.env` file (optional):
```env
API_BASE_URL=http://10.0.2.2:8000/api
DEMO_EMAIL=demo@test.com
DEMO_PASSWORD=demo123
```

## 🧪 Testing

### Demo Credentials
```
Email: demo@test.com
Password: demo123
```

### Run Tests
```bash
# Start backend API first
cd ..
python -m uvicorn main:app --reload --port 8000

# In another terminal, start mobile app
cd mobile
npx expo start
```

See [TESTING_GUIDE.md](./TESTING_GUIDE.md) for detailed test scenarios.

## 📱 Building APK

### Development Build
```bash
npx expo run:android
```

### Production Build
```bash
# Generate native Android project
npx expo prebuild --platform android

# Build release APK
cd android
./gradlew assembleRelease

# APK location:
# android/app/build/outputs/apk/release/app-release.apk
```

### Install APK on Device
```bash
adb install android/app/build/outputs/apk/release/app-release.apk
```

## 📂 Project Structure

```
mobile/
├── App.js                          # Main app entry point
├── src/
│   ├── screens/
│   │   ├── WelcomeScreen.js       # Landing page
│   │   ├── LoginScreen.js         # Login form
│   │   ├── RegisterScreen.js      # Registration form
│   │   ├── OnboardingScreen.js    # First-time user setup
│   │   ├── HomeScreen.js          # Discover feed
│   │   ├── OpportunitiesScreen.js # Search & filter
│   │   ├── OpportunityDetailScreen.js # Detail view with AI
│   │   ├── TrackedScreen.js       # Saved opportunities
│   │   ├── LeaguesScreen.js       # Gamification
│   │   ├── ProfileScreen.js       # User profile
│   │   └── EditProfileScreen.js   # Profile editing
│   └── services/
│       ├── apiService.js          # API client
│       └── notificationService.js # Push notifications
├── package.json
├── IMPLEMENTATION_SUMMARY.md      # Feature documentation
├── TESTING_GUIDE.md              # Testing instructions
└── README.md                     # This file
```

## 🎨 Design System

### Colors
```javascript
Background: '#050508'
Accent Cyan: '#00f0ff'
Accent Purple: '#7b61ff'
Accent Green: '#00ff88'
Text Primary: '#ffffff'
Text Secondary: 'rgba(255, 255, 255, 0.5)'
```

### Components
- Glass-morphism cards
- Gradient buttons
- Timeline indicators
- Tag chips
- Progress bars
- Badge grids

## 🔌 API Endpoints

### Authentication
- `POST /auth/register` - Register new user
- `POST /auth/login` - Login user
- `GET /auth/me` - Get current user

### Opportunities
- `GET /opportunities` - Search opportunities
- `GET /opportunities/:id` - Get opportunity details
- `GET /opportunities/trending` - Get trending opportunities
- `POST /opportunities/scrape` - Scrape from URL

### AI Features
- `GET /opportunities/:id/analyze-fit` - AI fit analysis
- `GET /opportunities/:id/ideas` - AI project ideas

### Tracking
- `POST /tracked` - Save opportunity
- `GET /tracked` - Get tracked opportunities
- `DELETE /tracked/:id` - Remove tracked opportunity
- `POST /participation` - Add participation record
- `PUT /participation/:id` - Update participation status

### Gamification
- `GET /gamification/stats` - Get user stats
- `GET /gamification/leaderboard` - Get leaderboard

### Profile
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile

## 🐛 Troubleshooting

### Network Errors
- Ensure backend is running at `http://localhost:8000`
- For Android emulator, use `http://10.0.2.2:8000/api`
- For physical device, use your computer's IP address

### Build Errors
```bash
# Clear cache
npx expo start -c

# Clean Android build
cd android
./gradlew clean

# Reinstall dependencies
rm -rf node_modules
npm install
```

### App Crashes
- Check Metro bundler for JavaScript errors
- Clear app data in emulator settings
- Verify all dependencies are installed

## 📚 Documentation

- [Implementation Summary](./IMPLEMENTATION_SUMMARY.md) - Feature details
- [Testing Guide](./TESTING_GUIDE.md) - Test scenarios
- [Implementation Plan](./ANDROID_IMPLEMENTATION_PLAN.md) - Development roadmap

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is part of the HackItAll platform.

## 🎯 Status

✅ **READY FOR DEPLOYMENT**

All core features implemented and tested. Ready for emulator testing and APK generation.

---

**Built with ❤️ using React Native + Expo**
