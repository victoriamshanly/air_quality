import boto3
import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import re
from typing import List, Dict, Any
import ast
from database_manager import AirQualityDatabase

class AirQualityPlotter:
    def __init__(self, bucket_name: str, s3_client: boto3.client):
        """
        Initialize the plotter with S3 bucket configuration
        
        Args:
            bucket_name: Name of the S3 bucket
            s3_client: S3 client
        """
        self.bucket_name = bucket_name
        
        # Initialize S3 client
        self.s3_client = s3_client

class DatabaseAirQualityPlotter:
    def __init__(self, db_path: str = "air_quality.db"):
        """
        Initialize the database-based plotter
        
        Args:
            db_path: Path to the SQLite database
        """
        self.db = AirQualityDatabase(db_path)
    
    def load_data_from_db(self, city: str = "Barcelona", days: int = 7, 
                         limit: int = None) -> pd.DataFrame:
        """
        Load air quality data from the database
        
        Args:
            city: City name to filter
            days: Number of recent days to retrieve
            limit: Maximum number of records to return
            
        Returns:
            DataFrame with air quality data
        """
        print(f"Loading data from database for {city} (last {days} days)...")
        df = self.db.get_data(city=city, days=days, limit=limit)
        
        if df.empty:
            print("No data found in database!")
            return df
        
        print(f"Loaded {len(df)} records from database")
        return df
    
    def get_latest_data(self, city: str = "Barcelona", hours: int = 24) -> pd.DataFrame:
        """
        Get the most recent air quality data
        
        Args:
            city: City name
            hours: Number of recent hours to retrieve
            
        Returns:
            DataFrame with recent air quality data
        """
        print(f"Loading latest {hours} hours of data for {city}...")
        df = self.db.get_latest_data(city=city, hours=hours)
        
        if df.empty:
            print("No recent data found in database!")
            return df
        
        print(f"Loaded {len(df)} recent records from database")
        return df
    
    def plot_metrics_evolution(self, df: pd.DataFrame, figsize: tuple = (15, 12)):
        """
        Create comprehensive plots of air quality metrics evolution
        
        Args:
            df: DataFrame with air quality data
            figsize: Figure size tuple
        """
        if df.empty:
            print("No data to plot!")
            return
        
        # Set up the plot style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('Barcelona Air Quality Metrics Evolution (Database)', fontsize=16, fontweight='bold')
        
        # Plot 1: AQI over time (newest first)
        axes[0, 0].plot(df['timestamp'], df['aqi'], linewidth=2, color='darkblue')
        axes[0, 0].set_title('Air Quality Index (AQI) - Latest Data', fontweight='bold')
        axes[0, 0].set_ylabel('AQI')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Plot 2: PM2.5 and PM10
        if 'pm25' in df.columns and 'pm10' in df.columns:
            axes[0, 1].plot(df['timestamp'], df['pm25'], label='PM2.5', linewidth=2)
            axes[0, 1].plot(df['timestamp'], df['pm10'], label='PM10', linewidth=2)
            axes[0, 1].set_title('Particulate Matter', fontweight='bold')
            axes[0, 1].set_ylabel('μg/m³')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Plot 3: Gas pollutants
        gas_pollutants = ['no2', 'o3', 'so2', 'co']
        available_gases = [col for col in gas_pollutants if col in df.columns]
        
        if available_gases:
            for gas in available_gases:
                axes[1, 0].plot(df['timestamp'], df[gas], label=gas.upper(), linewidth=2)
            axes[1, 0].set_title('Gas Pollutants', fontweight='bold')
            axes[1, 0].set_ylabel('Concentration')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Plot 4: Temperature and Humidity
        if 't' in df.columns and 'h' in df.columns:
            ax4_temp = axes[1, 1]
            ax4_hum = ax4_temp.twinx()
            
            line1 = ax4_temp.plot(df['timestamp'], df['t'], 'r-', label='Temperature', linewidth=2)
            line2 = ax4_hum.plot(df['timestamp'], df['h'], 'b-', label='Humidity', linewidth=2)
            
            ax4_temp.set_title('Temperature & Humidity', fontweight='bold')
            ax4_temp.set_ylabel('Temperature (°C)', color='r')
            ax4_hum.set_ylabel('Humidity (%)', color='b')
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax4_temp.legend(lines, labels, loc='upper left')
            
            ax4_temp.grid(True, alpha=0.3)
            ax4_temp.tick_params(axis='x', rotation=45)
        
        # Adjust layout and show
        plt.tight_layout()
        plt.show()
    
    def plot_daily_patterns(self, df: pd.DataFrame, figsize: tuple = (12, 8)):
        """
        Plot daily patterns by hour of day
        """
        if df.empty:
            return
        
        # Add hour column
        df_copy = df.copy()
        df_copy['hour'] = df_copy['timestamp'].dt.hour
        
        # Group by hour and calculate mean values
        hourly_means = df_copy.groupby('hour').agg({
            'aqi': 'mean',
            'pm25': 'mean',
            'pm10': 'mean',
            'no2': 'mean',
            'o3': 'mean'
        }).reset_index()
        
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle('Average Daily Patterns (by Hour) - Database', fontsize=14, fontweight='bold')
        
        # AQI pattern
        axes[0].plot(hourly_means['hour'], hourly_means['aqi'], marker='o', linewidth=2)
        axes[0].set_title('AQI Daily Pattern')
        axes[0].set_xlabel('Hour of Day')
        axes[0].set_ylabel('Average AQI')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xticks(range(0, 24, 2))
        
        # Multiple pollutants pattern
        pollutants = ['pm25', 'pm10', 'no2', 'o3']
        for pollutant in pollutants:
            if pollutant in hourly_means.columns:
                axes[1].plot(hourly_means['hour'], hourly_means[pollutant], 
                           marker='o', label=pollutant.upper(), linewidth=2)
        
        axes[1].set_title('Pollutants Daily Pattern')
        axes[1].set_xlabel('Hour of Day')
        axes[1].set_ylabel('Average Concentration')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xticks(range(0, 24, 2))
        
        plt.tight_layout()
        plt.show()
    
    def generate_summary_stats(self, df: pd.DataFrame):
        """
        Generate summary statistics
        """
        if df.empty:
            return
        
        print("\n=== AIR QUALITY SUMMARY STATISTICS (DATABASE) ===")
        print(f"Data Period: {df['timestamp'].max()} to {df['timestamp'].min()} (newest to oldest)")
        print(f"Total Records: {len(df)}")
        print(f"Date Range: {(df['timestamp'].max() - df['timestamp'].min()).days} days")
        
        # Numeric columns only
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        numeric_cols = [col for col in numeric_cols if col not in ['id', 'timestamp']]
        
        summary = df[numeric_cols].describe().round(2)
        print("\n", summary)
        
        # Show most recent data points
        print(f"\n=== MOST RECENT DATA POINTS ===")
        recent_data = df.head(10)[['timestamp', 'aqi', 'dominant_pollutant'] + 
                                 [col for col in ['pm25', 'pm10', 'no2', 'o3', 'so2', 'co'] if col in df.columns]]
        print(recent_data.to_string(index=False))
    
    def list_barcelona_files(self, prefix: str = "Barcelona-", limit: int = None, reverse: bool = True) -> List[str]:
        """
        List all Barcelona air quality files in the bucket
        
        Args:
            prefix: File prefix to filter
            limit: Maximum number of files to return
            reverse: If True, return newest files first (default: True)
            
        Returns:
            List of file keys
        """
        paginator = self.s3_client.get_paginator('list_objects_v2')
        page_iterator = paginator.paginate(Bucket=self.bucket_name, Prefix=prefix)
        
        files = []
        for page in page_iterator:
            if 'Contents' in page:
                for obj in page['Contents']:
                    if obj['Key'].endswith('.json'):
                        files.append(obj['Key'])
        
        # Sort files by name (which includes timestamp) and reverse if requested
        sorted_files = sorted(files, reverse=reverse)
        
        # Apply limit after sorting
        if limit:
            return sorted_files[:limit]
        
        return sorted_files
    
    def debug_file(self, file_key: str) -> None:
        """
        Debug a specific file to understand its content and structure
        
        Args:
            file_key: S3 object key to debug
        """
        try:
            print(f"Debugging file: {file_key}")
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=file_key)
            content = response['Body'].read().decode('utf-8')
            
            print(f"File size: {len(content)} characters")
            print(f"Content preview (first 200 chars): {content[:200]}")
            print(f"Content preview (last 200 chars): {content[-200:]}")
            
            # Try to parse JSON
            try:
                data = self.safe_parse_json(content)
                print(f"JSON structure: {list(data.keys()) if isinstance(data, dict) else type(data)}")
                if isinstance(data, dict) and 'data' in data:
                    print(f"Data keys: {list(data['data'].keys()) if isinstance(data['data'], dict) else type(data['data'])}")
            except ValueError as e:
                print(f"JSON parse error: {e}")
                
        except Exception as e:
            print(f"Error debugging file {file_key}: {e}")
    
    def safe_parse_json(self, content: str) -> dict:
        """
        Safely parse JSON content that might have single quotes instead of double quotes
        
        Args:
            content: JSON content as string
            
        Returns:
            Parsed data as dictionary
        """
        # First try standard JSON parsing
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            pass
        
        # If that fails, try using ast.literal_eval for Python dict syntax
        try:
            # Replace single quotes with double quotes for JSON compatibility
            # This is a simple approach - be careful with strings that contain quotes
            cleaned_content = content.replace("'", '"')
            return json.loads(cleaned_content)
        except (json.JSONDecodeError, ValueError):
            pass
        
        # If that fails, try ast.literal_eval (handles Python dict syntax)
        try:
            return ast.literal_eval(content)
        except (ValueError, SyntaxError) as e:
            raise ValueError(f"Could not parse content as JSON or Python dict: {e}")
    
    def extract_timestamp_from_filename(self, filename: str) -> datetime:
        """
        Extract timestamp from filename like 'Barcelona-2025-09-01T02:00:00+02:00.json'
        """
        pattern = r'Barcelona-(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\+\d{2}:\d{2})\.json'
        match = re.search(pattern, filename)
        if match:
            timestamp_str = match.group(1)
            return pd.to_datetime(timestamp_str)
        else:
            raise ValueError(f"Could not extract timestamp from {filename}")
    
    def load_data_from_s3(self, file_keys: List[str]) -> pd.DataFrame:
        """
        Load and parse multiple JSON files from S3 into a pandas DataFrame
        
        Args:
            file_keys: List of S3 object keys
            
        Returns:
            DataFrame with time series data
        """
        data_records = []
        error_count = 0
        success_count = 0
        
        print(f"Loading {len(file_keys)} files from S3...")
        
        for i, key in enumerate(file_keys):
            try:
                # Download file content
                response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
                content = response['Body'].read().decode('utf-8')
                
                # Check if content is empty or invalid
                if not content.strip():
                    print(f"Warning: Empty file {key}")
                    error_count += 1
                    continue
                
                # Try to parse JSON with better error handling
                try:
                    data = self.safe_parse_json(content)
                except ValueError as json_err:
                    print(f"JSON parse error in {key}: {json_err}")
                    print(f"Content preview: {content[:100]}...")
                    error_count += 1
                    continue
                
                # Extract timestamp from filename
                try:
                    timestamp = self.extract_timestamp_from_filename(key)
                except ValueError as ts_err:
                    print(f"Timestamp extraction error for {key}: {ts_err}")
                    error_count += 1
                    continue
                
                # Extract relevant data
                if data.get('status') == 'ok' and 'data' in data:
                    record = {
                        'timestamp': timestamp,
                        'aqi': data['data'].get('aqi'),
                        'dominant_pollutant': data['data'].get('dominentpol')
                    }
                    
                    # Extract individual air quality measurements
                    iaqi = data['data'].get('iaqi', {})
                    for pollutant, value_dict in iaqi.items():
                        if isinstance(value_dict, dict) and 'v' in value_dict:
                            record[pollutant] = value_dict['v']
                    
                    data_records.append(record)
                    success_count += 1
                else:
                    print(f"Invalid data structure in {key}: status={data.get('status')}, has_data={'data' in data}")
                    error_count += 1
                
                # Progress indicator
                if (i + 1) % 50 == 0:
                    print(f"Processed {i + 1}/{len(file_keys)} files (Success: {success_count}, Errors: {error_count})")
                    
            except KeyboardInterrupt:
                print(f"\nInterrupted by user. Processed {i + 1}/{len(file_keys)} files so far.")
                break
            except Exception as e:
                print(f"Unexpected error processing {key}: {e}")
                error_count += 1
                continue
        
        print(f"Loading complete: {success_count} successful, {error_count} errors")
        print(f"Successfully loaded {len(data_records)} records")
        
        # Convert to DataFrame and sort by timestamp (newest first by default)
        df = pd.DataFrame(data_records)
        if not df.empty:
            df = df.sort_values('timestamp', ascending=False).reset_index(drop=True)
        
        return df
    
    def plot_metrics_evolution(self, df: pd.DataFrame, figsize: tuple = (15, 12)):
        """
        Create comprehensive plots of air quality metrics evolution
        
        Args:
            df: DataFrame with air quality data
            figsize: Figure size tuple
        """
        if df.empty:
            print("No data to plot!")
            return
        
        # Set up the plot style
        plt.style.use('default')
        sns.set_palette("husl")
        
        # Create subplots
        fig, axes = plt.subplots(2, 2, figsize=figsize)
        fig.suptitle('Barcelona Air Quality Metrics Evolution', fontsize=16, fontweight='bold')
        
        # Plot 1: AQI over time (newest first)
        axes[0, 0].plot(df['timestamp'], df['aqi'], linewidth=2, color='darkblue')
        axes[0, 0].set_title('Air Quality Index (AQI) - Latest Data', fontweight='bold')
        axes[0, 0].set_ylabel('AQI')
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].tick_params(axis='x', rotation=45)
        
        # Plot 2: PM2.5 and PM10
        if 'pm25' in df.columns and 'pm10' in df.columns:
            axes[0, 1].plot(df['timestamp'], df['pm25'], label='PM2.5', linewidth=2)
            axes[0, 1].plot(df['timestamp'], df['pm10'], label='PM10', linewidth=2)
            axes[0, 1].set_title('Particulate Matter', fontweight='bold')
            axes[0, 1].set_ylabel('μg/m³')
            axes[0, 1].legend()
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].tick_params(axis='x', rotation=45)
        
        # Plot 3: Gas pollutants
        gas_pollutants = ['no2', 'o3', 'so2', 'co']
        available_gases = [col for col in gas_pollutants if col in df.columns]
        
        if available_gases:
            for gas in available_gases:
                axes[1, 0].plot(df['timestamp'], df[gas], label=gas.upper(), linewidth=2)
            axes[1, 0].set_title('Gas Pollutants', fontweight='bold')
            axes[1, 0].set_ylabel('Concentration')
            axes[1, 0].legend()
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].tick_params(axis='x', rotation=45)
        
        # Plot 4: Temperature and Humidity
        if 't' in df.columns and 'h' in df.columns:
            ax4_temp = axes[1, 1]
            ax4_hum = ax4_temp.twinx()
            
            line1 = ax4_temp.plot(df['timestamp'], df['t'], 'r-', label='Temperature', linewidth=2)
            line2 = ax4_hum.plot(df['timestamp'], df['h'], 'b-', label='Humidity', linewidth=2)
            
            ax4_temp.set_title('Temperature & Humidity', fontweight='bold')
            ax4_temp.set_ylabel('Temperature (°C)', color='r')
            ax4_hum.set_ylabel('Humidity (%)', color='b')
            
            # Combine legends
            lines = line1 + line2
            labels = [l.get_label() for l in lines]
            ax4_temp.legend(lines, labels, loc='upper left')
            
            ax4_temp.grid(True, alpha=0.3)
            ax4_temp.tick_params(axis='x', rotation=45)
        
        # Adjust layout and show
        plt.tight_layout()
        plt.show()
    
    def plot_daily_patterns(self, df: pd.DataFrame, figsize: tuple = (12, 8)):
        """
        Plot daily patterns by hour of day
        """
        if df.empty:
            return
        
        # Add hour column
        df_copy = df.copy()
        df_copy['hour'] = df_copy['timestamp'].dt.hour
        
        # Group by hour and calculate mean values
        hourly_means = df_copy.groupby('hour').agg({
            'aqi': 'mean',
            'pm25': 'mean',
            'pm10': 'mean',
            'no2': 'mean',
            'o3': 'mean'
        }).reset_index()
        
        fig, axes = plt.subplots(1, 2, figsize=figsize)
        fig.suptitle('Average Daily Patterns (by Hour)', fontsize=14, fontweight='bold')
        
        # AQI pattern
        axes[0].plot(hourly_means['hour'], hourly_means['aqi'], marker='o', linewidth=2)
        axes[0].set_title('AQI Daily Pattern')
        axes[0].set_xlabel('Hour of Day')
        axes[0].set_ylabel('Average AQI')
        axes[0].grid(True, alpha=0.3)
        axes[0].set_xticks(range(0, 24, 2))
        
        # Multiple pollutants pattern
        pollutants = ['pm25', 'pm10', 'no2', 'o3']
        for pollutant in pollutants:
            if pollutant in hourly_means.columns:
                axes[1].plot(hourly_means['hour'], hourly_means[pollutant], 
                           marker='o', label=pollutant.upper(), linewidth=2)
        
        axes[1].set_title('Pollutants Daily Pattern')
        axes[1].set_xlabel('Hour of Day')
        axes[1].set_ylabel('Average Concentration')
        axes[1].legend()
        axes[1].grid(True, alpha=0.3)
        axes[1].set_xticks(range(0, 24, 2))
        
        plt.tight_layout()
        plt.show()
    
    def generate_summary_stats(self, df: pd.DataFrame):
        """
        Generate summary statistics
        """
        if df.empty:
            return
        
        print("\n=== AIR QUALITY SUMMARY STATISTICS ===")
        print(f"Data Period: {df['timestamp'].max()} to {df['timestamp'].min()} (newest to oldest)")
        print(f"Total Records: {len(df)}")
        print(f"Date Range: {(df['timestamp'].max() - df['timestamp'].min()).days} days")
        
        # Numeric columns only
        numeric_cols = df.select_dtypes(include=['float64', 'int64']).columns
        numeric_cols = [col for col in numeric_cols if col != 'timestamp']
        
        summary = df[numeric_cols].describe().round(2)
        print("\n", summary)
        
        # Show most recent data points
        print(f"\n=== MOST RECENT DATA POINTS ===")
        recent_data = df.head(10)[['timestamp', 'aqi', 'dominant_pollutant'] + 
                                 [col for col in ['pm25', 'pm10', 'no2', 'o3', 'so2', 'co'] if col in df.columns]]
        print(recent_data.to_string(index=False))

