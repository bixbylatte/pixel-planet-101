import math
import requests
import streamlit as st
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium
import folium

st.set_page_config(page_title="Precip Map (NASA POWER)", layout="wide")

st.title("Average Precipitation • 20 km radius")
st.caption("Source: NASA POWER climatology (monthly averages, mm/month).")

# --- Inputs ---
place = st.text_input("Search a location", value="Davao City, Philippines")
month_names = ["JAN","FEB","MAR","APR","MAY","JUN","JUL","AUG","SEP","OCT","NOV","DEC"]
month = st.selectbox("Month (climatology)", month_names, index=0)
radius_km = 20  # static as requested

# --- Geocode ---
@st.cache_data(show_spinner=False)
def geocode_once(q):
    geolocator = Nominatim(user_agent="precip_app")
    loc = geolocator.geocode(q)
    if not loc:
        return None
    return float(loc.latitude), float(loc.longitude), loc.address

coords = geocode_once(place)
if not coords:
    st.error("Location not found.")
    st.stop()

lat, lon, resolved = coords
st.write(f"**Resolved:** {resolved}")
st.write(f"**Center:** {lat:.5f}, {lon:.5f} • **Radius:** {radius_km} km")

# --- NASA POWER fetch ---
# Monthly climatology for precipitation (PRECTOTCORR: total precip)
# Docs: https://power.larc.nasa.gov/docs/services/api/ (temporal=climatology, point)
@st.cache_data(show_spinner=False)
def fetch_power_precip(lat_, lon_):
    url = (
        "https://power.larc.nasa.gov/api/temporal/climatology/point"
        f"?parameters=PRECTOTCORR&community=RE&longitude={lon_}&latitude={lat_}&format=JSON"
    )
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    j = r.json()
    data = j["properties"]["parameter"]["PRECTOTCORR"]  # mm/month per month key
    return data  # dict with keys JAN..DEC

try:
    precip_dict = fetch_power_precip(lat, lon)
except Exception as e:
    st.error(f"POWER request failed: {e}")
    st.stop()

mm_per_month = precip_dict.get(month)
if mm_per_month is None:
    st.error("No precipitation data returned.")
    st.stop()

# Convert to an approximate mm/day for readability too
# Use month length approximation for the chosen month
month_len = dict(JAN=31,FEB=28,MAR=31,APR=30,MAY=31,JUN=30,JUL=31,AUG=31,SEP=30,OCT=31,NOV=30,DEC=31)[month]
mm_per_day = mm_per_month / month_len

st.metric(
    label=f"Average precipitation • {month}",
    value=f"{mm_per_month:.1f} mm/month",
    delta=f"~{mm_per_day:.1f} mm/day"
)

# --- Map ---
m = folium.Map(location=[lat, lon], zoom_start=10, tiles="CartoDB positron")

# 20 km circle
folium.Circle(
    location=[lat, lon],
    radius=radius_km * 1000,
    color="#1f77b4",
    fill=True,
    fill_opacity=0.1,
    popup=f"{radius_km} km radius"
).add_to(m)

# Center marker with precip info
folium.Marker(
    location=[lat, lon],
    tooltip="Center",
    popup=f"{resolved}\n{month}: {mm_per_month:.1f} mm/month (~{mm_per_day:.1f} mm/day)"
).add_to(m)

st_folium(m, height=520, use_container_width=True)

st.divider()
st.subheader("Notes")
st.write(
    "- POWER climatology gives long-term monthly averages (not daily forecasts).\n"
    "- Values are for the center point. This is a starter. Area-averaging over the 20 km circle requires gridded data sampling."
)
