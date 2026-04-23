# 🏙️ City Comparison Dashboard

A beautiful, interactive city comparison page with radar charts, rankings, and detailed metrics for comparing air quality across multiple Spanish cities.

## ✨ Features

### 🎯 **Radar Charts**
- **Multi-city comparison** with beautiful radar visualization
- **5 key metrics**: AQI, PM2.5, PM10, NO2, O3
- **Color-coded cities** with transparency for overlapping areas
- **Interactive hover** for exact values
- **Normalized scale** (0-100) for fair comparison

### 🏆 **City Rankings**
- **Overall scoring system** based on weighted air quality metrics
- **Top 3 cities** displayed as beautiful cards
- **Complete ranking table** with all metrics
- **Real-time updates** when changing time periods

### 📊 **Detailed Comparisons**
- **Bar charts** for each pollutant (AQI, PM2.5, PM10, NO2, O3)
- **Tabbed interface** for easy metric switching
- **Side-by-side metrics** in data table format
- **Sortable columns** for easy analysis

### 🎨 **Beautiful Design**
- **Gradient backgrounds** with modern color schemes
- **Card-based layout** for clean organization
- **Responsive design** that works on all devices
- **Smooth animations** and hover effects

## 🚀 How to Use

### **1. Launch the Multi-page Dashboard**
```bash
python3 run_multi_page.py
```

### **2. Select City Comparison**
- Click "🏆 City Comparison" button on the main page
- Or navigate directly to the comparison page

### **3. Choose Cities to Compare**
- Select 2-6 cities from the sidebar
- Choose time period (7/30/90 days)
- Cities will be automatically ranked

### **4. Explore the Visualizations**
- **Radar Chart**: See overall air quality patterns
- **Bar Charts**: Compare specific pollutants
- **Rankings**: See which cities have the best air quality
- **Data Table**: View exact values and metrics

## 📊 Scoring System

The city ranking uses a **weighted composite score**:

```
Overall Score = (AQI × 0.4) + (PM2.5 × 0.2) + (PM10 × 0.2) + (NO2 × 0.1) + (O3 × 0.1)
```

- **Lower scores = Better air quality**
- **AQI has highest weight** (40%) as it's the most comprehensive metric
- **Particulate matter** (PM2.5, PM10) has significant weight (20% each)
- **Gas pollutants** (NO2, O3) have lower weight (10% each)

## 🎯 Chart Types

### **1. Radar Chart**
- **Purpose**: Visual comparison across all metrics
- **Best for**: Seeing overall air quality patterns
- **Features**: 
  - Multiple cities overlaid
  - Color-coded with transparency
  - Normalized 0-100 scale
  - Interactive hover details

### **2. Bar Charts**
- **Purpose**: Detailed metric-by-metric comparison
- **Best for**: Analyzing specific pollutants
- **Features**:
  - One chart per pollutant
  - Sorted by performance
  - Color-coded bars
  - Exact values displayed

### **3. Ranking Table**
- **Purpose**: Complete data overview
- **Best for**: Detailed analysis and data export
- **Features**:
  - All metrics in one view
  - Sortable columns
  - Rank indicators
  - Data point counts

## 🏙️ Available Cities

The dashboard supports all Spanish cities from your data collection:

- **Barcelona** - Major metropolitan area
- **Madrid** - Capital city
- **Valencia** - Mediterranean coast
- **Granada** - Andalusian region
- **Sevilla** - Southern Spain
- **Bilbao** - Northern industrial city
- **Malaga** - Costa del Sol
- **Valladolid** - Castile and León
- **Zaragoza** - Aragon region
- **Huelva** - Andalusian coast
- **Soria** - Small city in Castile
- **Gijon** - Asturias region
- **Palma** - Balearic Islands

## 📈 Usage Examples

### **Compare Major Cities**
1. Select: Barcelona, Madrid, Valencia
2. Time period: Last 30 days
3. View radar chart for overall comparison
4. Check bar charts for specific pollutants

### **Regional Analysis**
1. Select: Granada, Sevilla, Malaga (Andalusia)
2. Compare with: Barcelona, Madrid (major cities)
3. Analyze regional air quality patterns

### **Best Air Quality Cities**
1. Select all available cities
2. Check ranking table
3. Identify top performers
4. Analyze what makes them better

## 🎨 Design Features

### **Color Scheme**
- **Primary**: Gradient red to teal (#ff6b6b to #4ecdc4)
- **City colors**: 7 distinct colors for easy identification
- **Status colors**: Green (good) to red (poor) for rankings

### **Layout**
- **Wide layout**: Maximizes chart space
- **Sidebar controls**: Easy city and time selection
- **Card-based design**: Clean separation of content
- **Responsive columns**: Adapts to screen size

### **Interactive Elements**
- **Hover tooltips**: Detailed information on hover
- **Click legends**: Show/hide city data
- **Zoom and pan**: Navigate through charts
- **Real-time updates**: Instant filtering

## 🔧 Technical Details

### **Performance**
- **Data caching**: Fast loading with `@st.cache_data`
- **Efficient queries**: Optimized database access
- **Lazy loading**: Load data only when needed
- **Memory management**: Efficient data processing

### **Data Processing**
- **Automatic normalization**: Fair comparison across metrics
- **Missing data handling**: Graceful degradation
- **Real-time calculation**: Dynamic scoring and ranking
- **Data validation**: Ensure data quality

## 💡 Tips for Best Results

### **City Selection**
- **2-6 cities**: Optimal for radar chart visualization
- **Mix of regions**: Compare different geographic areas
- **Similar sizes**: Fair comparison between cities
- **Time consistency**: Use same time period for all cities

### **Analysis**
- **Start with radar chart**: Get overall picture
- **Drill down with bar charts**: Analyze specific pollutants
- **Check rankings**: Identify best/worst performers
- **Export data**: Download for further analysis

### **Interpretation**
- **Lower scores are better**: For overall ranking
- **Consider context**: Industrial vs. residential areas
- **Time patterns**: Some cities may have seasonal variations
- **Data quality**: More data points = more reliable results

## 🐛 Troubleshooting

### **No Cities Available**
```bash
# Process some cities first
python3 process_s3_to_db.py --city Barcelona --limit 100
python3 process_s3_to_db.py --city Madrid --limit 100
```

### **Charts Not Loading**
1. Check if data exists for selected cities
2. Try different time periods
3. Reduce number of selected cities
4. Check browser console for errors

### **Performance Issues**
1. Reduce number of selected cities
2. Use shorter time periods
3. Clear browser cache
4. Close other applications

## 🎯 Demo

Try the demo to see the features:

```bash
python3 simple_demo.py
```

This shows a sample city comparison with realistic data.

## 🚀 Future Enhancements

- **Historical trends**: Compare cities over time
- **Seasonal analysis**: Month-by-month comparisons
- **Weather correlation**: Include weather data
- **Export functionality**: Download comparison reports
- **Alert system**: Notifications for poor air quality
- **Mobile optimization**: Enhanced mobile experience

---

**Built with ❤️ using Streamlit, Plotly, and modern web technologies**
