# 📱 Build Android APK - Real Android App

## Option 1: Build APK with EAS Build (Recommended - Easiest)

This creates a real Android APK file you can install on any Android phone.

### Steps:

1. **Install EAS CLI:**
```bash
npm install -g eas-cli
```

2. **Login to Expo (create free account if needed):**
```bash
eas login
```

3. **Configure the project:**
```bash
cd mobile
eas build:configure
```

4. **Build Android APK:**
```bash
eas build -p android --profile preview
```

This will:
- Upload your code to Expo's servers
- Build a real Android APK
- Give you a download link when done (takes ~10-15 minutes)
- You can install the APK on any Android phone

5. **Download and install:**
- Click the download link from the terminal
- Transfer the APK to your phone
- Install it (you may need to enable "Install from unknown sources")

---

## Option 2: Build Locally with Android Studio (Faster but Complex)

### Prerequisites:
- Android Studio installed
- Android SDK configured
- Java JDK installed

### Steps:

1. **Install Expo CLI globally:**
```bash
npm install -g @expo/cli
```

2. **Create a development build:**
```bash
cd mobile
npx expo prebuild
```

3. **Build the APK:**
```bash
cd android
./gradlew assembleRelease
```

4. **Find your APK:**
The APK will be at: `mobile/android/app/build/outputs/apk/release/app-release.apk`

---

## Option 3: Quick Test Build (Development APK)

This creates a development APK quickly for testing:

```bash
cd mobile
npx expo export:android
```

---

## Recommended: Use EAS Build (Option 1)

It's the easiest and most reliable way. Here's the exact commands:

```bash
# Install EAS CLI
npm install -g eas-cli

# Go to mobile folder
cd mobile

# Login (creates free account)
eas login

# Configure
eas build:configure

# Build APK
eas build -p android --profile preview
```

After 10-15 minutes, you'll get a download link for your APK file!

---

## What About the QR Code?

The QR code is for **development testing only** using the Expo Go app. It's not a real Android app - it's just for quick testing during development.

To get a **real Android app** that you can install on any phone without Expo Go, you need to build an APK using one of the methods above.

---

## Need Help?

The easiest path:
1. Run `npm install -g eas-cli`
2. Run `cd mobile && eas build -p android --profile preview`
3. Wait for the build to complete
4. Download the APK and install on your phone

This gives you a real Android app!
