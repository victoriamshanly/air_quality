import sqlite3
import json
import pandas as pd
from datetime import datetime
import boto3
from typing import List, Dict, Any, Optional
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from threading import Lock
import multiprocessing

class AirQualityDatabase:
    def __init__(self, db_path: str = "air_quality.db"):
        """
        Initialize the air quality database manager
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the database with the required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create air_quality_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS air_quality_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                hour_key TEXT NOT NULL,  -- For duplicate handling (city + hour)
                aqi INTEGER,
                dominant_pollutant TEXT,
                pm25 REAL,
                pm10 REAL,
                no2 REAL,
                o3 REAL,
                so2 REAL,
                co REAL,
                t REAL,  -- temperature
                h REAL,  -- humidity
                p REAL,  -- pressure
                w REAL,  -- wind
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(city, hour_key)
            )
        ''')
        
        # Create index for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_city_timestamp 
            ON air_quality_data(city, timestamp)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON air_quality_data(timestamp)
        ''')
        
        conn.commit()
        conn.close()
        print(f"Database initialized at {self.db_path}")
    
    def extract_city_from_filename(self, filename: str) -> str:
        """Extract city name from filename like 'Barcelona-2024-10-07T10:00:00+02:00.json'"""
        return filename.split('-')[0]
    
    def parse_timestamp(self, timestamp_str: str) -> datetime:
        """Parse ISO timestamp string to datetime object"""
        try:
            # Handle different timestamp formats
            if 'T' in timestamp_str:
                # Remove timezone info for simplicity
                clean_timestamp = timestamp_str.split('+')[0].split('Z')[0]
                return pd.to_datetime(clean_timestamp)
            else:
                return pd.to_datetime(timestamp_str)
        except Exception as e:
            raise ValueError(f"Could not parse timestamp '{timestamp_str}': {e}")
    
    def create_hour_key(self, city: str, timestamp: datetime) -> str:
        """Create a unique key for each city-hour combination to handle duplicates"""
        return f"{city}_{timestamp.strftime('%Y-%m-%d_%H')}"
    
    def process_s3_file(self, s3_client: boto3.client, bucket_name: str, file_key: str) -> bool:
        """
        Process a single S3 file and store data in the database
        
        Args:
            s3_client: S3 client instance
            bucket_name: S3 bucket name
            file_key: S3 object key
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Download file content
            response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
            content = response['Body'].read().decode('utf-8')
            
            if not content.strip():
                print(f"Warning: Empty file {file_key}")
                return False
            
            # Parse JSON content
            try:
                data = self.safe_parse_json(content)
            except ValueError as e:
                print(f"JSON parse error in {file_key}: {e}")
                return False
            
            # Extract city from filename
            city = self.extract_city_from_filename(file_key)
            
            # Extract timestamp from data
            if not (data.get('status') == 'ok' and 'data' in data):
                print(f"Invalid data structure in {file_key}")
                return False
            
            data_section = data['data']
            if 'time' not in data_section or 'iso' not in data_section['time']:
                print(f"No timestamp found in {file_key}")
                return False
            
            timestamp_str = data_section['time']['iso']
            timestamp = self.parse_timestamp(timestamp_str)
            hour_key = self.create_hour_key(city, timestamp)
            
            # Extract air quality data
            record = {
                'city': city,
                'timestamp': timestamp_str,
                'hour_key': hour_key,
                'aqi': data_section.get('aqi'),
                'dominant_pollutant': data_section.get('dominentpol')
            }
            
            # Extract individual air quality measurements
            iaqi = data_section.get('iaqi', {})
            for pollutant, value_dict in iaqi.items():
                if isinstance(value_dict, dict) and 'v' in value_dict:
                    record[pollutant] = value_dict['v']
            
            # Store in database
            self.insert_record(record)
            return True
            
        except Exception as e:
            print(f"Error processing {file_key}: {e}")
            return False
    
    def safe_parse_json(self, content: str) -> dict:
        """
        Safely parse JSON content that might have single quotes instead of double quotes
        """
        import ast
        
        # First try standard JSON parsing
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # If that fails, try using ast.literal_eval for Python dict syntax
        try:
            # Replace single quotes with double quotes for JSON compatibility
            cleaned_content = content.replace("'", '"')
            return json.loads(cleaned_content)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # If that fails, try ast.literal_eval (handles Python dict syntax)
        try:
            return ast.literal_eval(content)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Could not parse content as JSON or Python dict: {e}")
    
    def insert_record(self, record: Dict[str, Any]):
        """Insert a record into the database, handling duplicates"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Use INSERT OR REPLACE to handle duplicates
        cursor.execute('''
            INSERT OR REPLACE INTO air_quality_data 
            (city, timestamp, hour_key, aqi, dominant_pollutant, pm25, pm10, no2, o3, so2, co, t, h, p, w)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            record.get('city'),
            record.get('timestamp'),
            record.get('hour_key'),
            record.get('aqi'),
            record.get('dominant_pollutant'),
            record.get('pm25'),
            record.get('pm10'),
            record.get('no2'),
            record.get('o3'),
            record.get('so2'),
            record.get('co'),
            record.get('t'),
            record.get('h'),
            record.get('p'),
            record.get('w')
        ))
        
        conn.commit()
        conn.close()
    
    def insert_records_batch(self, records: List[Dict[str, Any]]):
        """Insert multiple records in a single transaction for better performance"""
        if not records:
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Prepare data for batch insert
            data_tuples = []
            for record in records:
                data_tuples.append((
                    record.get('city'),
                    record.get('timestamp'),
                    record.get('hour_key'),
                    record.get('aqi'),
                    record.get('dominant_pollutant'),
                    record.get('pm25'),
                    record.get('pm10'),
                    record.get('no2'),
                    record.get('o3'),
                    record.get('so2'),
                    record.get('co'),
                    record.get('t'),
                    record.get('h'),
                    record.get('p'),
                    record.get('w')
                ))
            
            # Batch insert
            cursor.executemany('''
                INSERT OR REPLACE INTO air_quality_data 
                (city, timestamp, hour_key, aqi, dominant_pollutant, pm25, pm10, no2, o3, so2, co, t, h, p, w)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', data_tuples)
            
            conn.commit()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def process_s3_bucket(self, s3_client: boto3.client, bucket_name: str, 
                         city_filter: str = "Barcelona", limit: Optional[int] = None,
                         max_workers: int = 10, batch_size: int = 50) -> Dict[str, int]:
        """
        Process all files from S3 bucket and store in database with parallel processing
        
        Args:
            s3_client: S3 client instance
            bucket_name: S3 bucket name
            city_filter: Filter files by city name
            limit: Maximum number of files to process
            max_workers: Number of parallel workers
            batch_size: Number of records to batch insert
            
        Returns:
            Dictionary with processing statistics
        """
        print(f"Processing S3 bucket '{bucket_name}' for city '{city_filter}'...")
        print(f"Using {max_workers} parallel workers with batch size {batch_size}")
        
        # List files
        paginator = s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=bucket_name, Prefix=city_filter)
        
        files = []
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith('.json'):
                        files.append(obj['Key'])
        
        # Sort files (newest first)
        files = sorted(files, reverse=True)
        
        if limit:
            files = files[:limit]
        
        print(f"Found {len(files)} files to process")
        
        # Process files in parallel
        return self._process_files_parallel(s3_client, bucket_name, files, max_workers, batch_size)
    
    def _process_files_parallel(self, s3_client: boto3.client, bucket_name: str, 
                               files: List[str], max_workers: int, batch_size: int) -> Dict[str, int]:
        """Process files in parallel with batch database inserts"""
        
        # Thread-safe counters
        success_count = 0
        error_count = 0
        processed_count = 0
        lock = Lock()
        
        # Batch storage for database inserts
        batch_records = []
        batch_lock = Lock()
        
        def process_single_file(file_key: str) -> Optional[Dict[str, Any]]:
            """Process a single file and return the record"""
            try:
                # Download file content
                response = s3_client.get_object(Bucket=bucket_name, Key=file_key)
                content = response['Body'].read().decode('utf-8')
                
                if not content.strip():
                    return None
                
                # Parse JSON content
                try:
                    data = self.safe_parse_json(content)
                except ValueError:
                    return None
                
                # Extract city from filename
                city = self.extract_city_from_filename(file_key)
                
                # Extract timestamp from data
                if not (data.get('status') == 'ok' and 'data' in data):
                    return None
                
                data_section = data['data']
                if 'time' not in data_section or 'iso' not in data_section['time']:
                    return None
                
                timestamp_str = data_section['time']['iso']
                timestamp = self.parse_timestamp(timestamp_str)
                hour_key = self.create_hour_key(city, timestamp)
                
                # Extract air quality data
                record = {
                    'city': city,
                    'timestamp': timestamp_str,
                    'hour_key': hour_key,
                    'aqi': data_section.get('aqi'),
                    'dominant_pollutant': data_section.get('dominentpol')
                }
                
                # Extract individual air quality measurements
                iaqi = data_section.get('iaqi', {})
                for pollutant, value_dict in iaqi.items():
                    if isinstance(value_dict, dict) and 'v' in value_dict:
                        record[pollutant] = value_dict['v']
                
                return record
                
            except Exception:
                return None
        
        def batch_insert_worker():
            """Worker function to handle batch database inserts"""
            nonlocal batch_records
            while True:
                with batch_lock:
                    if len(batch_records) >= batch_size:
                        records_to_insert = batch_records[:batch_size]
                        batch_records = batch_records[batch_size:]
                    else:
                        records_to_insert = batch_records
                        batch_records = []
                
                if records_to_insert:
                    try:
                        self.insert_records_batch(records_to_insert)
                    except Exception as e:
                        print(f"Batch insert error: {e}")
                
                if not batch_records and processed_count >= len(files):
                    break
        
        # Start parallel processing
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # Submit all file processing tasks
            future_to_file = {
                executor.submit(process_single_file, file_key): file_key 
                for file_key in files
            }
            
            # Process completed tasks
            for future in as_completed(future_to_file):
                file_key = future_to_file[future]
                
                try:
                    record = future.result()
                    with lock:
                        processed_count += 1
                        
                        if record:
                            success_count += 1
                            with batch_lock:
                                batch_records.append(record)
                        else:
                            error_count += 1
                        
                        # Progress indicator with ETA
                        if processed_count % 50 == 0 or processed_count == len(files):
                            elapsed = time.time() - start_time
                            rate = processed_count / elapsed if elapsed > 0 else 0
                            eta = (len(files) - processed_count) / rate if rate > 0 else 0
                            
                            print(f"Processed {processed_count}/{len(files)} files "
                                  f"(Success: {success_count}, Errors: {error_count}) "
                                  f"Rate: {rate:.1f} files/sec, ETA: {eta:.1f}s")
                
                except Exception as e:
                    with lock:
                        error_count += 1
                        processed_count += 1
                        print(f"Error processing {file_key}: {e}")
        
        # Insert remaining records
        if batch_records:
            try:
                self.insert_records_batch(batch_records)
            except Exception as e:
                print(f"Final batch insert error: {e}")
        
        total_time = time.time() - start_time
        print(f"Processing complete: {success_count} successful, {error_count} errors")
        print(f"Total time: {total_time:.1f}s, Average rate: {len(files)/total_time:.1f} files/sec")
        
        return {
            'total_files': len(files),
            'successful': success_count,
            'errors': error_count,
            'total_time': total_time,
            'rate': len(files)/total_time if total_time > 0 else 0
        }
    
    def get_data(self, city: str = "Barcelona", days: int = 7, 
                 limit: Optional[int] = None) -> pd.DataFrame:
        """
        Retrieve data from the database
        
        Args:
            city: City name to filter
            days: Number of recent days to retrieve
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with air quality data
        """
        conn = sqlite3.connect(self.db_path)
        
        # Calculate date threshold
        from datetime import datetime, timedelta
        threshold_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
        
        query = '''
            SELECT * FROM air_quality_data 
            WHERE city = ? AND timestamp >= ?
            ORDER BY timestamp DESC
        '''
        
        params = [city, threshold_date]
        
        if limit:
            query += ' LIMIT ?'
            params.append(limit)
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        # Convert timestamp to datetime
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def get_latest_data(self, city: str = "Barcelona", hours: int = 24) -> pd.DataFrame:
        """
        Get the most recent data for a city
        
        Args:
            city: City name
            hours: Number of recent hours to retrieve
            
        Returns:
            DataFrame with recent air quality data
        """
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM air_quality_data 
            WHERE city = ?
            ORDER BY timestamp DESC
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=[city, hours])
        conn.close()
        
        if not df.empty:
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get statistics about the database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total records
        cursor.execute('SELECT COUNT(*) FROM air_quality_data')
        total_records = cursor.fetchone()[0]
        
        # Records by city
        cursor.execute('SELECT city, COUNT(*) FROM air_quality_data GROUP BY city')
        city_counts = dict(cursor.fetchall())
        
        # Date range
        cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM air_quality_data')
        date_range = cursor.fetchone()
        
        conn.close()
        
        return {
            'total_records': total_records,
            'city_counts': city_counts,
            'date_range': date_range
        }
