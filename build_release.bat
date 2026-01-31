@echo off
REM CC-Packer v2.0 Release Build Script
echo ========================================
echo CC-Packer v2.0 Release Build
echo ========================================
echo.

REM Set version
set VERSION=2.0
set RELEASE_DIR=release\v%VERSION%

REM Check for required files
echo [0/5] Checking required files...
if not exist "bsarch.exe" (
    echo ERROR: bsarch.exe not found in project directory!
    echo Please place bsarch.exe in the same directory as this script.
    pause
    exit /b 1
)
if not exist "BSARCH_LICENSE.txt" (
    echo ERROR: BSARCH_LICENSE.txt not found in project directory!
    pause
    exit /b 1
)
echo Found bsarch.exe and BSARCH_LICENSE.txt.

REM Clean previous builds
echo.
echo [1/5] Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist %RELEASE_DIR% rmdir /s /q %RELEASE_DIR%
mkdir %RELEASE_DIR%

REM Build the executable
echo.
echo [2/5] Building CC-Packer executable...
pyinstaller --noconfirm CCPacker.spec
if errorlevel 1 (
    echo ERROR: Build failed!
    pause
    exit /b 1
)

REM Create release package
echo.
echo [3/5] Creating release package...
mkdir %RELEASE_DIR%\CC-Packer_v%VERSION%
copy dist\CCPacker.exe %RELEASE_DIR%\CC-Packer_v%VERSION%\
copy bsarch.exe %RELEASE_DIR%\CC-Packer_v%VERSION%\
copy README.md %RELEASE_DIR%\CC-Packer_v%VERSION%\
copy LICENSE %RELEASE_DIR%\CC-Packer_v%VERSION%\
copy BSARCH_LICENSE.txt %RELEASE_DIR%\CC-Packer_v%VERSION%\
copy CHANGELOG.md %RELEASE_DIR%\CC-Packer_v%VERSION%\

REM Create source package
echo.
echo [4/5] Creating source code package...
mkdir %RELEASE_DIR%\CC-Packer_v%VERSION%_Source
copy main.py %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\
copy merger.py %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\
copy requirements.txt %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\
copy CCPacker.spec %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\
copy build_exe.bat %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\
copy README.md %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\
copy LICENSE %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\
copy BSARCH_LICENSE.txt %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\
copy CHANGELOG.md %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\
copy bsarch.exe %RELEASE_DIR%\CC-Packer_v%VERSION%_Source\

REM Create zip archives
echo.
echo [5/5] Creating zip archives...
cd %RELEASE_DIR%
powershell Compress-Archive -Path CC-Packer_v%VERSION% -DestinationPath CC-Packer_v%VERSION%_Windows.zip -Force
powershell Compress-Archive -Path CC-Packer_v%VERSION%_Source -DestinationPath CC-Packer_v%VERSION%_Source.zip -Force
cd ..\..

echo.
echo ========================================
echo Build Complete!
echo ========================================
echo Binary package: %RELEASE_DIR%\CC-Packer_v%VERSION%_Windows.zip
echo Source package: %RELEASE_DIR%\CC-Packer_v%VERSION%_Source.zip
echo.
pause
