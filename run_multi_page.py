#!/usr/bin/env python3
"""
Launch script for the Multi-page Air Quality Dashboard
"""

import subprocess
import sys
import os

def check_dependencies():
    """Check if required packages are installed"""
    required_packages = [
        'streamlit',
        'plotly',
        'pandas',
        'numpy',
        'boto3'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print("❌ Missing required packages:")
        for package in missing_packages:
            print(f"   - {package}")
        print("\n📦 Install them with:")
        print("   pip install streamlit plotly pandas numpy boto3")
        return False
    
    return True

def check_database():
    """Check if database exists and has data"""
    if not os.path.exists("air_quality.db"):
        print("❌ Database not found!")
        print("📊 Please run the S3 processor first:")
        print("   python3 process_s3_to_db.py --city Barcelona --limit 100")
        return False
    
    # Check if database has data
    try:
        from database_manager import AirQualityDatabase
        db = AirQualityDatabase("air_quality.db")
        stats = db.get_database_stats()
        
        if stats['total_records'] == 0:
            print("❌ Database is empty!")
            print("📊 Please run the S3 processor first:")
            print("   python3 process_s3_to_db.py --city Barcelona --limit 100")
            return False
        
        print(f"✅ Database found with {stats['total_records']} records")
        print(f"   Cities available: {list(stats['city_counts'].keys())}")
        return True
        
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

def launch_multi_page_dashboard():
    """Launch the multi-page Streamlit dashboard"""
    print("🚀 Launching Multi-page Air Quality Dashboard...")
    print("🌐 The dashboard will open in your default browser")
    print("📊 Use Ctrl+C to stop the dashboard")
    print("-" * 50)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "multi_page_app.py",
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 Dashboard stopped by user")
    except Exception as e:
        print(f"❌ Error launching dashboard: {e}")

def main():
    print("🌍 Multi-page Air Quality Dashboard Launcher")
    print("=" * 50)
    
    # Check dependencies
    print("🔍 Checking dependencies...")
    if not check_dependencies():
        return
    
    # Check database
    print("🔍 Checking database...")
    if not check_database():
        return
    
    print("✅ All checks passed!")
    print()
    
    # Launch dashboard
    launch_multi_page_dashboard()

if __name__ == "__main__":
    main()
