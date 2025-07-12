import streamlit as st
import random
from math import radians, sin, cos, sqrt, atan2

# Set the page to a wide layout for better display
st.set_page_config(
    page_title="EV Station Recommender",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Fixed station data
stations = [
    {"name": "Connaught Place", "lat": 28.6315, "lon": 77.2167},
    {"name": "Saket", "lat": 28.5222, "lon": 77.2066},
    {"name": "Dwarka", "lat": 28.5921, "lon": 77.0460},
    {"name": "Karol Bagh", "lat": 28.6512, "lon": 77.1905},
    {"name": "Lajpat Nagar", "lat": 28.5672, "lon": 77.2436},
    {"name": "Rajouri Garden", "lat": 28.6426, "lon": 77.1197},
    {"name": "Vasant Kunj", "lat": 28.5206, "lon": 77.1571},
    {"name": "Preet Vihar", "lat": 28.6469, "lon": 77.3024},
    {"name": "Rohini", "lat": 28.7499, "lon": 77.0560},
    {"name": "Nehru Place", "lat": 28.5483, "lon": 77.2513},
]

# Simulate station data
def simulate_station_data():
    data = []
    for s in stations:
        car_ports = random.randint(2, 6)
        scooter_ports = random.randint(3, 8)
        car_waiting = random.randint(0, car_ports)
        scooter_waiting = random.randint(0, scooter_ports)
        car_session = random.randint(30, 90)  # minutes
        scooter_session = random.randint(20, 60)
        traffic_speed = random.randint(15, 30)
        data.append({
            "name": s["name"],
            "lat": s["lat"],
            "lon": s["lon"],
            "car_ports": car_ports,
            "scooter_ports": scooter_ports,
            "car_waiting": car_waiting,
            "scooter_waiting": scooter_waiting,
            "car_session": car_session,
            "scooter_session": scooter_session,
            "traffic_speed": traffic_speed,
        })
    return data

# --- HEADER ---
# Colors adjusted for dark mode
st.markdown(
    """
    <h1 style='text-align: center; color: #60a5fa; font-size: 2.2em; font-weight: 700; margin-bottom: 0.2em;'>⚡ EV Station Recommender</h1>
    <p style='text-align: center; color: #9ca3af; font-size: 1.08em; margin-bottom: 1.2em;'>Find the best charging station for your EV in Delhi, instantly!</p>
    """,
    unsafe_allow_html=True
)

# --- SIDEBAR ---
with st.sidebar:
    # Colors adjusted for dark mode
    st.markdown("<h2 style='color:#60a5fa;'>Your Location & Vehicle</h2>", unsafe_allow_html=True)
    user_lat = st.number_input("Current Latitude", value=28.6, format="%.4f")
    user_lon = st.number_input("Current Longitude", value=77.2, format="%.4f")
    vehicle_type = st.radio("Vehicle Type", ["car", "scooter"], horizontal=True)
    st.markdown("<hr style='border-color: #4b5563;'>", unsafe_allow_html=True)
    # Tip box colors adjusted for dark mode
    st.markdown(
        "<span style='color:#f59e0b; font-weight:600; font-size:1.0em; background-color:#373020; padding:6px 10px; border-radius:6px; display:inline-block;'>Tip: Use your GPS coordinates for best results!</span>",
        unsafe_allow_html=True
    )

    # Spacer to push button to bottom
    st.markdown("<div style='height:180px;'></div>", unsafe_allow_html=True)
    # Admin Panel button (styled)
    st.markdown(
        """
        <a href="http://localhost:8502" target="_blank" style="text-decoration:none;">
            <button style="width:100%; background:#3b82f6; color:#fff; font-weight:700; font-size:1.08em; border:none; border-radius:8px; padding:10px 0; margin-top:10px; cursor:pointer;">ADMIN PANEL</button>
        </a>
        """,
        unsafe_allow_html=True
    )

# --- HELPER FUNCTIONS ---
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def compute_eta(station, user_lat, user_lon, vehicle_type):
    if vehicle_type == "car":
        ports, waiting, avg_session = station["car_ports"], station["car_waiting"], station["car_session"]
    else:
        ports, waiting, avg_session = station["scooter_ports"], station["scooter_waiting"], station["scooter_session"]
    
    distance = haversine(user_lat, user_lon, station["lat"], station["lon"])
    queue_time = (waiting / ports) * avg_session if ports > 0 else 0
    travel_time = (distance / station["traffic_speed"]) * 60 if station["traffic_speed"] > 0 else 0
    total_eta = queue_time + travel_time
    
    return {
        **station,
        "distance_km": round(distance, 2),
        "queue_time": round(queue_time, 1),
        "travel_time": round(travel_time, 1),
        "total_eta": round(total_eta, 1),
        "recommended": False,
    }

# --- DATA PROCESSING ---
station_data = simulate_station_data()
annotated = [compute_eta(s, user_lat, user_lon, vehicle_type) for s in station_data]
annotated.sort(key=lambda x: x["total_eta"])
if annotated:
    annotated[0]["recommended"] = True

# --- SUBHEADER ---
# Color adjusted for dark mode
st.markdown("""
<div style='margin-top: 20px; margin-bottom: 10px;'>
    <h2 style='color:#60a5fa; text-align:center;'>Recommended Stations</h2>
</div>
""", unsafe_allow_html=True)

# --- DISPLAY LOGIC ---
# Card style colors adjusted for dark mode
card_style = """
    background-color: #1e293b;
    border-radius: 14px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.25);
    padding: 18px 16px 16px 16px;
    margin-bottom: 14px;
    border: 1px solid #3b82f6;
    max-width: 600px;
"""

for i in range(0, len(annotated), 2):
    cols = st.columns(2)
    for j in range(2):
        if i + j < len(annotated):
            s = annotated[i + j]
            # Recommended badge colors adjusted for dark mode
            recommended_badge = "<span style='background:#3b82f6; color:#ffffff; border-radius:6px; padding:2px 10px; font-weight:700; font-size:0.9em; margin-left:8px;'>✅ Recommended</span>" if s["recommended"] else ""
            with cols[j]:
                # All text and accent colors adjusted for dark mode
                st.markdown(f"""
                    <div style='{card_style}'>
                        <h3 style='color:#93c5fd; margin-bottom:0.2em; font-size:1.25em;'>{s['name']} {recommended_badge}</h3>
                        <div style='margin-top:4px; margin-bottom:6px;'>
                            <span style='font-size:1em; color:#93c5fd; font-weight:600;'>
                                {'🚗 Car' if vehicle_type=='car' else '🛵 Scooter'}
                            </span>
                        </div>
                        <ul style='list-style:none; padding-left:0; color:#e5e7eb; font-size:0.98em;'>
                            <li><b style='color:#60a5fa;'>Ports:</b> {s['car_ports'] if vehicle_type=='car' else s['scooter_ports']} &nbsp; | &nbsp; <b style='color:#60a5fa;'>Queue:</b> {s['car_waiting'] if vehicle_type=='car' else s['scooter_waiting']}</li>
                            <li><b style='color:#60a5fa;'>Avg Session:</b> {s['car_session'] if vehicle_type=='car' else s['scooter_session']} min</li>
                            <li><b style='color:#60a5fa;'>Distance:</b> {s['distance_km']} km</li>
                            <li><b style='color:#60a5fa;'>Travel Time:</b> {s['travel_time']} min</li>
                            <li><b style='color:#60a5fa;'>Queue Time:</b> {s['queue_time']} min</li>
                            <li style='color:#93c5fd; font-weight:700; margin-top:5px;'><b>Total ETA:</b> {s['total_eta']} min</li>
                        </ul>
                    </div>
                """, unsafe_allow_html=True)