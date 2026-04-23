# 🌍 Air Quality Streamlit Dashboard

A beautiful, interactive dashboard for visualizing air quality data with modern design and real-time insights.

## ✨ Features

### 🎨 **Modern Design**
- **Gradient backgrounds** and modern color schemes
- **Responsive layout** that works on all screen sizes
- **Custom CSS styling** for a professional look
- **Interactive elements** with hover effects

### 📊 **Interactive Charts**
- **Real-time AQI Gauge** with color-coded status
- **Time series charts** with multiple pollutants
- **Daily pattern analysis** showing hourly trends
- **Correlation heatmap** for pollutant relationships
- **Zoom and pan** functionality on all charts

### 🎛️ **Interactive Controls**
- **City selector** - Choose from available cities
- **Date range picker** - Last 7/30/90 days or custom range
- **Real-time filtering** - Instant updates when changing parameters
- **Data export** - Download filtered data as CSV

### 📈 **Key Metrics Dashboard**
- **Current AQI** with health status
- **Average AQI** for the selected period
- **Peak AQI** recorded
- **Data points count** for quality assessment

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install streamlit plotly pandas numpy boto3
```

### 2. Prepare Data
```bash
# Process S3 data to database first
python process_s3_to_db.py --city Barcelona --limit 1000
```

### 3. Launch Dashboard
```bash
# Option 1: Use the launcher script (recommended)
python run_dashboard.py

# Option 2: Direct Streamlit command
streamlit run streamlit_app.py
```

### 4. Access Dashboard
- Open your browser to `http://localhost:8501`
- The dashboard will automatically open in your default browser

## 📱 Dashboard Sections

### 🎯 **Current Air Quality Status**
- **AQI Gauge**: Visual gauge showing current air quality
- **Health Status**: Color-coded health recommendations
- **AQI Scale**: Reference guide for air quality levels

### 📊 **Key Metrics**
- **Current AQI**: Latest air quality reading
- **Average AQI**: Mean value for selected period
- **Peak AQI**: Highest recorded value
- **Data Points**: Number of measurements available

### 📈 **Air Quality Trends**
- **Multi-panel time series** showing:
  - Air Quality Index over time
  - Particulate Matter (PM2.5, PM10)
  - Gas Pollutants (NO2, O3, SO2, CO)
  - Weather data (Temperature, Humidity)

### 🕐 **Daily Patterns**
- **Hourly averages** showing daily pollution patterns
- **AQI daily pattern** - when air quality is best/worst
- **Pollutant patterns** - hourly variations by pollutant type

### 🔗 **Pollutant Correlations**
- **Heatmap visualization** showing relationships between pollutants
- **Color-coded correlations** (red = positive, blue = negative)
- **Interactive hover** for exact correlation values

### 📋 **Data Table**
- **Recent measurements** in tabular format
- **Sortable columns** for easy data exploration
- **Download functionality** for data export

## 🎛️ Controls & Filters

### **Sidebar Controls**
- **City Selection**: Choose from available cities in database
- **Time Period**: Quick selection (7/30/90 days) or custom range
- **Date Range**: Custom start/end date selection
- **Real-time Updates**: All charts update instantly when filters change

### **Interactive Features**
- **Chart Zoom**: Click and drag to zoom into specific time periods
- **Hover Details**: Hover over data points for exact values
- **Legend Toggle**: Click legend items to show/hide data series
- **Download Charts**: Right-click charts to save as images

## 🎨 Design Features

