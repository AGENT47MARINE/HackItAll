@echo off
echo ========================================
echo Android APK Builder
echo ========================================
echo.

echo Step 1: Installing Java 17 (required for Gradle)
echo Please run this command in PowerShell as Administrator:
echo.
echo     winget install Microsoft.OpenJDK.17
echo.
echo After Java 17 is installed, run this script again.
echo.
pause

REM Check if Java 17 is installed
java -version 2>&1 | findstr /C:"17" >nul
if errorlevel 1 (
    echo Java 17 not found. Please install it first.
    pause
    exit /b 1
)

echo Java 17 found!
echo.

REM Set environment variables
set ANDROID_HOME=%LOCALAPPDATA%\Android\Sdk
for /f "tokens=*" %%i in ('where java') do set JAVA_HOME=%%~dpi..
set JAVA_HOME=%JAVA_HOME:~0,-1%

echo ANDROID_HOME: %ANDROID_HOME%
echo JAVA_HOME: %JAVA_HOME%
echo.

REM Generate Android project
echo Step 2: Generating Android project files...
echo y | npx expo prebuild --platform android

REM Build the APK
echo.
echo Step 3: Building APK (this may take 5-10 minutes)...
cd android
call gradlew.bat assembleRelease

echo.
echo ========================================
echo BUILD COMPLETE!
echo ========================================
echo Your APK is at:
echo %CD%\app\build\outputs\apk\release\app-release.apk
echo.
pause
