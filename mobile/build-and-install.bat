@echo off
echo Setting Java 17...
set JAVA_HOME=C:\Program Files\Microsoft\jdk-17.0.18.8-hotspot
set PATH=%JAVA_HOME%\bin;%PATH%

echo Building APK...
cd android
call gradlew assembleRelease
cd ..

echo Installing on device...
set ANDROID_HOME=C:\Users\yagye\AppData\Local\Android\Sdk
"%ANDROID_HOME%\platform-tools\adb.exe" install -r android\app\build\outputs\apk\release\app-release.apk

echo Launching app...
"%ANDROID_HOME%\platform-tools\adb.exe" shell monkey -p com.opportunityplatform.app -c android.intent.category.LAUNCHER 1

echo Done!
pause