### **Color Scheme**
- **Primary**: Gradient blues and purples (#667eea to #764ba2)
- **Status Colors**: 
  - Green: Good air quality (0-50 AQI)
  - Yellow: Moderate (51-100 AQI)
  - Orange: Unhealthy for sensitive groups (101-150 AQI)
  - Red: Unhealthy (151-200 AQI)
  - Purple: Very unhealthy (201-300 AQI)
  - Maroon: Hazardous (300+ AQI)

### **Typography**
- **Headers**: Large, bold gradient text
- **Metrics**: Prominent numbers with descriptive labels
- **Body**: Clean, readable fonts with proper contrast

### **Layout**
- **Wide layout**: Maximizes screen real estate
- **Responsive columns**: Adapts to different screen sizes
- **Card-based design**: Clean separation of content sections
- **Consistent spacing**: Professional, organized appearance

## 📊 Data Visualization

### **Chart Types**
1. **Gauge Chart**: Current AQI with color-coded zones
2. **Line Charts**: Time series with multiple pollutants
3. **Scatter Plots**: Data points with trend lines
4. **Heatmap**: Correlation matrix with color intensity
5. **Multi-panel Layout**: Organized subplot arrangement

### **Interactive Elements**
- **Zoom & Pan**: Navigate through time periods
- **Hover Tooltips**: Detailed information on hover
- **Legend Controls**: Show/hide data series
- **Responsive Design**: Adapts to screen size

## 🔧 Technical Details

### **Performance Optimizations**
- **Data Caching**: `@st.cache_data` for fast loading
- **Efficient Queries**: Optimized database access
- **Lazy Loading**: Load data only when needed
- **Memory Management**: Efficient data processing

### **Browser Compatibility**
- **Modern Browsers**: Chrome, Firefox, Safari, Edge
- **Mobile Responsive**: Works on tablets and phones
- **JavaScript Required**: For interactive features

## 🛠️ Customization

### **Adding New Cities**
1. Process data for new city:
   ```bash
   python process_s3_to_db.py --city "NewCity" --limit 1000
   ```
2. Restart dashboard - city will appear automatically

### **Modifying Charts**
- Edit `streamlit_app.py` to customize chart appearance
- Modify color schemes in chart creation functions
- Add new chart types by extending the visualization functions

### **Styling Changes**
- Modify CSS in the `st.markdown()` section
- Change color schemes by updating CSS variables
- Adjust layout by modifying column configurations

## 🐛 Troubleshooting

### **Dashboard Won't Start**
```bash
# Check dependencies
pip install streamlit plotly pandas numpy boto3

# Check database exists
ls -la air_quality.db

# Check database has data
python -c "from database_manager import AirQualityDatabase; db = AirQualityDatabase(); print(db.get_database_stats())"
```

### **No Data Showing**
1. **Check database**: Ensure `air_quality.db` exists and has data
2. **Process data**: Run `python process_s3_to_db.py --city Barcelona --limit 100`
3. **Check date range**: Ensure selected date range has data
4. **Check city**: Verify city name matches database records

### **Charts Not Loading**
1. **Check Plotly**: Ensure Plotly is installed correctly
2. **Browser console**: Check for JavaScript errors
3. **Data format**: Verify data is in correct format
4. **Memory issues**: Try reducing date range or data size

### **Performance Issues**
1. **Reduce date range**: Use shorter time periods
2. **Limit data**: Process fewer files initially
3. **Browser cache**: Clear browser cache and reload
4. **System resources**: Close other applications

## 📈 Usage Examples

### **Daily Monitoring**
- Set time period to "Last 7 days"
- Monitor current AQI and trends
- Check daily patterns for planning outdoor activities

### **Historical Analysis**
- Use custom date range for specific periods
- Analyze correlation between pollutants
- Export data for further analysis

### **Multi-City Comparison**
- Switch between cities to compare air quality
- Use same date ranges for fair comparison
- Download data for external analysis

## 🎯 Best Practices

1. **Start Small**: Begin with 7-30 days of data
2. **Regular Updates**: Process new data regularly
3. **Monitor Performance**: Watch for slow loading times
4. **Export Data**: Download data for backup/analysis
5. **Share Insights**: Use screenshots for reports

## 🔮 Future Enhancements

- **Real-time Updates**: Live data streaming
- **Alerts System**: Notifications for poor air quality
- **Mobile App**: Native mobile application
- **API Integration**: REST API for data access
- **Advanced Analytics**: Machine learning predictions
- **Social Features**: Share air quality reports

---

**Built with ❤️ using Streamlit, Plotly, and modern web technologies**
