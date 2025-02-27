import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import sqlite3

# Page Title
st.title("Marine Data 🌊")
st.write("Track fish schools, ocean currents, and pollution patterns.")

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("marine_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS fish_schools (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    lat REAL,
                    lon REAL,
                    confidence REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    species TEXT,
                    latitude REAL,
                    longitude REAL,
                    speed REAL,
                    direction REAL,
                    target_latitude REAL,
                    target_longitude REAL,
                    timestamp TEXT)''')
    conn.commit()
    conn.close()

def generate_mock_data():
    conn = sqlite3.connect("marine_data.db")
    c = conn.cursor()

    # Generate fish school data
    np.random.seed(42)
    num_schools = 50
    fish_schools = [(np.random.uniform(-5, -2), np.random.uniform(39, 42), np.random.uniform(50, 100)) for _ in range(num_schools)]
    c.executemany("INSERT INTO fish_schools (lat, lon, confidence) VALUES (?, ?, ?)", fish_schools)

    # Generate marine species migration data
    species = ["Tuna", "Shark", "Whale", "Salmon"]
    migrations = []
    for _ in range(50):
        species_name = np.random.choice(species)
        lat, lon = np.random.uniform(-5, -2), np.random.uniform(39, 42)
        speed = np.random.uniform(1, 10)
        direction = np.random.uniform(0, 360)
        timestamp = pd.Timestamp.now() - pd.Timedelta(minutes=np.random.randint(0, 120))
        target_lat = lat + (speed / 100) * np.sin(np.radians(direction))
        target_lon = lon + (speed / 100) * np.cos(np.radians(direction))
        migrations.append((species_name, lat, lon, speed, direction, target_lat, target_lon, timestamp.isoformat()))
    c.executemany("INSERT INTO migrations (species, latitude, longitude, speed, direction, target_latitude, target_longitude, timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", migrations)

    conn.commit()
    conn.close()

# Initialize database and generate data if empty
init_db()

def fetch_fish_schools():
    conn = sqlite3.connect("marine_data.db")
    df = pd.read_sql("SELECT * FROM fish_schools", conn)
    conn.close()
    return df

def fetch_migrations():
    conn = sqlite3.connect("marine_data.db")
    df = pd.read_sql("SELECT * FROM migrations", conn, parse_dates=["timestamp"])
    conn.close()
    return df

fish_schools = fetch_fish_schools()

# Confidence Level Slider
confidence_threshold = st.slider(
    "Select minimum confidence level for fish school predictions:",
    min_value=50,
    max_value=100,
    value=70,
    step=5
)

# Filter fish schools based on selected confidence level
filtered_schools = fish_schools[fish_schools["confidence"] >= confidence_threshold]

st.metric(label="Total Fish Schools Detected", value=len(filtered_schools))

# Visualization with PyDeck
st.subheader("Fish School Locations")
filtered_schools["color"] = filtered_schools["confidence"].apply(
    lambda x: [0, 255, 0, 160] if x > 85 else [255, 165, 0, 160] if x > 70 else [255, 0, 0, 160]
)

layer = pdk.Layer(
    "ScatterplotLayer",
    filtered_schools,
    get_position=["lon", "lat"],
    get_radius=5000,
    get_color="color",
    pickable=True,
)

view_state = pdk.ViewState(latitude=-3.5, longitude=40.5, zoom=6, pitch=0)
st.pydeck_chart(pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Confidence: {confidence}%"}))

# Marine Migration Tracker
st.subheader("Marine Species Migration Tracker")

migrations = fetch_migrations()
species_list = migrations["species"].unique().tolist()
selected_species = st.selectbox("Select Fish Species", species_list, index=0)
time_window = st.slider("Time Window (minutes)", 10, 120, 60)

latest_time = pd.Timestamp.now() - pd.Timedelta(minutes=time_window)
filtered_data = migrations[(migrations["species"] == selected_species) & (migrations["timestamp"] >= latest_time)]

# Statistics
st.metric("Total Active Migrations", len(filtered_data))
st.metric("Average Speed (km/h)", round(filtered_data["speed"].mean(), 2) if not filtered_data.empty else 0)
st.metric("Dominant Direction (°)", round(filtered_data["direction"].mode()[0], 2) if not filtered_data.empty else "N/A")

layer_migration = pdk.Layer(
    "ScatterplotLayer",
    filtered_data,
    get_position=["longitude", "latitude"],
    get_fill_color=[255, 0, 0],
    get_radius=400,
    pickable=True,
    auto_highlight=True,
    get_tooltip = {"html": "<b>Species:</b> {species}"}
)

direction_layer = pdk.Layer(
    "LineLayer",
    filtered_data,
    get_source_position=["longitude", "latitude"],
    get_target_position=["target_longitude", "target_latitude"],
    get_color=[0, 255, 0],
    get_width=3,
    highlight_color=[255, 255, 0],
    picking_radius=10,
    auto_highlight=True,
    pickable=True,
)

st.pydeck_chart(pdk.Deck(layers=[layer_migration, direction_layer], initial_view_state=view_state))

if st.button("Update Migration Data"):
    generate_mock_data()
    st.rerun()
