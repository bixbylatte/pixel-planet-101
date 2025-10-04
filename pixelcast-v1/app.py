import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import requests
import json
from typing import Dict, List, Tuple, Optional

# Page configuration
st.set_page_config(
    page_title="PixelCast",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# PixelCast CSS styling system
st.markdown("""
<style>
:root{
  --pc-bg:#f6f8fb;
  --pc-card:#ffffff;
  --pc-border:#e6eaf0;
  --pc-text:#0f172a;
  --pc-muted:#64748b;
  --pc-primary:#2563eb;
  --pc-success:#22c55e;
  --pc-warning:#f59e0b;
  --pc-danger:#ef4444;
  --pc-radius:14px;
  --pc-shadow:0 2px 10px rgba(15,23,42,.06);
}

/* App chrome */
html,body,.stApp{background:var(--pc-bg); color:var(--pc-text); font-family:Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji","Segoe UI Emoji";}
[data-testid="stHeader"]{background:transparent;}
.main .block-container{padding-top:1.2rem; padding-bottom:2rem;}

/* Generic card */
.pixel-card{
  background:var(--pc-card);
  border:1px solid var(--pc-border);
  border-radius:var(--pc-radius);
  box-shadow:var(--pc-shadow);
  padding:18px;
  position:relative;
}
.pixel-card h1,.pixel-card h2,.pixel-card h3{margin:0 0 .4rem 0; font-weight:700;}
.pixel-muted{color:var(--pc-muted); font-size:.92rem}

/* Pixelated edge accent (right side) */
.pixel-accent{overflow:hidden}
.pixel-accent::after{
  content:"";
  position:absolute; top:0; right:0; height:100%; width:56px; pointer-events:none;
  background:
    conic-gradient(from 0turn at 100% 0,#c7d2fe00 0 25%, #c7d2fe66 0 100%),
    repeating-linear-gradient(
      to bottom,
      #dbeafe 0 6px, #eff6ff 6px 12px
    );
  clip-path:polygon(0 0,100% 0,100% 100%,0 100%);
  image-rendering: pixelated;
  opacity:.55;
  border-top-right-radius:var(--pc-radius);
  border-bottom-right-radius:var(--pc-radius);
}

/* Metrics */
[data-testid="stMetric"]{
  background:var(--pc-card);
  border:1px solid var(--pc-border);
  border-radius:var(--pc-radius);
  box-shadow:var(--pc-shadow);
  padding:14px 16px;
}
[data-testid="stMetricLabel"]{color:var(--pc-muted) !important; font-weight:600;}
[data-testid="stMetricValue"]{font-size:1.6rem !important; font-weight:800;}

/* Buttons */
.stButton>button{
  background:var(--pc-success);
  color:#fff;
  border:1px solid #16a34a;
  border-radius:12px;
  padding:.6rem 1rem;
  font-weight:700;
  box-shadow:var(--pc-shadow);
}
.stButton>button:hover{filter:brightness(.95)}
/* Secondary button */
.button-secondary .stButton>button{
  background:var(--pc-primary);
  border-color:#1e40af;
}

/* Inputs */
input, textarea, select, .stTextInput>div>div>input{
  background:#fff !important;
  border:1px solid var(--pc-border) !important;
  border-radius:12px !important;
  padding:.55rem .7rem !important;
  box-shadow:none !important;
}
label, .stSelectbox label, .stDateInput label{color:var(--pc-muted); font-weight:600}

/* Tabs */
[data-testid="stTabs"] button{
  background:#f1f5f9;
  border:1px solid var(--pc-border);
  border-bottom:none;
  border-top-left-radius:12px; border-top-right-radius:12px;
  padding:.5rem .9rem; color:var(--pc-muted); font-weight:700;
}
[data-testid="stTabs"] button[aria-selected="true"]{
  background:#fff; color:var(--pc-text);
}

/* Expander */
[data-testid="stExpander"]{
  background:var(--pc-card);
  border:1px solid var(--pc-border);
  border-radius:var(--pc-radius);
  box-shadow:var(--pc-shadow);
}

/* Alerts */
.pixel-good{background:#f0fdf4; border:1px solid #bbf7d0; color:#166534; border-radius:12px; padding:.6rem .75rem}
.pixel-warn{background:#fffbeb; border:1px solid #fde68a; color:#92400e; border-radius:12px; padding:.6rem .75rem}
.pixel-bad{background:#fef2f2; border:1px solid #fecaca; color:#991b1b; border-radius:12px; padding:.6rem .75rem}

/* Sidebar */
[data-testid="stSidebar"]{
  background:#ffffff;
  border-right:1px solid var(--pc-border);
}
[data-testid="stSidebar"] .block-container{padding:1rem .8rem}

/* Weather metric styling */
.weather-metric {
    background:var(--pc-card);
    border:1px solid var(--pc-border);
    border-radius:var(--pc-radius);
    box-shadow:var(--pc-shadow);
    padding:18px;
    margin:0.5rem 0;
}

/* AI overview styling */
.ai-overview {
    background:var(--pc-card);
    border:1px solid var(--pc-border);
    border-radius:var(--pc-radius);
    box-shadow:var(--pc-shadow);
    padding:24px;
    margin-bottom:1rem;
}
</style>
""", unsafe_allow_html=True)

class WeatherDataGenerator:
    """Generate deterministic mock weather data"""
    
    @staticmethod
    def generate_weather_data(lat: float, lon: float, date: datetime, 
                            start_time: str, end_time: str) -> Dict:
        """Generate mock weather data based on location and time"""
        # Create deterministic seed based on coordinates and date
        seed = int(lat * 1000 + lon * 1000 + date.toordinal())
        np.random.seed(seed)
        
        # Base values with some variation
        base_temp = 20 + (lat / 10) + np.random.normal(0, 5)
        base_humidity = 60 + np.random.normal(0, 15)
        base_wind = 5 + np.random.exponential(3)
        base_uv = min(11, max(0, 3 + (lat / 20) + np.random.normal(0, 2)))
        
        return {
            'temperature': round(base_temp, 1),
            'precipitation': round(max(0, np.random.exponential(2)), 1),
            'humidity': round(max(0, min(100, base_humidity)), 1),
            'wind_speed': round(base_wind, 1),
            'uv_index': round(base_uv, 1),
            'cloud_cover': round(np.random.uniform(0, 100), 1)
        }

class GeocodingService:
    """Handle location geocoding using OpenStreetMap Nominatim API"""
    
    @staticmethod
    def geocode_location(location: str) -> Optional[Tuple[float, float, str]]:
        """Geocode a location string to coordinates"""
        try:
            # Using Nominatim API (free, no API key required)
            url = "https://nominatim.openstreetmap.org/search"
            params = {
                'q': location,
                'format': 'json',
                'limit': 1,
                'addressdetails': 1
            }
            headers = {
                'User-Agent': 'PixelCast Weather App'
            }
            
            response = requests.get(url, params=params, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                if data:
                    result = data[0]
                    lat = float(result['lat'])
                    lon = float(result['lon'])
                    display_name = result.get('display_name', location)
                    return lat, lon, display_name
        except Exception as e:
            st.error(f"Error geocoding location: {e}")
        return None

def create_weather_metric_display(metric_name: str, value: float, unit: str, emoji: str) -> str:
    """Create HTML for weather metric display using PixelCast styling"""
    return f"""
    <div class="pixel-card">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <span style="font-size: 1.8rem;">{emoji}</span>
            <div style="text-align: right;">
                <div style="font-weight: 800; font-size: 1.4rem; color: var(--pc-text);">{value} {unit}</div>
                <div class="pixel-muted" style="font-size: 0.9rem; font-weight: 600;">{metric_name}</div>
            </div>
        </div>
    </div>
    """

def initialize_session_state():
    """Initialize session state variables"""
    if 'selected_location' not in st.session_state:
        st.session_state.selected_location = None
    if 'selected_coords' not in st.session_state:
        st.session_state.selected_coords = None
    if 'weather_data' not in st.session_state:
        st.session_state.weather_data = {}
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = None
    if 'map_clicked' not in st.session_state:
        st.session_state.map_clicked = None

def main():
    initialize_session_state()
    
    # Title
    st.title("🌤️ PixelCast")
    st.markdown("**Your Intelligent Weather Forecast Companion**")
    
    # Create two-column layout
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Location & Preferences")
        
        # Location input with search icon
        col_location, col_search = st.columns([4, 1])
        
        with col_location:
            location_input = st.text_input(
                "Location", 
                value=st.session_state.selected_location or "",
                placeholder="Enter city, address, or coordinates...",
                label_visibility="collapsed"
            )
        
        with col_search:
            st.markdown("<br>", unsafe_allow_html=True)  # Align with text input
            if st.button("🔍", help="Search location"):
                if location_input:
                    with st.spinner("Searching location..."):
                        geocode_result = GeocodingService.geocode_location(location_input)
                        if geocode_result:
                            lat, lon, display_name = geocode_result
                            st.session_state.selected_location = display_name
                            st.session_state.selected_coords = (lat, lon)
                            st.success(f"Found: {display_name}")
                        else:
                            st.error("Location not found. Please try a different search term.")
                else:
                    st.error("Please enter a location to search.")
        
        # Date range selection with calendar
        st.markdown("### Date Range")
        date_range = st.date_input(
            "Select date range (max 7 days)",
            value=(datetime.now().date(), datetime.now().date() + timedelta(days=1)),
            min_value=datetime.now().date(),
            max_value=datetime.now().date() + timedelta(days=365),
            help="Select start and end dates for your forecast"
        )
        
        # Handle date range input and validation
        if isinstance(date_range, tuple) and len(date_range) == 2:
            start_date, end_date = date_range
        else:
            # If single date selected, treat it as start date
            start_date = date_range
            end_date = start_date + timedelta(days=1)
        
        # Validate date range
        date_range_days = (end_date - start_date).days
        if date_range_days > 7:
            st.error("❌ Error: Date range cannot exceed 7 days. Please select a shorter range.")
            # Reset to valid range
            end_date = start_date + timedelta(days=7)
        elif date_range_days < 0:
            st.error("❌ Error: End date cannot be before start date.")
            # Reset to valid range
            end_date = start_date + timedelta(days=1)
        
        # Time selection
        st.markdown("### Time Range")
        col_time1, col_time2 = st.columns(2)
        
        with col_time1:
            start_time = st.time_input("Start Time", value=datetime.strptime("09:00", "%H:%M").time())
        
        with col_time2:
            end_time = st.time_input("End Time", value=datetime.strptime("17:00", "%H:%M").time())
        
        # Validate time range
        if start_time >= end_time:
            st.error("❌ Error: Start time must be before end time. Please select a valid time range.")
            # Reset to valid time range
            end_time = datetime.strptime("17:00", "%H:%M").time()
        
        # Activity selection with reduced options
        st.markdown("### Activity (Optional)")
        activities = [
            "Select Activity",
            "Hiking", "Running", "Wedding", "Photography", "Others"
        ]
        
        selected_activity = st.selectbox(
            "Choose your activity",
            options=activities,
            index=0
        )
        
        # Manual activity input if Others is selected
        if selected_activity == "Others":
            manual_activity = st.text_input(
                "Specify your activity",
                placeholder="Enter your custom activity..."
            )
            if manual_activity:
                selected_activity = manual_activity
        
        # Confirm button
        if st.button("✅ Confirm & Update Forecast", type="primary"):
            # Validate all inputs before processing
            validation_errors = []
            
            # Check if location is selected
            if not st.session_state.selected_coords:
                validation_errors.append("Please search and select a location first.")
            
            # Check date range validity
            if (end_date - start_date).days > 7:
                validation_errors.append("Date range cannot exceed 7 days.")
            
            # Check time range validity
            if start_time >= end_time:
                validation_errors.append("Start time must be before end time.")
            
            # Display validation errors if any
            if validation_errors:
                for error in validation_errors:
                    st.error(f"❌ {error}")
            else:
                # Generate weather data for all dates in range
                current_date = start_date
                weather_data = {}
                
                while current_date <= end_date:
                    weather_data[current_date.strftime("%Y-%m-%d")] = WeatherDataGenerator.generate_weather_data(
                        st.session_state.selected_coords[0],
                        st.session_state.selected_coords[1],
                        datetime.combine(current_date, start_time),
                        start_time.strftime("%H:%M"),
                        end_time.strftime("%H:%M")
                    )
                    current_date += timedelta(days=1)
                
                st.session_state.weather_data = weather_data
                st.session_state.selected_date = start_date.strftime("%Y-%m-%d")
                st.success("Weather forecast updated!")
    
    with col2:
        st.markdown("### AI Overview")
        
        # AI Overview section - Mock data for now
        # Connect to AI agent.
        ai_recommendations = {
            "summary": "Based on your selected location and time, here are some recommendations:",
            "recommendations": [
                "Temperature looks comfortable for outdoor activities",
                "Light precipitation expected - consider bringing an umbrella",
                "Moderate winds - good for sailing but watch for cycling",
                "UV levels are moderate - sunscreen recommended"
            ]
        }
        
        if selected_activity != "Select Activity":
            ai_recommendations["recommendations"].append(f"Perfect conditions for {selected_activity.lower()}!")
        
        st.markdown(f"""
        <div class="pixel-card pixel-accent">
            <h3>🤖 AI Weather Summary</h3>
            <p class="pixel-muted">{ai_recommendations['summary']}</p>
            <ul style="margin: 12px 0; padding-left: 20px;">
                {''.join([f'<li style="margin: 8px 0;">{rec}</li>' for rec in ai_recommendations['recommendations']])}
            </ul>
        </div>
        """, unsafe_allow_html=True)
        
        # Date selector buttons
        if st.session_state.weather_data:
            st.markdown("### Select Date")
            
            date_cols = st.columns(len(st.session_state.weather_data))
            dates = sorted(st.session_state.weather_data.keys())
            
            for i, date_str in enumerate(dates):
                with date_cols[i]:
                    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                    day_name = date_obj.strftime("%a")
                    day_num = date_obj.day
                    
                    if st.button(f"{day_name}\n{day_num}", key=f"date_{date_str}"):
                        st.session_state.selected_date = date_str
                        st.rerun()
            
            # Map view with integrated weather metrics
            st.markdown("### Interactive Weather Map")
            
            if st.session_state.selected_coords:
                # Create map with larger size to accommodate weather metrics
                m = folium.Map(
                    location=st.session_state.selected_coords,
                    zoom_start=12,
                    tiles='OpenStreetMap'
                )
                
                # Add weather marker
                if st.session_state.selected_date and st.session_state.selected_date in st.session_state.weather_data:
                    weather = st.session_state.weather_data[st.session_state.selected_date]
                    
                    # Create popup with weather info
                    popup_html = f"""
                    <div style="width: 200px;">
                        <h4>Weather Forecast</h4>
                        <p><strong>Date:</strong> {datetime.strptime(st.session_state.selected_date, '%Y-%m-%d').strftime('%B %d, %Y')}</p>
                        <p>🌡️ {weather['temperature']}°C</p>
                        <p>☔ {weather['precipitation']}mm</p>
                        <p>💧 {weather['humidity']}%</p>
                        <p>🌬️ {weather['wind_speed']} km/h</p>
                        <p>☀️ UV {weather['uv_index']}</p>
                        <p>☁️ {weather['cloud_cover']}%</p>
                    </div>
                    """
                    
                    folium.Marker(
                        st.session_state.selected_coords,
                        popup=folium.Popup(popup_html, max_width=250),
                        icon=folium.Icon(color='blue', icon='cloud')
                    ).add_to(m)
                
                # Handle map clicks for location selection (double-click simulation)
                map_data = st_folium(m, width=700, height=500, returned_objects=["last_object_clicked"])
                
                # Check for map clicks and handle location selection
                if map_data["last_object_clicked"]:
                    clicked_lat = map_data["last_object_clicked"]["lat"]
                    clicked_lon = map_data["last_object_clicked"]["lng"]
                    
                    # Automatically select location on click (double-click simulation)
                    st.session_state.selected_coords = (clicked_lat, clicked_lon)
                    st.session_state.selected_location = f"Selected Location ({clicked_lat:.4f}, {clicked_lon:.4f})"
                    st.success("Location updated! Click Confirm to update weather forecast.")
                    st.rerun()
                
                # Weather metrics display - integrated within map view area
                if st.session_state.selected_date and st.session_state.selected_date in st.session_state.weather_data:
                    weather = st.session_state.weather_data[st.session_state.selected_date]
                    
                    st.markdown("#### Weather Metrics")
                    
                    # Create columns for weather metrics
                    metric_cols = st.columns(3)
                    
                    metrics = [
                        ("Temperature", weather['temperature'], "°C", "🌡️"),
                        ("Precipitation", weather['precipitation'], "mm", "☔"),
                        ("Humidity", weather['humidity'], "%", "💧"),
                        ("Wind Speed", weather['wind_speed'], "km/h", "🌬️"),
                        ("UV Index", weather['uv_index'], "", "☀️"),
                        ("Cloud Cover", weather['cloud_cover'], "%", "☁️")
                    ]
                    
                    for i, (name, value, unit, emoji) in enumerate(metrics):
                        with metric_cols[i % 3]:
                            st.markdown(create_weather_metric_display(name, value, unit, emoji), unsafe_allow_html=True)
        
        else:
            st.info("👈 Please search for a location and click Confirm to see the weather forecast.")

if __name__ == "__main__":
    main()
