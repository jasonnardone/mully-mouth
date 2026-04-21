@echo off
REM Launcher script for Mully Mouth system tray application
REM Double-click this file to start the system tray app

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo.
    echo Please run install.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

echo Starting Mully Mouth Golf Caddy (System Tray)...
echo.
echo The application will appear in your system tray.
echo Look for the GRAY "M" icon in the bottom-right corner.
echo.
echo Right-click the icon and select "Start Monitoring" to begin.
echo.
echo If you see an error about missing API keys, run:
echo   setup_credentials.bat
echo.

REM Run the tray application
python -m src.cli.tray_app

REM If there's an error, pause so user can see it
if errorlevel 1 (
    echo.
    echo Error: Failed to start application
    echo.
    echo If API keys are not configured, run: setup_credentials.bat
    echo.
    pause
)
