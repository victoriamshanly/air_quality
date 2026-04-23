#!/usr/bin/env python3
"""
Simple City Comparison Launcher
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = ['streamlit', 'plotly', 'pandas', 'numpy', 'boto3']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def check_database():
    """Check if database exists and has data"""
    try:
        from database_manager import AirQualityDatabase
        db = AirQualityDatabase("air_quality.db")
        stats = db.get_database_stats()
        
        if stats['total_records'] == 0:
            return False, "Database is empty"
        
        return True, f"Database found with {stats['total_records']} records"
    except Exception as e:
        return False, f"Database error: {e}"

def main():
    print("🏙️ Simple City Comparison Launcher")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    missing = check_dependencies()
    if missing:
        print(f"❌ Missing packages: {', '.join(missing)}")
        print("📦 Install them with:")
        print(f"   pip install {' '.join(missing)}")
        return
    
    print("✅ All dependencies found")
    
    # Check database
    print("🔍 Checking database...")
    db_ok, db_msg = check_database()
    if not db_ok:
        print(f"❌ {db_msg}")
        return
    
    print(f"✅ {db_msg}")
    
    print("\n🚀 Launching Simple City Comparison...")
    print("🌐 The app will open in your default browser")
    print("📊 Use Ctrl+C to stop the app")
    print("-" * 50)
    
    # Launch Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            "simple_city_comparison.py",
            "--server.port", "8502",
            "--server.headless", "true"
        ])
    except KeyboardInterrupt:
        print("\n👋 App stopped by user")
    except Exception as e:
        print(f"❌ Error launching app: {e}")

if __name__ == "__main__":
    main()
