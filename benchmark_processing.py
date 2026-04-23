#!/usr/bin/env python3
"""
Benchmark script to test S3 processing performance
"""

import time
import boto3
from database_manager import AirQualityDatabase
from credentials import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

def benchmark_processing():
    """Benchmark different processing configurations"""
    
    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    
    # Test configurations
    test_configs = [
        {"workers": 1, "batch_size": 1, "name": "Single-threaded, single inserts"},
        {"workers": 5, "batch_size": 10, "name": "5 workers, batch size 10"},
        {"workers": 10, "batch_size": 50, "name": "10 workers, batch size 50"},
        {"workers": 20, "batch_size": 100, "name": "20 workers, batch size 100"},
    ]
    
    # Test with a small number of files first
    test_limit = 50
    
    print(f"Benchmarking S3 processing with {test_limit} files...")
    print("=" * 60)
    
    results = []
    
    for config in test_configs:
        print(f"\nTesting: {config['name']}")
        print("-" * 40)
        
        # Create fresh database for each test
        db_path = f"benchmark_{config['workers']}_{config['batch_size']}.db"
        db = AirQualityDatabase(db_path)
        
        # Time the processing
        start_time = time.time()
        
        result = db.process_s3_bucket(
            s3_client=s3_client,
            bucket_name="air-quality-data-dumps",
            city_filter="Barcelona",
            limit=test_limit,
            max_workers=config['workers'],
            batch_size=config['batch_size']
        )
        
        end_time = time.time()
        total_time = end_time - start_time
        
        # Calculate metrics
        rate = result['total_files'] / total_time if total_time > 0 else 0
        
        results.append({
            'config': config['name'],
            'workers': config['workers'],
            'batch_size': config['batch_size'],
            'total_time': total_time,
            'rate': rate,
            'successful': result['successful'],
            'errors': result['errors']
        })
        
        print(f"Results: {result['successful']} successful, {result['errors']} errors")
        print(f"Time: {total_time:.2f}s, Rate: {rate:.2f} files/sec")
        
        # Clean up test database
        import os
        if os.path.exists(db_path):
            os.remove(db_path)
    
    # Print summary
    print("\n" + "=" * 60)
    print("BENCHMARK SUMMARY")
    print("=" * 60)
    
    # Sort by rate (highest first)
    results.sort(key=lambda x: x['rate'], reverse=True)
    
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['config']}")
        print(f"   Rate: {result['rate']:.2f} files/sec")
        print(f"   Time: {result['total_time']:.2f}s")
        print(f"   Success: {result['successful']}/{result['successful'] + result['errors']}")
        print()
    
    # Recommend best configuration
    best = results[0]
    print(f"RECOMMENDED CONFIGURATION:")
    print(f"Workers: {best['workers']}, Batch Size: {best['batch_size']}")
    print(f"Expected rate: {best['rate']:.2f} files/sec")

if __name__ == "__main__":
    benchmark_processing()