# Usage example function
def quick_analysis(bucket_name: str, s3_client: boto3.client, days_limit: int = 7):
    """
    Quick analysis function to get started fast
    
    Args:
        bucket_name: S3 bucket name
        s3_client: S3 client instance
        days_limit: Limit analysis to recent N days worth of data
    """
    try:
        plotter = AirQualityPlotter(bucket_name, s3_client)
        
        # Get file list (limit to avoid overwhelming)
        print(f"Fetching file list for last {days_limit} days...")
        files = plotter.list_barcelona_files(limit=days_limit * 24)  # Assuming hourly data
        
        if not files:
            print("No Barcelona air quality files found!")
            return None
        
        print(f"Found {len(files)} files")
        
        # Load data with error handling
        print("Starting data loading...")
        df = plotter.load_data_from_s3(files)
        
        if df.empty:
            print("No valid data found! Check the error messages above for details.")
            return None
        
        print(f"Data loaded successfully: {len(df)} records")
        
        # Generate plots and stats
        try:
            plotter.generate_summary_stats(df)
        except Exception as e:
            print(f"Error generating summary stats: {e}")
        
        try:
            plotter.plot_metrics_evolution(df)
        except Exception as e:
            print(f"Error creating evolution plots: {e}")
        
        try:
            plotter.plot_daily_patterns(df)
        except Exception as e:
            print(f"Error creating daily pattern plots: {e}")
        
        return df
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        return None
    except Exception as e:
        print(f"Unexpected error during analysis: {e}")
        return None

