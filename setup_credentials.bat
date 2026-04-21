@echo off
REM Wrapper script for credential setup using virtual environment

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo.
    echo Please run install.bat first to set up the environment.
    echo.
    pause
    exit /b 1
)

REM Activate virtual environment and run credential setup
call venv\Scripts\activate.bat
python setup_credentials.py

REM Pause only if there was an error
if errorlevel 1 pause
