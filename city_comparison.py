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
    'Zaragoza': '#42a5f5',
    # Reference locations
    'Amazon Rainforest': '#2ecc71',  # Green for excellent air quality
    'Jakarta': '#e74c3c'             # Red for poor air quality
}

def get_city_color(city):
    """Get consistent color for a city"""
    return CITY_COLORS.get(city, '#95a5a6')  # Default gray for unknown cities

# Page configuration
st.set_page_config(
    page_title="🏙️ City Comparison - Air Quality Dashboard",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for city comparison page
st.markdown("""
<style>
    .comparison-header {
        font-size: 2.5rem;
        font-weight: 700;
        background: linear-gradient(90deg, #ff6b6b 0%, #4ecdc4 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .city-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    .city-name {
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
    }
    
    .city-score {
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0.5rem 0;
    }
    
    .city-rank {
        font-size: 1rem;
        opacity: 0.9;
    }
    
    .comparison-metric {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .metric-title {
        font-weight: bold;
        color: #333;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        font-size: 1.2rem;
        color: #667eea;
        font-weight: bold;
    }
    
    .ranking-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
        margin: 0.25rem;
    }
    
    .rank-1 { background: #ffd700; color: #333; }
    .rank-2 { background: #c0c0c0; color: #333; }
    .rank-3 { background: #cd7f32; color: white; }
    .rank-other { background: #e0e0e0; color: #666; }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_all_cities_data(days=30):
    """Load data for all cities from database"""
    try:
        db = AirQualityDatabase("air_quality.db")
        stats = db.get_database_stats()
        available_cities = list(stats['city_counts'].keys())
        
        all_data = {}
        for city in available_cities:
            df = db.get_data(city=city, days=days, limit=1000)
            if not df.empty:
                # Convert numeric columns to proper types, handling mixed string/int data
                numeric_columns = ['aqi', 'pm25', 'pm10', 'no2', 'o3']
                for col in numeric_columns:
                    if col in df.columns:
                        # Convert to numeric, coercing errors to NaN, then fill NaN with 0
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                all_data[city] = df
        
        return all_data
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {}

def calculate_city_scores(data_dict):
    """Calculate air quality scores for each city"""
    scores = {}
    
    for city, df in data_dict.items():
        if df.empty:
            continue
        
        # Convert numeric columns to proper types, handling mixed string/int data
        numeric_columns = ['aqi', 'pm25', 'pm10', 'no2', 'o3']
        for col in numeric_columns:
            if col in df.columns:
                # Convert to numeric, coercing errors to NaN, then fill NaN with 0
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
        # Calculate average values
        avg_aqi = df['aqi'].mean() if 'aqi' in df.columns else 0
        avg_pm25 = df['pm25'].mean() if 'pm25' in df.columns else 0
        avg_pm10 = df['pm10'].mean() if 'pm10' in df.columns else 0
        avg_no2 = df['no2'].mean() if 'no2' in df.columns else 0
        avg_o3 = df['o3'].mean() if 'o3' in df.columns else 0
        
        # Calculate composite score (lower is better)
        # Weighted average with AQI having highest weight
        score = (avg_aqi * 0.4 + avg_pm25 * 0.2 + avg_pm10 * 0.2 + 
                avg_no2 * 0.1 + avg_o3 * 0.1)
        
        scores[city] = {
            'score': score,
            'aqi': avg_aqi,
            'pm25': avg_pm25,
            'pm10': avg_pm10,
            'no2': avg_no2,
            'o3': avg_o3,
            'data_points': len(df)
        }
    
    return scores

def create_radar_chart(cities_data, selected_cities):
    """Create radar chart comparing selected cities with fixed normalization scales"""
    if not selected_cities or len(selected_cities) < 2:
        return go.Figure()
    
    # Define categories
    categories = ['AQI', 'PM2.5', 'PM10', 'NO2', 'O3']
    
    # Fixed scales based on maximum values including reference locations (with 20% padding)
    # Reference locations: Amazon Rainforest (excellent air quality) and Jakarta (poor air quality)
    # Spanish cities: aqi: 52.1 (Sevilla), pm25: 51.9 (Sevilla), pm10: 22.5 (Malaga), no2: 14.4 (Granada), o3: 25.5 (Granada)
    # Jakarta: aqi: ~150, pm25: ~80, pm10: ~120, no2: ~60, o3: ~40
    fixed_scales = {
        'aqi': 180,     # Jakarta ~150 * 1.2
        'pm25': 96,     # Jakarta ~80 * 1.2
        'pm10': 144,    # Jakarta ~120 * 1.2
        'no2': 72,      # Jakarta ~60 * 1.2
        'o3': 48        # Jakarta ~40 * 1.2
    }
    
    fig = go.Figure()
    
    # Add reference locations first (so they appear in the background)
    reference_locations = {
        'Amazon Rainforest': {'aqi': 15, 'pm25': 8, 'pm10': 12, 'no2': 2, 'o3': 8},
        'Jakarta': {'aqi': 150, 'pm25': 80, 'pm10': 120, 'no2': 60, 'o3': 40}
    }
    
    for ref_name, ref_data in reference_locations.items():
        values = [ref_data['aqi'], ref_data['pm25'], ref_data['pm10'], ref_data['no2'], ref_data['o3']]
        
        # Normalize values using fixed scales (0-100 scale)
        normalized_values = []
        for j, (value, metric) in enumerate(zip(values, ['aqi', 'pm25', 'pm10', 'no2', 'o3'])):
            max_scale = fixed_scales[metric]
            normalized = min((value / max_scale) * 100, 100)
            normalized_values.append(normalized)
        
        # Create hover text with real values
        hover_text = []
        for j, (value, metric) in enumerate(zip(values, ['AQI', 'PM2.5', 'PM10', 'NO2', 'O3'])):
            hover_text.append(f"{metric}: {value:.1f}")
        
        ref_color = get_city_color(ref_name)
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            name=ref_name,
            line_color=ref_color,
            fillcolor=ref_color,
            opacity=0.2,  # Lower opacity for reference locations
            line=dict(dash='dash'),  # Dashed line for reference
            hovertemplate='<b>%{fullData.name}</b> (Reference)<br>' +
                         '%{theta}: %{customdata}<br>' +
                         'Normalized: %{r:.1f}%<br>' +
                         '<extra></extra>',
            customdata=hover_text
        ))
    
    # Add selected cities
    for i, city in enumerate(selected_cities):
        if city not in cities_data:
            continue
            
        data = cities_data[city]
        values = [
            data['aqi'],
            data['pm25'],
            data['pm10'],
            data['no2'],
            data['o3']
        ]
        
        # Normalize values using fixed scales (0-100 scale)
        normalized_values = []
        for j, (value, metric) in enumerate(zip(values, ['aqi', 'pm25', 'pm10', 'no2', 'o3'])):
            max_scale = fixed_scales[metric]
            normalized = min((value / max_scale) * 100, 100)
            normalized_values.append(normalized)
        
        # Create hover text with real values
        hover_text = []
        for j, (value, metric) in enumerate(zip(values, ['AQI', 'PM2.5', 'PM10', 'NO2', 'O3'])):
            hover_text.append(f"{metric}: {value:.1f}")
        
        city_color = get_city_color(city)
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            name=city,
            line_color=city_color,
            fillcolor=city_color,
            opacity=0.3,
            hovertemplate='<b>%{fullData.name}</b><br>' +
                         '%{theta}: %{customdata}<br>' +
                         'Normalized: %{r:.1f}%<br>' +
                         '<extra></extra>',
            customdata=hover_text
        ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickmode='linear',
                tick0=0,
                dtick=20,
                tickfont=dict(size=12),
                gridcolor='rgba(255,255,255,0.3)'
            )),
        showlegend=True,
        title="Air Quality Comparison - Normalized Radar Chart<br><sub>Values normalized to 0-100% scale for fair comparison</sub>",
        title_font_size=18,
        height=600,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig

def create_comparison_bar_chart(cities_data, selected_cities, metric='aqi'):
    """Create bar chart comparing cities for a specific metric"""
    if not selected_cities:
        return go.Figure()
    
    cities = []
    values = []
    colors = []
    
    # Sort cities by metric value
    sorted_cities = sorted(selected_cities, key=lambda x: cities_data.get(x, {}).get(metric, 0))
    
    for city in sorted_cities:
        if city in cities_data:
            cities.append(city)
            values.append(cities_data[city][metric])
            colors.append(get_city_color(city))
    
    fig = go.Figure(data=[
        go.Bar(
            x=cities,
            y=values,
            marker_color=colors,
            text=[f"{v:.1f}" for v in values],
            textposition='auto',
        )
    ])
    
    metric_names = {
        'aqi': 'Air Quality Index',
        'pm25': 'PM2.5 (μg/m³)',
        'pm10': 'PM10 (μg/m³)',
        'no2': 'NO2 (μg/m³)',
        'o3': 'O3 (μg/m³)'
    }
    
    fig.update_layout(
        title=f"City Comparison - {metric_names.get(metric, metric.upper())}",
        xaxis_title="Cities",
        yaxis_title=metric_names.get(metric, metric.upper()),
        height=400,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig


def main():
    # Header
    st.markdown('<h1 class="comparison-header">🏙️ City Comparison Dashboard</h1>', unsafe_allow_html=True)
    
    # Air Quality Indicators Information
    st.markdown("## 📊 Air Quality Indicators")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        **🌡️ AQI (Air Quality Index)**
        - **What it measures**: Overall air quality based on multiple pollutants
        - **Scale**: 0-500 (0-50 Good, 51-100 Moderate, 101-150 Unhealthy for Sensitive Groups, 151-200 Unhealthy, 201-300 Very Unhealthy, 301-500 Hazardous)
        - **Health impact**: Higher values indicate increased health risks
        
        **💨 PM2.5 (Fine Particulate Matter)**
        - **What it measures**: Particles smaller than 2.5 micrometers in diameter
        - **Sources**: Vehicle emissions, industrial processes, wildfires, dust
        - **Health impact**: Can penetrate deep into lungs, cause respiratory and cardiovascular problems
        - **WHO Guideline**: < 15 μg/m³ (annual), < 25 μg/m³ (24-hour)
        
        **🌫️ PM10 (Coarse Particulate Matter)**
        - **What it measures**: Particles smaller than 10 micrometers in diameter
        - **Sources**: Dust, pollen, mold spores, construction activities
        - **Health impact**: Can irritate eyes, nose, throat, and lungs
        - **WHO Guideline**: < 45 μg/m³ (annual), < 50 μg/m³ (24-hour)
        """)
    
    with col2:
        st.markdown("""
        **🚗 NO2 (Nitrogen Dioxide)**
        - **What it measures**: Reddish-brown gas from combustion processes
        - **Sources**: Vehicle emissions, power plants, industrial facilities
        - **Health impact**: Can cause respiratory problems, especially in asthmatics
        - **WHO Guideline**: < 25 μg/m³ (annual), < 200 μg/m³ (1-hour)
        
        **☀️ O3 (Ozone)**
        - **What it measures**: Ground-level ozone (not the protective ozone layer)
        - **Sources**: Chemical reactions between NOx and VOCs in sunlight
        - **Health impact**: Can cause breathing problems, reduce lung function
        - **WHO Guideline**: < 100 μg/m³ (8-hour average)
        
        **📈 Reference Locations**
        - **🌿 Amazon Rainforest**: Pristine air quality baseline
        - **🏙️ Jakarta**: Major city with significant air pollution challenges
        """)
    
    # Sidebar
    st.sidebar.markdown("## 🎛️ Comparison Controls")
    
    # Time period selection
    time_period = st.sidebar.selectbox(
        "Time Period",
        ["Last 7 days", "Last 30 days", "Last 90 days"],
        index=1
    )
    
    days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
    days = days_map[time_period]
    
    # Load data
    with st.spinner("Loading city data..."):
        all_cities_data = load_all_cities_data(days=days)
    
    if not all_cities_data:
        st.error("No city data available. Please process some cities first.")
        return
    
    available_cities = list(all_cities_data.keys())
    st.sidebar.markdown(f"**Available Cities:** {len(available_cities)}")
    
    # City selection
    st.sidebar.markdown("### 🏙️ Select Cities to Compare")
    selected_cities = st.sidebar.multiselect(
        "Choose cities (2-6 recommended)",
        available_cities,
        default=available_cities[:3] if len(available_cities) >= 3 else available_cities
    )
    
    # Calculate scores
    cities_scores = calculate_city_scores(all_cities_data)
    
    # Comparison Charts
    if len(selected_cities) >= 2:
        st.markdown("## 📈 City Comparison Charts")
        
        # Radar Chart
        st.markdown("### 🎯 Air Quality Radar Comparison")
        radar_fig = create_radar_chart(cities_scores, selected_cities)
        st.plotly_chart(radar_fig, use_container_width=True)
        
        # Info about normalization
        st.info("""
        **📊 About the Radar Chart:**
        
        The radar chart includes **reference locations** and uses **expanded scales** for global context:
        - **AQI**: 0-180 (Jakarta reference: ~150)
        - **PM2.5**: 0-96 μg/m³ (Jakarta reference: ~80)
        - **PM10**: 0-144 μg/m³ (Jakarta reference: ~120)
        - **NO2**: 0-72 μg/m³ (Jakarta reference: ~60)
        - **O3**: 0-48 μg/m³ (Jakarta reference: ~40)
        
        **Reference Locations:**
        - 🌿 **Amazon Rainforest** (dashed green): Excellent air quality baseline
        - 🏙️ **Jakarta** (dashed red): Poor air quality reference
        
        - Each metric is scaled to a 0-100% range using these global reference maximums
        - **Lower percentages = Better air quality** for all metrics
        - Spanish cities now appear smaller, showing they have relatively good air quality globally
        - Hover over the chart to see both real values and normalized percentages
        """)
        
        # Bar Charts for different metrics
        st.markdown("### 📊 Detailed Metric Comparison")
        
        metrics = ['aqi', 'pm25', 'pm10', 'no2', 'o3']
        metric_names = {
            'aqi': 'Air Quality Index',
            'pm25': 'PM2.5',
            'pm10': 'PM10',
            'no2': 'NO2',
            'o3': 'O3'
        }
        
        # Create tabs for different metrics
        tabs = st.tabs([metric_names[metric].upper() for metric in metrics])
        
        for i, metric in enumerate(metrics):
            with tabs[i]:
                bar_fig = create_comparison_bar_chart(cities_scores, selected_cities, metric)
                st.plotly_chart(bar_fig, use_container_width=True)
    
    else:
        st.info("Please select at least 2 cities to see comparison charts.")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 2rem;'>
        <p>🏙️ City Comparison Dashboard | Compare air quality across Spanish cities</p>
        <p>Built with ❤️ using Streamlit and Plotly</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