def safe_analysis(bucket_name: str, s3_client: boto3.client, days_limit: int = 3, max_files: int = 50):
    """
    Safer analysis function that limits the number of files and provides better error handling
    
    Args:
        bucket_name: S3 bucket name
        s3_client: S3 client instance
        days_limit: Limit analysis to recent N days worth of data
        max_files: Maximum number of files to process
    """
    try:
        plotter = AirQualityPlotter(bucket_name, s3_client)
        
        # Get file list with stricter limits
        print(f"Fetching file list for last {days_limit} days (max {max_files} files)...")
        files = plotter.list_barcelona_files(limit=max_files)
        
        if not files:
            print("No Barcelona air quality files found!")
            return None
        
        print(f"Found {len(files)} files")
        
        # Debug a few files first to understand the data structure
        print("Debugging first few files...")
        for i, file_key in enumerate(files[:3]):
            plotter.debug_file(file_key)
            print("-" * 50)
        
        # Load data with error handling
        print("Starting data loading...")
        df = plotter.load_data_from_s3(files)
        
        if df.empty:
            print("No valid data found! Check the error messages above for details.")
            return None
        
        print(f"Data loaded successfully: {len(df)} records")
        
        # Generate plots and stats
        try:
            plotter.generate_summary_stats(df)
        except Exception as e:
            print(f"Error generating summary stats: {e}")
        
        try:
            plotter.plot_metrics_evolution(df)
        except Exception as e:
            print(f"Error creating evolution plots: {e}")
        
        try:
            plotter.plot_daily_patterns(df)
        except Exception as e:
            print(f"Error creating daily pattern plots: {e}")
        
        return df
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        return None
    except Exception as e:
        print(f"Unexpected error during analysis: {e}")
        return None

