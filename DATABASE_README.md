# Air Quality Database System

This system processes S3 air quality files into a SQLite database and provides plotting capabilities.

## Features

- **SQLite Database**: Stores air quality data with proper indexing and duplicate handling
- **Duplicate Management**: Handles duplicate values per hour using unique constraints
- **Proper Timestamps**: Uses `data["data"]["time"]["iso"]` as the primary timestamp
- **Database-based Plotting**: Fast plotting from pre-processed database
- **Multiple Cities**: Support for different cities (Barcelona, Madrid, etc.)

## Files

- `database_manager.py`: Core database operations
- `process_s3_to_db.py`: Script to process S3 files into database
- `plotData.py`: Updated plotting functions (both S3 and database-based)
- `test_database.py`: Test script for database functionality

## Quick Start

### 1. Process S3 Files to Database

```bash
# Process Barcelona data (last 100 files)
python process_s3_to_db.py --city Barcelona --limit 100

# Process all Barcelona files
python process_s3_to_db.py --city Barcelona

# Process different city
python process_s3_to_db.py --city Madrid --limit 50
```

### 2. Analyze Data from Database

```bash
# Run database-based analysis
python plotData.py
```

### 3. Test Database System

```bash
# Test database functionality
python test_database.py
```

## Database Schema

The `air_quality_data` table includes:

- `id`: Primary key
- `city`: City name (Barcelona, Madrid, etc.)
- `timestamp`: ISO timestamp from `data["data"]["time"]["iso"]`
- `hour_key`: Unique key for duplicate handling (city + hour)
- `aqi`: Air Quality Index
- `dominant_pollutant`: Dominant pollutant
- `pm25`, `pm10`, `no2`, `o3`, `so2`, `co`: Pollutant concentrations
- `t`, `h`, `p`, `w`: Temperature, humidity, pressure, wind
- `created_at`: Record creation timestamp

## Key Features

### Duplicate Handling
- Uses `hour_key` (city + hour) to prevent duplicates
- `INSERT OR REPLACE` updates existing records
- Ensures one record per city per hour

### Timestamp Management
- Extracts timestamp from `data["data"]["time"]["iso"]`
- Handles different timestamp formats
- Sorts data with newest first

### Database Functions

#### AirQualityDatabase Class
- `process_s3_bucket()`: Process S3 files to database
- `get_data()`: Retrieve data by city and date range
- `get_latest_data()`: Get most recent data
- `get_database_stats()`: Database statistics

#### DatabaseAirQualityPlotter Class
- `load_data_from_db()`: Load data for plotting
- `plot_metrics_evolution()`: Create comprehensive plots
- `plot_daily_patterns()`: Hourly pattern analysis
- `generate_summary_stats()`: Statistical summary

## Usage Examples

### Process S3 Data
```python
from database_manager import AirQualityDatabase
import boto3

# Initialize database
db = AirQualityDatabase("air_quality.db")

# Initialize S3 client
s3_client = boto3.client('s3', ...)

# Process files
result = db.process_s3_bucket(s3_client, "air-quality-data-dumps", "Barcelona", limit=100)
print(f"Processed: {result}")
```

### Analyze Data
```python
from plotData import database_quick_analysis, database_latest_analysis

# Analyze last 7 days
df = database_quick_analysis(db_path="air_quality.db", city="Barcelona", days=7)

# Analyze last 24 hours
df = database_latest_analysis(db_path="air_quality.db", city="Barcelona", hours=24)
```

### Direct Database Access
```python
from database_manager import AirQualityDatabase

db = AirQualityDatabase("air_quality.db")

# Get data
df = db.get_data(city="Barcelona", days=7, limit=100)

# Get latest data
df = db.get_latest_data(city="Barcelona", hours=24)

# Get statistics
stats = db.get_database_stats()
print(stats)
```

## Command Line Options

### process_s3_to_db.py
- `--bucket`: S3 bucket name (default: air-quality-data-dumps)
- `--city`: City to process (default: Barcelona)
- `--limit`: Maximum files to process
- `--db-path`: Database path (default: air_quality.db)
- `--days`: Recent days to process (default: 30)

### Examples
```bash
# Process recent Barcelona data
python process_s3_to_db.py --city Barcelona --limit 200

# Process Madrid data
python process_s3_to_db.py --city Madrid --limit 100

# Use custom database path
python process_s3_to_db.py --db-path my_air_quality.db --city Barcelona
```

## Performance Benefits

- **Faster Queries**: Indexed database vs. parsing JSON files
- **Duplicate Handling**: Automatic deduplication
- **Flexible Filtering**: Query by city, date range, etc.
- **Persistent Storage**: Data available across sessions
- **Memory Efficient**: Load only needed data

## Migration from S3-based System

The system maintains backward compatibility:

- Original `AirQualityPlotter` class still available
- New `DatabaseAirQualityPlotter` class for database operations
- Both `quick_analysis()` and `database_quick_analysis()` functions available

## Troubleshooting

### No Data Found
```bash
# Check if database has data
python -c "from database_manager import AirQualityDatabase; db = AirQualityDatabase(); print(db.get_database_stats())"

# Process S3 files first
python process_s3_to_db.py --city Barcelona --limit 50
```

### Database Errors
```bash
# Test database functionality
python test_database.py

# Recreate database
rm air_quality.db
python process_s3_to_db.py --city Barcelona --limit 10
```

### JSON Parsing Errors
The system handles malformed JSON files with single quotes automatically using `safe_parse_json()`.
