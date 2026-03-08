@echo off
echo Building Android APK...
echo.

REM Set environment variables
set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.18.8-hotspot

echo ANDROID_HOME: %ANDROID_HOME%
echo JAVA_HOME: %JAVA_HOME%
echo.

REM Generate Android project (answer yes to prompt)
echo Generating Android project files...
echo y | npx expo prebuild --platform android

REM Build the APK
echo.
echo Building APK...
cd android
call gradlew.bat assembleRelease

echo.
echo Done! Your APK is at:
echo android\app\build\outputs\apk\release\app-release.apk
pause
