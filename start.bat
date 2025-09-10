@echo off
echo ====================================================
echo Indian Bank API - Quick Start
echo ====================================================

REM Check if UV is installed
uv --version >nul 2>&1
if %errorlevel% neq 0 (
    echo UV is not installed. Installing UV...
    powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
    if %errorlevel% neq 0 (
        echo Failed to install UV. Please install manually.
        pause
        exit /b 1
    )
)

echo Installing dependencies...
uv sync
if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo Checking database...
if not exist "indian_banks.db" (
    echo Loading data into database...
    uv run python scripts/load_data.py
    if %errorlevel% neq 0 (
        echo Failed to load data.
        pause
        exit /b 1
    )
)

echo ====================================================
echo Starting API Server...
echo ====================================================
echo API Documentation: http://localhost:8000/docs
echo Health Check: http://localhost:8000/health
echo Database Stats: http://localhost:8000/stats
echo Press Ctrl+C to stop the server
echo ====================================================

uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

pause
