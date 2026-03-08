# Building Mobile App in Android Studio

## Steps to Build and Install:

1. **Android Studio is now opening** with the project at:
   `C:\Users\yagye\OneDrive\Desktop\HackItAll\mobile\android`

2. **Wait for Gradle Sync** (bottom right corner will show progress)
   - This may take 2-5 minutes on first load
   - Android Studio will download dependencies automatically

3. **Set Java Version** (if needed):
   - File → Settings → Build, Execution, Deployment → Build Tools → Gradle
   - Set "Gradle JDK" to: Java 17 (Microsoft OpenJDK 17.0.18)

4. **Build the APK**:
   - Click: Build → Build Bundle(s) / APK(s) → Build APK(s)
   - OR use menu: Build → Generate Signed Bundle / APK → APK → Next → release → Finish

5. **Install on Emulator**:
   - Make sure emulator is running (you have Pixel_5 running on emulator-5554)
   - After build completes, click "locate" in the notification
   - Or find APK at: `mobile/android/app/build/outputs/apk/release/app-release.apk`
   - Drag and drop APK onto emulator window to install

6. **Alternative - Run Directly**:
   - Select "app" from the configuration dropdown (top toolbar)
   - Click the green "Run" button (▶️)
   - Select your emulator from the device list

## What's New in the UI:

✨ **Welcome Screen** - Beautiful landing page before login
- Cyberpunk dark theme matching website
- Cyan/purple gradient buttons
- Stats display
- Option to browse without account

🎨 **Updated Theme**:
- Dark backgrounds: #050508, #0a0a12
- Accent colors: #00f0ff (cyan), #7b61ff (purple), #00ff88 (green)
- Glass-morphism effects
- Modern card designs

📱 **Improved Screens**:
- Login/Register with gradient buttons
- Home screen with trending opportunities
- Color-coded type badges
- Rank badges for trending items

## Troubleshooting:

If build fails:
1. File → Invalidate Caches → Invalidate and Restart
2. Build → Clean Project
3. Build → Rebuild Project
4. Try building again

If Java version error:
1. Ensure Java 17 is selected in Gradle settings
2. Check gradle.properties has correct JAVA_HOME path
