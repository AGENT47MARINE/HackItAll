@echo off
setlocal

:: Set Java 17
set "JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.18.8-hotspot"
set "PATH=%JAVA_HOME%\bin;%PATH%"

:: Set Android SDK
set "ANDROID_HOME=C:\Users\yagye\AppData\Local\Android\Sdk"
set "PATH=%ANDROID_HOME%\platform-tools;%ANDROID_HOME%\tools;%PATH%"

echo.
echo ========================================
echo Java Version:
java -version
echo ========================================
echo.

cd android

echo Cleaning...
call gradlew.bat clean

echo.
echo Building Release APK...
call gradlew.bat assembleRelease --warning-mode all

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo BUILD SUCCESS!
    echo ========================================
    echo.
    echo Installing on emulator...
    adb install -r app\build\outputs\apk\release\app-release.apk
    
    echo.
    echo Launching app...
    adb shell monkey -p com.opportunityplatform.app -c android.intent.category.LAUNCHER 1
    
    echo.
    echo DONE! Check your emulator.
) else (
    echo.
    echo ========================================
    echo BUILD FAILED!
    echo ========================================
    echo Check the error messages above.
)

cd ..
pause
