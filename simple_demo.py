#!/usr/bin/env python3
"""
Simple demo script to show city comparison features (no pandas required)
"""

import random

def create_demo_data():
    """Create demo data for city comparison"""
    
    # Spanish cities
    cities = ["Barcelona", "Madrid", "Valencia", "Granada", "Sevilla", "Bilbao"]
    
    # Create demo air quality data
    demo_data = {}
    
    for city in cities:
        # Generate realistic air quality data
        random.seed(hash(city) % 2**32)  # Consistent random data per city
        
        # Base values (realistic for Spanish cities)
        base_aqi = random.uniform(40, 80)    # AQI between 40-80
        base_pm25 = random.uniform(15, 30)   # PM2.5 between 15-30
        base_pm10 = random.uniform(20, 40)   # PM10 between 20-40
        base_no2 = random.uniform(15, 35)    # NO2 between 15-35
        base_o3 = random.uniform(25, 45)     # O3 between 25-45
        
        # Calculate composite score
        score = base_aqi * 0.4 + base_pm25 * 0.2 + base_pm10 * 0.2 + base_no2 * 0.1 + base_o3 * 0.1
        
        demo_data[city] = {
            'score': round(score, 1),
            'aqi': round(base_aqi, 1),
            'pm25': round(base_pm25, 1),
            'pm10': round(base_pm10, 1),
            'no2': round(base_no2, 1),
            'o3': round(base_o3, 1),
            'data_points': random.randint(100, 500)
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
    
    # Print comparison table
    print(f"{'City':<12} {'Score':<6} {'AQI':<6} {'PM2.5':<6} {'PM10':<6} {'NO2':<6} {'O3':<6} {'Data':<6}")
    print("-" * 60)
    
    for city, data in sorted_cities:
        print(f"{city:<12} {data['score']:<6.1f} {data['aqi']:<6.1f} {data['pm25']:<6.1f} {data['pm10']:<6.1f} {data['no2']:<6.1f} {data['o3']:<6.1f} {data['data_points']:<6}")
    
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
