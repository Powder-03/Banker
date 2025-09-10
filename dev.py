#!/usr/bin/env python3
"""
Development startup script for Indian Bank API
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed")
        print(f"   Error: {e.stderr.strip()}")
        return False

def check_uv_installed():
    """Check if UV is installed"""
    try:
        subprocess.run(["uv", "--version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    """Main startup script"""
    print("=" * 60)
    print("🏦 Indian Bank API - Development Setup")
    print("=" * 60)
    
    # Check if UV is installed
    if not check_uv_installed():
        print("❌ UV is not installed. Please install it first:")
        print("   Windows: powershell -c \"irm https://astral.sh/uv/install.ps1 | iex\"")
        print("   macOS/Linux: curl -LsSf https://astral.sh/uv/install.sh | sh")
        sys.exit(1)
    
    print("✅ UV is installed")
    
    # Install dependencies
    if not run_command("uv sync", "Installing dependencies"):
        sys.exit(1)
    
    # Check if database exists
    db_path = Path("indian_banks.db")
    if not db_path.exists():
        print("📦 Database not found. Loading data...")
        if not run_command("uv run python scripts/load_data.py", "Loading database"):
            sys.exit(1)
    else:
        print("✅ Database already exists")
    
    print("\n" + "=" * 60)
    print("🚀 Starting API Server")
    print("=" * 60)
    print("📝 API Documentation: http://localhost:8000/docs")
    print("🔗 Health Check: http://localhost:8000/health")
    print("📊 Database Stats: http://localhost:8000/stats")
    print("🛑 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    # Start the server
    try:
        subprocess.run([
            "uv", "run", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ], check=True)
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Server failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
