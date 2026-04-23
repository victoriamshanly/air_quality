#!/usr/bin/env python3
"""
Demo script to show city comparison features
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def create_demo_data():
    """Create demo data for city comparison"""
    
    # Spanish cities
    cities = ["Barcelona", "Madrid", "Valencia", "Granada", "Sevilla", "Bilbao"]
    
    # Create demo air quality data
    demo_data = {}
    
    for city in cities:
        # Generate realistic air quality data
        np.random.seed(hash(city) % 2**32)  # Consistent random data per city
        
        # Base values (realistic for Spanish cities)
        base_aqi = np.random.normal(60, 15)  # Average AQI around 60
        base_pm25 = np.random.normal(20, 5)  # PM2.5 around 20
        base_pm10 = np.random.normal(30, 8)  # PM10 around 30
        base_no2 = np.random.normal(25, 8)   # NO2 around 25
        base_o3 = np.random.normal(35, 10)   # O3 around 35
        
        # Ensure values are positive and realistic
        demo_data[city] = {
            'score': max(base_aqi * 0.4 + base_pm25 * 0.2 + base_pm10 * 0.2 + base_no2 * 0.1 + base_o3 * 0.1, 10),
            'aqi': max(base_aqi, 10),
            'pm25': max(base_pm25, 5),
            'pm10': max(base_pm10, 10),
            'no2': max(base_no2, 5),
            'o3': max(base_o3, 10),
            'data_points': np.random.randint(100, 500)
        }
    
    return demo_data

def print_demo_comparison():
    """Print demo city comparison"""
    
    print("🏙️ City Comparison Demo")
    print("=" * 50)
    
    demo_data = create_demo_data()
    
    # Sort cities by score (lower is better)
    sorted_cities = sorted(demo_data.items(), key=lambda x: x[1]['score'])
    
    print("📊 City Rankings (Lower score = Better air quality):")
    print("-" * 50)
    
    for i, (city, data) in enumerate(sorted_cities, 1):
        print(f"{i:2d}. {city:12s} | Score: {data['score']:5.1f} | AQI: {data['aqi']:5.1f} | PM2.5: {data['pm25']:4.1f}")
    
    print("\n🎯 Detailed Comparison:")
    print("-" * 50)
    
    # Create comparison table
    comparison_df = pd.DataFrame([
        {
            'City': city,
            'Overall Score': f"{data['score']:.1f}",
            'AQI': f"{data['aqi']:.1f}",
            'PM2.5': f"{data['pm25']:.1f}",
            'PM10': f"{data['pm10']:.1f}",
            'NO2': f"{data['no2']:.1f}",
            'O3': f"{data['o3']:.1f}",
            'Data Points': data['data_points']
        }
        for city, data in demo_data.items()
    ])
    
    # Sort by overall score
    comparison_df['Overall Score'] = pd.to_numeric(comparison_df['Overall Score'])
    comparison_df = comparison_df.sort_values('Overall Score')
    comparison_df['Overall Score'] = comparison_df['Overall Score'].astype(str)
    
    print(comparison_df.to_string(index=False))
    
    print("\n🏆 Best Cities for Air Quality:")
    print("-" * 30)
    for i, (city, data) in enumerate(sorted_cities[:3], 1):
        print(f"{i}. {city} - Score: {data['score']:.1f}")
    
    print("\n⚠️ Cities Needing Attention:")
    print("-" * 30)
    for city, data in sorted_cities[-2:]:
        print(f"• {city} - Score: {data['score']:.1f} (AQI: {data['aqi']:.1f})")
    
    print("\n💡 Features of the City Comparison Dashboard:")
    print("-" * 50)
    print("🎯 Radar Charts - Visual comparison across all pollutants")
    print("📊 Bar Charts - Detailed metric-by-metric comparison")
    print("🏆 Rankings - Overall air quality scoring system")
    print("📈 Interactive Charts - Zoom, hover, and filter capabilities")
    print("🎨 Beautiful Design - Modern gradient styling and animations")
    print("📱 Responsive - Works on desktop, tablet, and mobile")
    
    print("\n🚀 To see the full interactive dashboard:")
    print("   python3 run_multi_page.py")
    print("   Then select 'City Comparison' from the main menu")

if __name__ == "__main__":
    print_demo_comparison()
