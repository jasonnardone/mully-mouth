@echo off
REM Launcher script for Mully Mouth system tray application
REM Double-click this file to start the system tray app

echo Starting Mully Mouth Golf Caddy (System Tray)...
echo.
echo The application will appear in your system tray.
echo Look for the GRAY "M" icon in the bottom-right corner.
echo.
echo Right-click the icon and select "Start Monitoring" to begin.
echo.
echo If you see an error about missing API keys, run:
echo   setup_credentials.py
echo.

REM Run the tray application
python -m src.cli.tray_app

REM If there's an error, pause so user can see it
if errorlevel 1 (
    echo.
    echo Error: Failed to start application
    echo.
    echo If API keys are not configured, run: python setup_credentials.py
    echo.
    pause
)
