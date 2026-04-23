import streamlit as st
import os
import sys
import pandas as pd

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Page configuration
st.set_page_config(
    page_title="🌍 Air Quality Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for multi-page app
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
    
    .page-selector {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .page-button {
        background: rgba(255,255,255,0.2);
        border: none;
        color: white;
        padding: 0.5rem 1rem;
        margin: 0.25rem;
        border-radius: 5px;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .page-button:hover {
        background: rgba(255,255,255,0.3);
        transform: translateY(-2px);
    }
    
    .page-button.active {
        background: rgba(255,255,255,0.4);
        font-weight: bold;
    }
    
    .footer {
        text-align: center;
        color: #666;
        padding: 2rem;
        margin-top: 3rem;
        border-top: 1px solid #eee;
    }
</style>
""", unsafe_allow_html=True)

def main():
    # Header
    st.markdown('<h1 class="main-header">🌍 Air Quality Dashboard</h1>', unsafe_allow_html=True)
    
    # Page selector
    st.markdown("""
    <div class="page-selector">
        <h3 style="color: white; text-align: center; margin-bottom: 1rem;">📊 Select Dashboard Page</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Page selection
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🏙️ City Analysis", use_container_width=True):
            st.session_state.page = "city_analysis"
            st.rerun()
    
    with col2:
        if st.button("🏆 City Comparison", use_container_width=True):
            st.session_state.page = "city_comparison"
            st.rerun()
    
    with col3:
        if st.button("📈 Data Processing", use_container_width=True):
            st.session_state.page = "data_processing"
            st.rerun()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = "city_analysis"
    
    # Page content
    if st.session_state.page == "city_analysis":
        st.markdown("## 🏙️ Single City Analysis")
        st.info("This page shows detailed analysis for a single city with time series, patterns, and metrics.")
        
        # Import and run the main dashboard
        try:
            from streamlit_app import main as city_analysis_main
            city_analysis_main()
        except ImportError as e:
            st.error(f"Could not load city analysis page: {e}")
            st.info("Make sure streamlit_app.py is in the same directory.")
    
    elif st.session_state.page == "city_comparison":
        st.markdown("## 🏆 City Comparison")
        st.info("This page allows you to compare multiple cities with radar charts, rankings, and detailed metrics.")
        
        # Import and run the city comparison page
        try:
            from city_comparison import main as comparison_main
            comparison_main()
        except ImportError as e:
            st.error(f"Could not load city comparison page: {e}")
            st.info("Make sure city_comparison.py is in the same directory.")
    
    elif st.session_state.page == "data_processing":
        st.markdown("## 📈 Data Processing")
        st.info("This page shows database statistics and processing options.")
        
        # Data processing page content
        try:
            from database_manager import AirQualityDatabase
            
            st.markdown("### 🗄️ Database Statistics")
            
            # Show database stats
            db = AirQualityDatabase("air_quality.db")
            stats = db.get_database_stats()
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Records", stats['total_records'])
            
            with col2:
                st.metric("Cities Available", len(stats['city_counts']))
            
            with col3:
                if stats['date_range'][0] and stats['date_range'][1]:
                    date_range = f"{stats['date_range'][0]} to {stats['date_range'][1]}"
                else:
                    date_range = "No data"
                st.metric("Date Range", date_range)
            
            # Cities breakdown
            st.markdown("### 🏙️ Cities in Database")
            if stats['city_counts']:
                cities_df = pd.DataFrame([
                    {"City": city, "Records": count} 
                    for city, count in stats['city_counts'].items()
                ])
                cities_df = cities_df.sort_values('Records', ascending=False)
                st.dataframe(cities_df, use_container_width=True)
            else:
                st.warning("No cities found in database. Please process some S3 data first.")
            
            # Processing instructions
            st.markdown("### 🔧 Data Processing")
            st.markdown("""
            To add more cities to the database, use the following commands:
            
            ```bash
            # Process a single city
            python3 process_s3_to_db.py --city Barcelona --limit 1000
            
            # Process all cities (after installing dependencies)
            ./process_all_cities_commands.sh
            ```
            
            **Available Cities:**
            Barcelona, Madrid, Valencia, Granada, Sevilla, Bilbao, Malaga, Valladolid, Zaragoza, Huelva, Soria, Gijon, Palma
            """)
            
        except ImportError as e:
            st.error(f"Could not load database manager: {e}")
            st.info("Make sure database_manager.py is in the same directory.")
    
    # Footer
    st.markdown("""
    <div class="footer">
        <p>🌍 Air Quality Dashboard | Multi-page application for comprehensive air quality analysis</p>
        <p>Built with ❤️ using Streamlit and Plotly</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
