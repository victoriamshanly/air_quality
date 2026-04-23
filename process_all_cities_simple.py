#!/usr/bin/env python3
"""
Simple script to process all cities using the existing process_s3_to_db.py
"""

import subprocess
import sys

def process_all_cities():
    """Process all cities using the existing script"""
    
    # All Spanish cities from collect_data.py
    cities = [
        "Barcelona", "Madrid", "Valencia", "Granada", "Sevilla", 
        "Bilbao", "Malaga", "Valladolid", "Zaragoza", "Huelva", 
        "Soria", "Gijon", "Palma"
    ]
    
    print("🌍 Processing All Cities to Database")
    print("=" * 50)
    print(f"Cities to process: {len(cities)}")
    print(f"Cities: {', '.join(cities)}")
    print()
    
    results = []
    
    for i, city in enumerate(cities, 1):
        print(f"🏙️ Processing {city} ({i}/{len(cities)})")
        print("-" * 30)
        
        try:
            # Run the existing process_s3_to_db.py script for each city
            cmd = [
                sys.executable, "process_s3_to_db.py",
                "--city", city,
                "--limit", "500",  # Process up to 500 files per city
                "--workers", "10",
                "--batch-size", "50"
            ]
            
            print(f"Running: {' '.join(cmd)}")
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                print(f"✅ {city} processed successfully")
                # Extract success/error counts from output
                output_lines = result.stdout.split('\n')
                for line in output_lines:
                    if "successful" in line and "errors" in line:
                        print(f"   {line}")
                        break
            else:
                print(f"❌ Error processing {city}")
                print(f"   Error: {result.stderr}")
            
            print()
            
        except Exception as e:
            print(f"❌ Exception processing {city}: {e}")
            print()
            continue
    
    print("=" * 50)
    print("🎉 All cities processing completed!")
    print("🚀 You can now run the Streamlit dashboard:")
    print("   python3 run_dashboard.py")

if __name__ == "__main__":
    process_all_cities()
