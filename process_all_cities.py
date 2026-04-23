#!/usr/bin/env python3
"""
Process all cities from S3 to database
"""

import boto3
from database_manager import AirQualityDatabase
from credentials import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import time

def process_all_cities():
    """Process all available cities from S3 to database"""
    
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
    
    # Initialize S3 client
    print("🔗 Initializing S3 client...")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    
    # Initialize database
    print("🗄️ Initializing database...")
    db = AirQualityDatabase("air_quality.db")
    
    # Show current stats
    stats = db.get_database_stats()
    print(f"📊 Current database stats: {stats['total_records']} records")
    print(f"   Cities already in database: {list(stats['city_counts'].keys())}")
    print()
    
    # Process each city
    total_results = {
        'total_files': 0,
        'successful': 0,
        'errors': 0,
        'total_time': 0
    }
    
    start_time = time.time()
    
    for i, city in enumerate(cities, 1):
        print(f"🏙️ Processing {city} ({i}/{len(cities)})")
        print("-" * 30)
        
        try:
            # Process city with optimized settings
            result = db.process_s3_bucket(
                s3_client=s3_client,
                bucket_name="air-quality-data-dumps",
                city_filter=city,
                limit=None,  # Process all files for this city
                max_workers=15,  # Optimized for multiple cities
                batch_size=100   # Larger batches for efficiency
            )
            
            # Accumulate results
            total_results['total_files'] += result['total_files']
            total_results['successful'] += result['successful']
            total_results['errors'] += result['errors']
            
            print(f"✅ {city} completed: {result['successful']} successful, {result['errors']} errors")
            print(f"   Rate: {result.get('rate', 0):.1f} files/sec")
            print()
            
        except Exception as e:
            print(f"❌ Error processing {city}: {e}")
            print()
            continue
    
    total_time = time.time() - start_time
    total_results['total_time'] = total_time
    
    # Final summary
    print("=" * 50)
    print("📊 FINAL SUMMARY")
    print("=" * 50)
    print(f"Total files processed: {total_results['total_files']}")
    print(f"Successful: {total_results['successful']}")
    print(f"Errors: {total_results['errors']}")
    print(f"Total time: {total_time:.1f}s")
    print(f"Average rate: {total_results['total_files']/total_time:.1f} files/sec")
    print()
    
    # Show updated database stats
    print("🗄️ Updated database stats:")
    final_stats = db.get_database_stats()
    print(f"Total records: {final_stats['total_records']}")
    print("Cities in database:")
    for city, count in final_stats['city_counts'].items():
        print(f"  {city}: {count} records")
    
    print()
    print("🎉 All cities processed successfully!")
    print("🚀 You can now run the Streamlit dashboard:")
    print("   python3 run_dashboard.py")

if __name__ == "__main__":
    process_all_cities()
