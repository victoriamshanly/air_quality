#!/usr/bin/env python3
"""
Test script for Streamlit dashboard components
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required packages can be imported"""
    print("🔍 Testing imports...")
    
    try:
        import streamlit as st
        print("✅ Streamlit imported successfully")
    except ImportError as e:
        print(f"❌ Streamlit import failed: {e}")
        return False
    
    try:
        import plotly.express as px
        import plotly.graph_objects as go
        print("✅ Plotly imported successfully")
    except ImportError as e:
        print(f"❌ Plotly import failed: {e}")
        return False
    
    try:
        import pandas as pd
        import numpy as np
        print("✅ Pandas and NumPy imported successfully")
    except ImportError as e:
        print(f"❌ Pandas/NumPy import failed: {e}")
        return False
    
    try:
        from database_manager import AirQualityDatabase
        print("✅ Database manager imported successfully")
    except ImportError as e:
        print(f"❌ Database manager import failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection and data availability"""
    print("\n🔍 Testing database connection...")
    
    try:
        db = AirQualityDatabase("air_quality.db")
        stats = db.get_database_stats()
        
        print(f"✅ Database connected successfully")
        print(f"   Total records: {stats['total_records']}")
        print(f"   Cities available: {list(stats['city_counts'].keys())}")
        
        if stats['total_records'] == 0:
            print("⚠️  Database is empty - you may need to process S3 data first")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_data_loading():
    """Test data loading functionality"""
    print("\n🔍 Testing data loading...")
    
    try:
        from database_manager import AirQualityDatabase
        
        db = AirQualityDatabase("air_quality.db")
        df = db.get_data(city="Barcelona", days=7, limit=10)
        
        if df.empty:
            print("⚠️  No data loaded - database may be empty")
            return False
        
        print(f"✅ Data loaded successfully")
        print(f"   Records: {len(df)}")
        print(f"   Columns: {list(df.columns)}")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        return True
        
    except Exception as e:
        print(f"❌ Data loading failed: {e}")
        return False

def test_chart_creation():
    """Test chart creation functions"""
    print("\n🔍 Testing chart creation...")
    
    try:
        # Create sample data
        dates = pd.date_range(start='2024-01-01', periods=24, freq='H')
        sample_data = pd.DataFrame({
            'timestamp': dates,
            'aqi': np.random.randint(20, 150, 24),
            'pm25': np.random.randint(10, 80, 24),
            'pm10': np.random.randint(15, 100, 24),
            'no2': np.random.randint(5, 50, 24),
            'o3': np.random.randint(10, 60, 24)
        })
        
        # Test if we can import chart functions
        from streamlit_app import create_aqi_gauge, create_time_series_chart, create_daily_patterns_chart
        
        # Test gauge creation
        gauge = create_aqi_gauge(75)
        print("✅ AQI gauge created successfully")
        
        # Test time series chart
        ts_chart = create_time_series_chart(sample_data)
        print("✅ Time series chart created successfully")
        
        # Test daily patterns chart
        daily_chart = create_daily_patterns_chart(sample_data)
        print("✅ Daily patterns chart created successfully")
        
        return True
        
    except Exception as e:
        print(f"❌ Chart creation failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🌍 Streamlit Dashboard Test Suite")
    print("=" * 40)
    
    tests = [
        ("Import Test", test_imports),
        ("Database Connection", test_database_connection),
        ("Data Loading", test_data_loading),
        ("Chart Creation", test_chart_creation)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 40)
    print("📊 TEST SUMMARY")
    print("=" * 40)
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! Dashboard should work correctly.")
        print("🚀 You can now run: python run_dashboard.py")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
        print("💡 Common solutions:")
        print("   - Install missing packages: pip install streamlit plotly pandas numpy boto3")
        print("   - Process S3 data: python process_s3_to_db.py --city Barcelona --limit 100")

if __name__ == "__main__":
    main()
