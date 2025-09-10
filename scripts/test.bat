@echo off
REM Test runner script for Indian Bank API (Windows)

echo 🧪 Indian Bank API Test Suite
echo ================================

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo ❌ UV is not installed. Please install UV first.
    exit /b 1
)

REM Install test dependencies
echo 📦 Installing test dependencies...
uv sync --extra test

REM Set default argument to "all" if none provided
set TEST_TYPE=%1
if "%TEST_TYPE%"=="" set TEST_TYPE=all

if "%TEST_TYPE%"=="all" (
    echo 🔍 Running all tests...
    uv run pytest -v
) else if "%TEST_TYPE%"=="unit" (
    echo 🔍 Running unit tests...
    uv run pytest tests/test_services.py -v
) else if "%TEST_TYPE%"=="api" (
    echo 🔍 Running API tests...
    uv run pytest tests/test_banks.py tests/test_branches.py tests/test_api.py -v
) else if "%TEST_TYPE%"=="banks" (
    echo 🔍 Running bank tests...
    uv run pytest tests/test_banks.py -v
) else if "%TEST_TYPE%"=="branches" (
    echo 🔍 Running branch tests...
    uv run pytest tests/test_branches.py -v
) else if "%TEST_TYPE%"=="coverage" (
    echo 🔍 Running tests with coverage...
    uv run pytest --cov=app --cov-report=html --cov-report=term
    echo 📊 Coverage report generated in htmlcov/
) else if "%TEST_TYPE%"=="fast" (
    echo 🔍 Running fast tests only...
    uv run pytest -m "not slow" -v
) else (
    echo Usage: %0 [all^|unit^|api^|banks^|branches^|coverage^|fast]
    echo.
    echo Test suites:
    echo   all       - Run all tests ^(default^)
    echo   unit      - Run only service/unit tests
    echo   api       - Run only API endpoint tests
    echo   banks     - Run only bank-related tests
    echo   branches  - Run only branch-related tests
    echo   coverage  - Run tests with coverage report
    echo   fast      - Run only fast tests ^(skip slow ones^)
    exit /b 1
)

echo ✅ Tests completed!
