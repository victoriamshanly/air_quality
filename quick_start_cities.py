#!/usr/bin/env python3
"""
Quick start script for city comparison - works without additional packages
"""

import os
import sys

def check_files():
    """Check if all required files exist"""
    required_files = [
        "database_manager.py",
        "streamlit_app.py", 
        "city_comparison.py",
        "multi_page_app.py",
        "run_multi_page.py"
    ]
    
    print("🔍 Checking required files...")
    missing_files = []
    
    for file in required_files:
        if os.path.exists(file):
            print(f"✅ {file}")
        else:
            print(f"❌ {file}")
            missing_files.append(file)
    
    return len(missing_files) == 0

def show_city_comparison_features():
    """Show what the city comparison dashboard offers"""
    
    print("🏙️ City Comparison Dashboard Features")
    print("=" * 50)
    
    print("🎯 RADAR CHARTS")
    print("- Multi-city comparison with beautiful radar visualization")
    print("- 5 key metrics: AQI, PM2.5, PM10, NO2, O3")
    print("- Color-coded cities with transparency")
    print("- Interactive hover for exact values")
    print()
    
    print("🏆 CITY RANKINGS")
    print("- Overall scoring system based on weighted air quality metrics")
    print("- Top 3 cities displayed as beautiful cards")
    print("- Complete ranking table with all metrics")
    print("- Real-time updates when changing time periods")
    print()
    
    print("📊 DETAILED COMPARISONS")
    print("- Bar charts for each pollutant (AQI, PM2.5, PM10, NO2, O3)")
    print("- Tabbed interface for easy metric switching")
    print("- Side-by-side metrics in data table format")
    print("- Sortable columns for easy analysis")
    print()
    
    print("🎨 BEAUTIFUL DESIGN")
    print("- Gradient backgrounds with modern color schemes")
    print("- Card-based layout for clean organization")
    print("- Responsive design that works on all devices")
    print("- Smooth animations and hover effects")
    print()

def show_available_cities():
    """Show available Spanish cities"""
    
    cities = [
        "Barcelona", "Madrid", "Valencia", "Granada", "Sevilla", 
        "Bilbao", "Malaga", "Valladolid", "Zaragoza", "Huelva", 
        "Soria", "Gijon", "Palma"
    ]
    
    print("🏙️ Available Spanish Cities")
    print("=" * 30)
    for i, city in enumerate(cities, 1):
        print(f"{i:2d}. {city}")
    print()

def show_scoring_system():
    """Show the scoring system used for rankings"""
    
    print("📊 City Ranking Scoring System")
    print("=" * 35)
    print("Overall Score = (AQI × 0.4) + (PM2.5 × 0.2) + (PM10 × 0.2) + (NO2 × 0.1) + (O3 × 0.1)")
    print()
    print("• Lower scores = Better air quality")
    print("• AQI has highest weight (40%) - most comprehensive metric")
    print("• Particulate matter (PM2.5, PM10) has significant weight (20% each)")
    print("• Gas pollutants (NO2, O3) have lower weight (10% each)")
    print()

def show_next_steps():
    """Show next steps to get the dashboard running"""
    
    print("🚀 Next Steps to Launch the Dashboard")
    print("=" * 40)
    print()
    print("1. 📦 Install required packages:")
    print("   pip install streamlit plotly pandas numpy boto3")
    print()
    print("2. 📊 Process some city data:")
    print("   python3 process_s3_to_db.py --city Barcelona --limit 100")
    print("   python3 process_s3_to_db.py --city Madrid --limit 100")
    print()
    print("3. 🚀 Launch the multi-page dashboard:")
    print("   python3 run_multi_page.py")
    print()
    print("4. 🏆 Select 'City Comparison' from the main menu")
    print()
    print("5. 🎯 Choose 2-6 cities to compare and explore!")
    print()

def main():
    print("🌍 Air Quality City Comparison - Quick Start Guide")
    print("=" * 55)
    print()
    
    # Check files
    if check_files():
        print("✅ All required files are present!")
    else:
        print("❌ Some files are missing. Please ensure all files are in the directory.")
        return
    
    print()
    
    # Show features
    show_city_comparison_features()
    
    # Show available cities
    show_available_cities()
    
    # Show scoring system
    show_scoring_system()
    
    # Show next steps
    show_next_steps()
    
    print("💡 Demo the features:")
    print("   python3 simple_demo.py")
    print()

if __name__ == "__main__":
    main()