# Database-based analysis functions
def database_quick_analysis(db_path: str = "air_quality.db", city: str = "Barcelona", 
                           days: int = 7, limit: int = None):
    """
    Quick analysis function using the database
    
    Args:
        db_path: Path to the SQLite database
        city: City name to analyze
        days: Number of recent days to analyze
        limit: Maximum number of records to retrieve
    """
    try:
        plotter = DatabaseAirQualityPlotter(db_path)
        
        # Load data from database
        df = plotter.load_data_from_db(city=city, days=days, limit=limit)
        
        if df.empty:
            print("No data found in database! Make sure to process S3 files first.")
            return None
        
        # Generate plots and stats
        try:
            plotter.generate_summary_stats(df)
        except Exception as e:
            print(f"Error generating summary stats: {e}")
        
        try:
            plotter.plot_metrics_evolution(df)
        except Exception as e:
            print(f"Error creating evolution plots: {e}")
        
        try:
            plotter.plot_daily_patterns(df)
        except Exception as e:
            print(f"Error creating daily pattern plots: {e}")
        
        return df
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        return None
    except Exception as e:
        print(f"Unexpected error during analysis: {e}")
        return None

def database_latest_analysis(db_path: str = "air_quality.db", city: str = "Barcelona", 
                            hours: int = 24):
    """
    Analyze the most recent data from the database
    
    Args:
        db_path: Path to the SQLite database
        city: City name to analyze
        hours: Number of recent hours to analyze
    """
    try:
        plotter = DatabaseAirQualityPlotter(db_path)
        
        # Load latest data from database
        df = plotter.get_latest_data(city=city, hours=hours)
        
        if df.empty:
            print("No recent data found in database!")
            return None
        
        # Generate plots and stats
        try:
            plotter.generate_summary_stats(df)
        except Exception as e:
            print(f"Error generating summary stats: {e}")
        
        try:
            plotter.plot_metrics_evolution(df)
        except Exception as e:
            print(f"Error creating evolution plots: {e}")
        
        return df
        
    except KeyboardInterrupt:
        print("\nAnalysis interrupted by user.")
        return None
    except Exception as e:
        print(f"Unexpected error during analysis: {e}")
        return None

# Example usage:
if __name__ == "__main__":
    # Replace with your bucket name
    BUCKET_NAME = "air-quality-data-dumps"
    from credentials import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

    s3_client = boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )
    
    # Database-based analysis (recommended)
    print("Starting database-based analysis...")
    df = database_quick_analysis(db_path="air_quality.db", city="Barcelona", days=7)
    
    if df is not None and not df.empty:
        print("Database analysis completed successfully!")
        print("You can also try:")
        print("df = database_latest_analysis(db_path='air_quality.db', city='Barcelona', hours=24)")
    else:
        print("Database analysis failed. Make sure to process S3 files first:")
        print("python process_s3_to_db.py --city Barcelona --limit 100")
    
    # Original S3-based analysis (uncomment if needed)
    # print("Starting S3-based analysis...")
    # df = quick_analysis(BUCKET_NAME, s3_client, days_limit=7)