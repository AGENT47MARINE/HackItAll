# Download and install Java 17 (required for Gradle)
Write-Host "Downloading Java 17..." -ForegroundColor Green

$javaUrl = "https://download.oracle.com/java/17/latest/jdk-17_windows-x64_bin.exe"
$installerPath = "$env:TEMP\jdk-17-installer.exe"

# Download
Invoke-WebRequest -Uri $javaUrl -OutFile $installerPath

Write-Host "Installing Java 17..." -ForegroundColor Green
Write-Host "Please follow the installation wizard" -ForegroundColor Yellow

# Run installer
Start-Process -FilePath $installerPath -Wait

Write-Host "Java 17 installed!" -ForegroundColor Green
Write-Host "Please run the build script again" -ForegroundColor Yellow
