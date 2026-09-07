@echo off
setlocal enabledelayedexpansion

title Sora Voice Assistant Launcher

echo ===================================================
echo               Sora Voice Assistant
echo ===================================================
echo.

:: Check for Python
where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [ERROR] Python was not found in your PATH!
    echo Please install Python 3.10+ from https://python.org and add it to PATH.
    pause
    exit /b 1
)

:: Check for virtual environment in jarvis or .venv
set "VENV_DIR="
if exist "jarvis\Scripts\python.exe" (
    set "VENV_DIR=jarvis"
) else if exist ".venv\Scripts\python.exe" (
    set "VENV_DIR=.venv"
) else (
    echo [INFO] Creating Python virtual environment in .venv...
    python -m venv .venv
    set "VENV_DIR=.venv"
)

:: Activate virtual environment
call "%VENV_DIR%\Scripts\activate.bat"

:: Check if all runtime requirements are installed. Voice imports are loaded
:: during startup, so checking only the GUI packages makes the app appear to
:: launch while microphone support fails with a missing-module error.
python -c "import PyQt6, qasync, loguru, pydantic, dotenv, numpy, sounddevice, soundfile, speech_recognition, edge_tts, pyttsx3, httpx" >nul 2>nul
if %errorlevel% neq 0 (
    echo [INFO] Installing required dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo [ERROR] Failed to install dependencies.
        pause
        exit /b 1
    )
)

echo [INFO] Launching Sora Voice Interface...
python run.py

if %errorlevel% neq 0 (
    echo.
    echo [INFO] Application exited with code %errorlevel%.
    pause
)
