@echo off
setlocal enabledelayedexpansion

echo ===================================================
echo             Sora Voice Assistant Launcher
echo ===================================================

:: Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python was not found in your PATH.
    echo Please install Python 3.10-3.12 from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)

:: Create virtual environment if it doesn't exist
if not exist "venv\Scripts\activate.bat" (
    echo [INFO] Virtual environment not found. Creating 'venv'...
    python -m venv venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install / verify dependencies
echo [INFO] Verifying requirements...
python -m pip install --quiet --upgrade pip
pip install --quiet -r requirements.txt

:: Launch Sora Voice
echo [INFO] Launching Sora Voice...
python run.py

if %ERRORLEVEL% neq 0 (
    echo [NOTICE] Application closed with return code %ERRORLEVEL%.
    pause
)
