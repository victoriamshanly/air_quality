#!/usr/bin/env python3
"""
Test script for the database system
"""

from database_manager import AirQualityDatabase
from plotData import database_quick_analysis, database_latest_analysis
import os

def test_database():
    """Test the database functionality"""
    
    # Test database initialization
    print("=== Testing Database Initialization ===")
    db = AirQualityDatabase("test_air_quality.db")
    
    # Test database stats
    print("\n=== Testing Database Stats ===")
    stats = db.get_database_stats()
    print(f"Database stats: {stats}")
    
    # Test data retrieval (will be empty initially)
    print("\n=== Testing Data Retrieval ===")
    df = db.get_data(city="Barcelona", days=7, limit=10)
    print(f"Retrieved {len(df)} records")
    
    if not df.empty:
        print("Sample data:")
        print(df[['timestamp', 'aqi', 'dominant_pollutant']].head())
    else:
        print("No data found (expected if database is empty)")
    
    # Test plotting functions
    print("\n=== Testing Plotting Functions ===")
    try:
        df = database_quick_analysis(db_path="test_air_quality.db", city="Barcelona", days=7)
        if df is not None and not df.empty:
            print("Plotting test successful!")
        else:
            print("No data to plot (expected if database is empty)")
    except Exception as e:
        print(f"Plotting test failed: {e}")
    
    # Clean up test database
    if os.path.exists("test_air_quality.db"):
        os.remove("test_air_quality.db")
        print("\nTest database cleaned up")

if __name__ == "__main__":
    test_database()
