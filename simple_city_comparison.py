import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from database_manager import AirQualityDatabase

# Page configuration
st.set_page_config(
    page_title="🏙️ City Air Quality Comparison",
    page_icon="🏙️",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main > div {
        padding-top: 2rem;
    }
    
    .stMetric {
        background-color: rgba(248, 249, 250, 0.8);
        border: 1px solid rgba(52, 73, 94, 0.2);
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .stMetric > div {
        text-align: center;
    }
    
    .stMetric label {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #2c3e50 !important;
    }
    
    .stMetric [data-testid="metric-value"] {
        font-size: 2rem !important;
        font-weight: 700 !important;
        color: #e74c3c !important;
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: rgba(248, 249, 250, 0.8);
        border: 1px solid rgba(52, 73, 94, 0.2);
        border-radius: 8px 8px 0 0;
        padding: 0.5rem 1rem;
        font-weight: 600;
    }
    
    .stTabs [aria-selected="true"] {
        background-color: #3498db;
        color: white;
    }
    
    h1 {
        text-align: center;
        color: #2c3e50;
        margin-bottom: 2rem;
    }
    
    h2 {
        color: #2c3e50;
        border-bottom: 2px solid #3498db;
        padding-bottom: 0.5rem;
    }
    
    h3 {
        color: #34495e;
    }
</style>
""", unsafe_allow_html=True)

# Consistent color mapping for all cities
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
    'Amazon Rainforest': '#2ecc71',
    'Jakarta': '#e74c3c'
}

def get_city_color(city):
    """Get consistent color for a city"""
    return CITY_COLORS.get(city, '#95a5a6')

@st.cache_data
def load_city_data(days=30):
    """Load data for all cities from database"""
    try:
        db = AirQualityDatabase("air_quality.db")
        stats = db.get_database_stats()
        available_cities = list(stats['city_counts'].keys())
        
        all_data = {}
        for city in available_cities:
            df = db.get_data(city=city, days=days, limit=1000)
            if not df.empty:
                # Convert numeric columns to proper types
                numeric_columns = ['aqi', 'pm25', 'pm10', 'no2', 'o3']
                for col in numeric_columns:
                    if col in df.columns:
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
        
        # Calculate average values
        avg_aqi = df['aqi'].mean() if 'aqi' in df.columns else 0
        avg_pm25 = df['pm25'].mean() if 'pm25' in df.columns else 0
        avg_pm10 = df['pm10'].mean() if 'pm10' in df.columns else 0
        avg_no2 = df['no2'].mean() if 'no2' in df.columns else 0
        avg_o3 = df['o3'].mean() if 'o3' in df.columns else 0
        
        # Calculate composite score (lower is better)
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
    """Create radar chart comparing selected cities with reference locations"""
    if not selected_cities or len(selected_cities) < 2:
        return go.Figure()
    
    categories = ['AQI', 'PM2.5', 'PM10', 'NO2', 'O3']
    
    # Fixed scales based on global references
    fixed_scales = {
        'aqi': 180,     # Jakarta ~150 * 1.2
        'pm25': 96,     # Jakarta ~80 * 1.2
        'pm10': 144,    # Jakarta ~120 * 1.2
        'no2': 72,      # Jakarta ~60 * 1.2
        'o3': 48        # Jakarta ~40 * 1.2
    }
    
    fig = go.Figure()
    
    # Add reference locations first
    reference_locations = {
        'Amazon Rainforest': {'aqi': 15, 'pm25': 8, 'pm10': 12, 'no2': 2, 'o3': 8},
        'Jakarta': {'aqi': 150, 'pm25': 80, 'pm10': 120, 'no2': 60, 'o3': 40}
    }
    
    for ref_name, ref_data in reference_locations.items():
        values = [ref_data['aqi'], ref_data['pm25'], ref_data['pm10'], ref_data['no2'], ref_data['o3']]
        
        normalized_values = []
        for j, (value, metric) in enumerate(zip(values, ['aqi', 'pm25', 'pm10', 'no2', 'o3'])):
            max_scale = fixed_scales[metric]
            normalized = min((value / max_scale) * 100, 100)
            normalized_values.append(normalized)
        
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
            opacity=0.2,
            line=dict(dash='dash'),
            hovertemplate='<b>%{fullData.name}</b> (Reference)<br>' +
                         '%{theta}: %{customdata}<br>' +
                         'Normalized: %{r:.1f}%<br>' +
                         '<extra></extra>',
            customdata=hover_text
        ))
    
    # Add selected cities
    for city in selected_cities:
        if city not in cities_data:
            continue
            
        data = cities_data[city]
        values = [data['aqi'], data['pm25'], data['pm10'], data['no2'], data['o3']]
        
        normalized_values = []
        for j, (value, metric) in enumerate(zip(values, ['aqi', 'pm25', 'pm10', 'no2', 'o3'])):
            max_scale = fixed_scales[metric]
            normalized = min((value / max_scale) * 100, 100)
            normalized_values.append(normalized)
        
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
                tickfont=dict(size=14, color='#2c3e50'),
                gridcolor='rgba(52, 73, 94, 0.2)',
                linecolor='rgba(52, 73, 94, 0.3)',
                showline=True,
                linewidth=1
            ),
            angularaxis=dict(
                tickfont=dict(size=14, color='#2c3e50'),
                linecolor='rgba(52, 73, 94, 0.3)',
                showline=True,
                linewidth=1
            ),
            bgcolor='rgba(248, 249, 250, 0.8)'
        ),
        showlegend=True,
        title=dict(
            text="Air Quality Comparison - Normalized Radar Chart",
            font=dict(size=20, color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        height=650,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02,
            font=dict(size=12),
            bgcolor='rgba(255,255,255,0.8)',
            bordercolor='rgba(52, 73, 94, 0.2)',
            borderwidth=1
        ),
        margin=dict(l=50, r=150, t=80, b=50)
    )
    
    return fig

def create_bar_chart(cities_data, selected_cities, metric='aqi'):
    """Create bar chart comparing cities for a specific metric"""
    if not selected_cities:
        return go.Figure()
    
    metric_names = {
        'aqi': 'Air Quality Index',
        'pm25': 'PM2.5 (μg/m³)',
        'pm10': 'PM10 (μg/m³)',
        'no2': 'NO2 (μg/m³)',
        'o3': 'O3 (μg/m³)'
    }
    
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
            textfont=dict(size=12, color='#2c3e50'),
            marker=dict(
                line=dict(color='rgba(52, 73, 94, 0.3)', width=1),
                opacity=0.8
            ),
            hovertemplate='<b>%{x}</b><br>' +
                         f'{metric_names.get(metric, metric.upper())}: %{{y:.1f}}<br>' +
                         '<extra></extra>'
        )
    ])
    
    fig.update_layout(
        title=dict(
            text=f"{metric_names.get(metric, metric.upper())} Comparison",
            font=dict(size=18, color='#2c3e50'),
            x=0.5,
            xanchor='center'
        ),
        xaxis=dict(
            title=dict(text="Cities", font=dict(size=14, color='#2c3e50')),
            tickfont=dict(size=12, color='#2c3e50'),
            gridcolor='rgba(52, 73, 94, 0.1)',
            linecolor='rgba(52, 73, 94, 0.3)',
            showline=True,
            linewidth=1
        ),
        yaxis=dict(
            title=dict(text=metric_names.get(metric, metric.upper()), font=dict(size=14, color='#2c3e50')),
            tickfont=dict(size=12, color='#2c3e50'),
            gridcolor='rgba(52, 73, 94, 0.1)',
            linecolor='rgba(52, 73, 94, 0.3)',
            showline=True,
            linewidth=1
        ),
        height=450,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(248, 249, 250, 0.8)",
        margin=dict(l=60, r=30, t=60, b=60),
        showlegend=False
    )
    
    return fig

def main():
    # Header
    st.title("🏙️ City Air Quality Comparison")
    
    # Sidebar controls
    st.sidebar.header("Controls")
    
    # Time period
    time_period = st.sidebar.selectbox(
        "Time Period",
        ["Last 7 days", "Last 30 days", "Last 90 days"],
        index=1
    )
    
    days_map = {"Last 7 days": 7, "Last 30 days": 30, "Last 90 days": 90}
    days = days_map[time_period]
    
    # Load data
    with st.spinner("Loading data..."):
        all_cities_data = load_city_data(days=days)
    
    if not all_cities_data:
        st.error("No data available. Please process some cities first.")
        return
    
    available_cities = list(all_cities_data.keys())
    
    # City selection
    selected_cities = st.sidebar.multiselect(
        "Select cities to compare",
        available_cities,
        default=available_cities[:3] if len(available_cities) >= 3 else available_cities
    )
    
    if len(selected_cities) < 2:
        st.info("Please select at least 2 cities to compare.")
        return
    
    # Calculate scores
    cities_scores = calculate_city_scores(all_cities_data)
    
    # Radar Chart - Full Width at the top
    radar_fig = create_radar_chart(cities_scores, selected_cities)
    st.plotly_chart(radar_fig, use_container_width=True)
    
    # City scores
    st.subheader("🏆 City Scores")
    score_cols = st.columns(len(selected_cities))
    for i, city in enumerate(selected_cities):
        if city in cities_scores:
            data = cities_scores[city]
            with score_cols[i]:
                st.metric(
                    label=city,
                    value=f"{data['score']:.1f}",
                    help=f"AQI: {data['aqi']:.1f}, PM2.5: {data['pm25']:.1f}, PM10: {data['pm10']:.1f}, NO2: {data['no2']:.1f}, O3: {data['o3']:.1f}"
                )
    
    # Quick info section
    st.subheader("📋 Air Quality Indicators")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🌡️ AQI**: Overall air quality (0-500)
        - 0-50: Good
        - 51-100: Moderate
        - 101-150: Unhealthy for sensitive groups
        
        **💨 PM2.5**: Fine particles (< 2.5μm)
        - WHO Guideline: < 15 μg/m³
        """)
    
    with col2:
        st.markdown("""
        **🌫️ PM10**: Coarse particles (< 10μm)
        - WHO Guideline: < 45 μg/m³
        
        **🚗 NO2**: Nitrogen dioxide
        - WHO Guideline: < 25 μg/m³
        """)
    
    with col3:
        st.markdown("""
        **☀️ O3**: Ground-level ozone
        - WHO Guideline: < 100 μg/m³
        
        **📈 References:**
        - 🌿 Amazon: Excellent
        - 🏙️ Jakarta: Poor
        """)
    
    # Bar Charts
    st.subheader("📊 Detailed Comparisons")
    
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
            bar_fig = create_bar_chart(cities_scores, selected_cities, metric)
            st.plotly_chart(bar_fig, use_container_width=True)

if __name__ == "__main__":
    main()
