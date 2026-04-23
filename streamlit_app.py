import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import sqlite3
from database_manager import AirQualityDatabase
import os

# Consistent color mapping for all cities across all charts
CITY_COLORS = {
    'Barcelona': '#ff6b6b',
    'Bilbao': '#4ecdc4', 
    'Gijon': '#45b7d1',
    'Granada': '#96ceb4',
    'Huelva': '#feca57',
    'Madrid': '#ff9ff3',
    'Malaga': '#54a0ff',
    'Palma': '#ffa726',
    'Sevilla': '#ab47bc',
    'Soria': '#26a69a',
    'Valencia': '#66bb6a',
    'Valladolid': '#ef5350',
    'Zaragoza': '#42a5f5'
}

def get_city_color(city):
    """Get consistent color for a city"""
    return CITY_COLORS.get(city, '#95a5a6')  # Default gray for unknown cities

# Page configuration
st.set_page_config(
    page_title="🌍 Air Quality Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
        margin: 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stSelectbox > div > div {
        background-color: #f0f2f6;
        border-radius: 5px;
    }
    
    .stDateInput > div > div {
        background-color: #f0f2f6;
        border-radius: 5px;
    }
    
    .chart-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 1rem 0;
    }
    
    .status-good { color: #28a745; }
    .status-moderate { color: #ffc107; }
    .status-unhealthy { color: #fd7e14; }
    .status-very-unhealthy { color: #dc3545; }
    .status-hazardous { color: #6f42c1; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data_from_db(city="Barcelona", days=30):
    """Load data from database with caching"""
    try:
        db = AirQualityDatabase("air_quality.db")
        df = db.get_data(city=city, days=days)
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

@st.cache_data
def get_available_cities():
    """Get list of available cities from database"""
    try:
        db = AirQualityDatabase("air_quality.db")
        stats = db.get_database_stats()
        return list(stats.get('city_counts', {}).keys())
    except:
        return ["Barcelona", "Madrid", "Valencia", "Granada", "Sevilla"]

def get_aqi_status(aqi):
    """Get AQI status and color"""
    if pd.isna(aqi):
        return "Unknown", "status-unknown"
    elif aqi <= 50:
        return "Good", "status-good"
    elif aqi <= 100:
        return "Moderate", "status-moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "status-unhealthy"
    elif aqi <= 200:
        return "Unhealthy", "status-very-unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy", "status-very-unhealthy"
    else:
        return "Hazardous", "status-hazardous"

def create_aqi_gauge(current_aqi, target_aqi=50):
    """Create AQI gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = current_aqi,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Current AQI"},
        delta = {'reference': target_aqi},
        gauge = {
            'axis': {'range': [None, 500]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgreen"},
                {'range': [50, 100], 'color': "yellow"},
                {'range': [100, 150], 'color': "orange"},
                {'range': [150, 200], 'color': "red"},
                {'range': [200, 500], 'color': "darkred"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 100
            }
        }
    ))
    
    fig.update_layout(
        height=300,
        font={'color': "darkblue", 'family': "Arial Black"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def create_time_series_chart(df, pollutants=['aqi', 'pm25', 'pm10', 'no2', 'o3']):
    """Create interactive time series chart"""
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Air Quality Index', 'Particulate Matter', 'Gas Pollutants', 'Weather'),
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": True}]]
    )
    
    # AQI
    if 'aqi' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['aqi'], 
                      mode='lines+markers', name='AQI',
                      line=dict(color='#667eea', width=3),
                      marker=dict(size=6)),
            row=1, col=1
        )
    
    # Particulate Matter
    if 'pm25' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['pm25'], 
                      mode='lines+markers', name='PM2.5',
                      line=dict(color='#e74c3c', width=2)),
            row=1, col=2
        )
    if 'pm10' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['pm10'], 
                      mode='lines+markers', name='PM10',
                      line=dict(color='#c0392b', width=2)),
            row=1, col=2
        )
    
    # Gas Pollutants
    gas_colors = {'no2': '#f39c12', 'o3': '#27ae60', 'so2': '#8e44ad', 'co': '#34495e'}
    for gas in ['no2', 'o3', 'so2', 'co']:
        if gas in df.columns:
            fig.add_trace(
                go.Scatter(x=df['timestamp'], y=df[gas], 
                          mode='lines+markers', name=gas.upper(),
                          line=dict(color=gas_colors[gas], width=2)),
                row=2, col=1
            )
    
    # Weather (Temperature and Humidity)
    if 't' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['t'], 
                      mode='lines+markers', name='Temperature (°C)',
                      line=dict(color='#e67e22', width=2)),
            row=2, col=2
        )
    if 'h' in df.columns:
        fig.add_trace(
            go.Scatter(x=df['timestamp'], y=df['h'], 
                      mode='lines+markers', name='Humidity (%)',
                      line=dict(color='#3498db', width=2)),
            row=2, col=2, secondary_y=True
        )
    
    fig.update_layout(
        height=600,
        showlegend=True,
        title_text="Air Quality Metrics Over Time",
        title_font_size=20,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    # Update axes
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_xaxes(title_text="Time", row=2, col=2)
    fig.update_yaxes(title_text="AQI", row=1, col=1)
    fig.update_yaxes(title_text="μg/m³", row=1, col=2)
    fig.update_yaxes(title_text="Concentration", row=2, col=1)
    fig.update_yaxes(title_text="Temperature (°C)", row=2, col=2)
    fig.update_yaxes(title_text="Humidity (%)", row=2, col=2, secondary_y=True)
    
    return fig

def create_daily_patterns_chart(df):
    """Create daily patterns chart"""
    if df.empty:
        return go.Figure()
    
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
    
    fig = make_subplots(
        rows=1, cols=2,
        subplot_titles=('AQI Daily Pattern', 'Pollutants Daily Pattern')
    )
    
    # AQI pattern
    fig.add_trace(
        go.Scatter(x=hourly_means['hour'], y=hourly_means['aqi'], 
                  mode='lines+markers', name='AQI',
                  line=dict(color='#667eea', width=3),
                  marker=dict(size=8)),
        row=1, col=1
    )
    
    # Pollutants pattern
    pollutants = ['pm25', 'pm10', 'no2', 'o3']
    colors = ['#e74c3c', '#c0392b', '#f39c12', '#27ae60']
    for pollutant, color in zip(pollutants, colors):
        if pollutant in hourly_means.columns:
            fig.add_trace(
                go.Scatter(x=hourly_means['hour'], y=hourly_means[pollutant], 
                          mode='lines+markers', name=pollutant.upper(),
                          line=dict(color=color, width=2)),
                row=1, col=2
            )
    
    fig.update_layout(
        height=400,
        title_text="Daily Patterns by Hour",
        title_font_size=18,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    fig.update_xaxes(title_text="Hour of Day", row=1, col=1)
    fig.update_xaxes(title_text="Hour of Day", row=1, col=2)
    fig.update_yaxes(title_text="Average AQI", row=1, col=1)
    fig.update_yaxes(title_text="Average Concentration", row=1, col=2)
    
    return fig

def create_correlation_heatmap(df):
    """Create correlation heatmap"""
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    correlation_matrix = df[numeric_cols].corr()
    
    fig = px.imshow(
        correlation_matrix,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Pollutant Correlation Matrix"
    )
    
    fig.update_layout(
        height=500,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

def main():
    # Header
    st.markdown('<h1 class="main-header">🌍 Air Quality Dashboard</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.markdown("## 🎛️ Controls")
    
    # City selection
    available_cities = get_available_cities()
    selected_city = st.sidebar.selectbox(
        "Select City",
        available_cities,
        index=0
    )
    
    # Date range selection
    st.sidebar.markdown("### 📅 Date Range")
    date_range = st.sidebar.selectbox(
        "Time Period",
        ["Last 7 days", "Last 30 days", "Last 90 days", "Custom"],
        index=1
    )
    
    if date_range == "Custom":
        start_date = st.sidebar.date_input("Start Date", value=datetime.now() - timedelta(days=30))
        end_date = st.sidebar.date_input("End Date", value=datetime.now())
        days = (end_date - start_date).days
    else:
        days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
        days = days_map[date_range]
    
    # Load data
    with st.spinner(f"Loading data for {selected_city}..."):
        df = load_data_from_db(city=selected_city, days=days)
    
    if df.empty:
        st.error("No data available for the selected criteria. Please check your database or try different parameters.")
        return
    
    # Convert timestamp to datetime if it's not already
    if not pd.api.types.is_datetime64_any_dtype(df['timestamp']):
        df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Filter by date range if custom
    if date_range == "Custom":
        df = df[(df['timestamp'].dt.date >= start_date) & (df['timestamp'].dt.date <= end_date)]
    
    # Key Metrics
    st.markdown("## 📊 Key Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_aqi = df['aqi'].iloc[0] if not df.empty else 0
        aqi_status, aqi_class = get_aqi_status(current_aqi)
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{current_aqi:.0f}</p>
            <p class="metric-label">Current AQI</p>
            <p class="metric-label {aqi_class}">{aqi_status}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        avg_aqi = df['aqi'].mean() if not df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{avg_aqi:.1f}</p>
            <p class="metric-label">Average AQI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        max_aqi = df['aqi'].max() if not df.empty else 0
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{max_aqi:.0f}</p>
            <p class="metric-label">Peak AQI</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        data_points = len(df)
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{data_points}</p>
            <p class="metric-label">Data Points</p>
        </div>
        """, unsafe_allow_html=True)
    
    # AQI Gauge
    st.markdown("## 🎯 Current Air Quality Status")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.plotly_chart(create_aqi_gauge(current_aqi), use_container_width=True)
    
    with col2:
        st.markdown("### 📈 AQI Scale")
        st.markdown("""
        - **0-50**: Good (Green) - Air quality is satisfactory
        - **51-100**: Moderate (Yellow) - Sensitive people may experience minor issues
        - **101-150**: Unhealthy for Sensitive Groups (Orange) - Children and elderly should limit outdoor activities
        - **151-200**: Unhealthy (Red) - Everyone may experience health effects
        - **201-300**: Very Unhealthy (Purple) - Health warnings of emergency conditions
        - **301+**: Hazardous (Maroon) - Everyone should avoid outdoor activities
        """)
    
    # Time Series Charts
    st.markdown("## 📈 Air Quality Trends")
    st.plotly_chart(create_time_series_chart(df), use_container_width=True)
    
    # Daily Patterns
    st.markdown("## 🕐 Daily Patterns")
    st.plotly_chart(create_daily_patterns_chart(df), use_container_width=True)
    
    # Correlation Analysis
    st.markdown("## 🔗 Pollutant Correlations")
    st.plotly_chart(create_correlation_heatmap(df), use_container_width=True)
    
    # Data Table
    st.markdown("## 📋 Recent Data")
    
    # Show recent data with selected columns
    display_cols = ['timestamp', 'aqi', 'dominant_pollutant']
    available_pollutants = ['pm25', 'pm10', 'no2', 'o3', 'so2', 'co', 't', 'h']
    for col in available_pollutants:
        if col in df.columns:
            display_cols.append(col)
    
    recent_data = df[display_cols].head(20)
    st.dataframe(recent_data, use_container_width=True)
    
    # Download button
    csv = df.to_csv(index=False)
    st.download_button(
        label="📥 Download Data as CSV",
        data=csv,
        file_name=f"air_quality_{selected_city}_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🌍 Air Quality Dashboard | Data from World Air Quality Index API</p>
        <p>Built with ❤️ using Streamlit and Plotly</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
