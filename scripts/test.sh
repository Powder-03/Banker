#!/usr/bin/env bash
# Test runner script for Indian Bank API

set -e

echo "🧪 Indian Bank API Test Suite"
echo "================================"

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ UV is not installed. Please install UV first."
    exit 1
fi

# Install test dependencies
echo "📦 Installing test dependencies..."
uv sync --extra test

# Run different test suites based on argument
case "${1:-all}" in
    "all")
        echo "🔍 Running all tests..."
        uv run pytest -v
        ;;
    "unit")
        echo "🔍 Running unit tests..."
        uv run pytest tests/test_services.py -v
        ;;
    "api")
        echo "🔍 Running API tests..."
        uv run pytest tests/test_banks.py tests/test_branches.py tests/test_api.py -v
        ;;
    "banks")
        echo "🔍 Running bank tests..."
        uv run pytest tests/test_banks.py -v
        ;;
    "branches")
        echo "🔍 Running branch tests..."
        uv run pytest tests/test_branches.py -v
        ;;
    "coverage")
        echo "🔍 Running tests with coverage..."
        uv run pytest --cov=app --cov-report=html --cov-report=term
        echo "📊 Coverage report generated in htmlcov/"
        ;;
    "fast")
        echo "🔍 Running fast tests only..."
        uv run pytest -m "not slow" -v
        ;;
    "watch")
        echo "👀 Running tests in watch mode..."
        echo "Note: This requires pytest-watch. Install with: uv add --dev pytest-watch"
        uv run ptw
        ;;
    *)
        echo "Usage: $0 [all|unit|api|banks|branches|coverage|fast|watch]"
        echo ""
        echo "Test suites:"
        echo "  all       - Run all tests (default)"
        echo "  unit      - Run only service/unit tests"
        echo "  api       - Run only API endpoint tests"
        echo "  banks     - Run only bank-related tests"
        echo "  branches  - Run only branch-related tests"
        echo "  coverage  - Run tests with coverage report"
        echo "  fast      - Run only fast tests (skip slow ones)"
        echo "  watch     - Run tests in watch mode"
        exit 1
        ;;
esac

echo "✅ Tests completed!"
