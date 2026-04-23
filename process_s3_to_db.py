#!/usr/bin/env python3
"""
Script to process S3 air quality files and store them in SQLite database
"""

import boto3
from database_manager import AirQualityDatabase
from credentials import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY
import argparse
import sys

def main():
    parser = argparse.ArgumentParser(description='Process S3 air quality files to SQLite database')
    parser.add_argument('--bucket', default='air-quality-data-dumps', 
                       help='S3 bucket name (default: air-quality-data-dumps)')
    parser.add_argument('--city', default='Barcelona', 
                       help='City to process (default: Barcelona)')
    parser.add_argument('--limit', type=int, 
                       help='Maximum number of files to process')
    parser.add_argument('--db-path', default='air_quality.db', 
                       help='SQLite database path (default: air_quality.db)')
    parser.add_argument('--days', type=int, default=30, 
                       help='Number of recent days to process (default: 30)')
    parser.add_argument('--workers', type=int, default=10, 
                       help='Number of parallel workers (default: 10)')
    parser.add_argument('--batch-size', type=int, default=50, 
                       help='Batch size for database inserts (default: 50)')
    
    args = parser.parse_args()
    
    # Initialize S3 client
    print("Initializing S3 client...")
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    
    # Initialize database
    print(f"Initializing database at {args.db_path}...")
    db = AirQualityDatabase(args.db_path)
    
    # Show current database stats
    stats = db.get_database_stats()
    print(f"Current database stats: {stats}")
    
    # Process S3 files with optimized parallel processing
    print(f"Processing S3 files for {args.city}...")
    result = db.process_s3_bucket(
        s3_client=s3_client,
        bucket_name=args.bucket,
        city_filter=args.city,
        limit=args.limit,
        max_workers=args.workers,
        batch_size=args.batch_size
    )
    
    print(f"Processing results: {result}")
    
    # Show updated database stats
    stats = db.get_database_stats()
    print(f"Updated database stats: {stats}")
    
    # Test data retrieval
    print(f"Testing data retrieval for {args.city}...")
    df = db.get_data(city=args.city, days=7, limit=10)
    
    if not df.empty:
        print(f"Retrieved {len(df)} records")
        print("Sample data:")
        print(df[['timestamp', 'aqi', 'dominant_pollutant', 'pm25', 'pm10']].head())
    else:
        print("No data retrieved")
    
    print("Processing complete!")

if __name__ == "__main__":
    main()
