@echo off
REM Installation script for Mully Mouth Golf Caddy
REM This script creates a virtual environment and installs all dependencies

echo ========================================
echo Mully Mouth Golf Caddy - Installation
echo ========================================
echo.

REM Check if venv already exists
if exist "venv\Scripts\activate.bat" (
    echo Virtual environment already exists.
    echo.
    set /p REINSTALL="Do you want to reinstall? (y/n): "
    if /i "%REINSTALL%"=="y" (
        echo Removing old virtual environment...
        rmdir /s /q venv
    ) else (
        goto :skip_venv
    )
)

REM Check Python version
echo Checking Python version...
python --version 2>nul
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.11 or 3.12 from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

REM Get Python version and check compatibility
for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo Found Python %PYTHON_VERSION%

REM Extract major and minor version
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

REM Check if version is 3.11 or 3.12
if %MAJOR% NEQ 3 (
    goto :version_error
)
if %MINOR% LSS 11 (
    goto :version_error
)
if %MINOR% GTR 13 (
    echo WARNING: Python %PYTHON_VERSION% detected.
    echo Recommended versions are 3.11 or 3.12 for best compatibility.
    echo Some packages like pygame may not work properly.
    echo.
    set /p CONTINUE="Continue anyway? (y/n): "
    if /i not "%CONTINUE%"=="y" exit /b 1
)

echo Python version is compatible.
echo.

:skip_venv
REM Create virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
    echo.
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo.
echo Installing dependencies...
echo This may take a few minutes...
echo.

REM Try installing all dependencies
pip install -r requirements.txt
set INSTALL_STATUS=%errorlevel%

REM If that failed, try installing core packages only (skip pygame and pycaw)
if %INSTALL_STATUS% NEQ 0 (
    echo.
    echo WARNING: Full installation failed. Installing core packages only...
    echo.
    pip install anthropic openai pyyaml pydantic pillow pystray keyring opencv-python mss pygetwindow pynput imagehash numpy
    if errorlevel 1 (
        echo.
        echo ERROR: Failed to install core packages.
        echo Installation cannot continue.
        pause
        exit /b 1
    )
    echo.
    echo Core packages installed successfully.
    echo.
    echo NOTE: Audio features (pygame, pycaw) were skipped due to compatibility issues.
    echo For full audio support, use Python 3.11 or 3.12.
    echo.
)

echo.
echo ========================================
echo Installation Complete!
echo ========================================
echo.
echo Next steps:
echo   1. Run setup_credentials.bat to configure your API keys
echo   2. Double-click mully-mouth.bat to start the application
echo.
pause
exit /b 0

:version_error
echo.
echo ERROR: Python %PYTHON_VERSION% is not compatible.
echo.
echo Mully Mouth requires Python 3.11, 3.12, or 3.13
echo.
echo Please install a compatible version from:
echo https://www.python.org/downloads/
echo.
echo Recommended: Python 3.12.x for best compatibility
echo.
pause
exit /b 1
