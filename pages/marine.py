import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import sqlite3
import time

# Page Title
st.title("Marine Data 🌊")
st.write("Track fish schools, ocean currents, and pollution patterns.")

# Initialize SQLite database
def init_db():
    """Initialize database with proper error handling and transactions.
    
    Creates tables for fish school data and marine migrations if they don't exist.
    Uses proper transaction management and error handling.
    """
    try:
        with sqlite3.connect("marine_data.db") as conn:
            c = conn.cursor()
            
            # Create fish schools table with spatial metadata
            c.execute("""CREATE TABLE IF NOT EXISTS fish_schools (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        lat REAL NOT NULL CHECK(lat BETWEEN -90 AND 90),
                        lon REAL NOT NULL CHECK(lon BETWEEN -180 AND 180),
                        confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 100),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )""")
            
            # Create migrations table with referential integrity
            c.execute("""CREATE TABLE IF NOT EXISTS migrations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        species TEXT NOT NULL,
                        latitude REAL NOT NULL CHECK(latitude BETWEEN -90 AND 90),
                        longitude REAL NOT NULL CHECK(longitude BETWEEN -180 AND 180),
                        speed REAL NOT NULL CHECK(speed >= 0),
                        direction REAL NOT NULL CHECK(direction BETWEEN 0 AND 360),
                        target_latitude REAL NOT NULL CHECK(target_latitude BETWEEN -90 AND 90),
                        target_longitude REAL NOT NULL CHECK(target_longitude BETWEEN -180 AND 180),
                        timestamp TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )""")
            
            # Create index for faster species lookups
            c.execute("CREATE INDEX IF NOT EXISTS idx_migrations_species ON migrations(species)")
            
            conn.commit()
    except sqlite3.Error as e:
        st.error(f"Database initialization failed: {str(e)}")
        raise

def generate_mock_data(schools_count: int = 50, migrations_count: int = 50) -> None:
    """
    Generate synthetic marine data using vectorized operations and proper transaction handling.
    
    Args:
        schools_count: Number of fish school records to generate
        migrations_count: Number of migration records to generate
        
    Features:
    - Type hints and docstring
    - Context manager for database connection
    - Vectorized NumPy operations
    - Proper transaction handling
    - Parameterized counts
    """
    try:
        with sqlite3.connect("marine_data.db") as conn:
            c = conn.cursor()
            c.execute("BEGIN TRANSACTION")

            # Generate fish school data using vectorized operations
            np.random.seed(42)
            lats = np.random.uniform(-5, -2, schools_count)
            lons = np.random.uniform(39, 42, schools_count)
            confidences = np.random.uniform(50, 100, schools_count)
            c.executemany(
                "INSERT INTO fish_schools (lat, lon, confidence) VALUES (?, ?, ?)",
                zip(lats, lons, confidences)
            )

            # Generate migration data with vectorized calculations
            species = np.random.choice(["Tuna", "Shark", "Whale", "Salmon"], migrations_count)
            base_lats = np.random.uniform(-5, -2, migrations_count)
            base_lons = np.random.uniform(39, 42, migrations_count)
            speeds = np.random.uniform(1, 10, migrations_count)
            directions = np.random.uniform(0, 360, migrations_count)
            
            # Vectorized coordinate calculations
            delta = speeds / 100  # 1% of speed as degree offset
            target_lats = base_lats + delta * np.sin(np.radians(directions))
            target_lons = base_lons + delta * np.cos(np.radians(directions))
            
            # Single timestamp reference for consistency
            base_time = pd.Timestamp.now()
            timestamps = [base_time - pd.Timedelta(minutes=np.random.randint(0, 120)) 
                         for _ in range(migrations_count)]

            c.executemany(
                """INSERT INTO migrations 
                (species, latitude, longitude, speed, direction,
                 target_latitude, target_longitude, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                zip(species, base_lats, base_lons, speeds, directions,
                    target_lats, target_lons, [t.isoformat() for t in timestamps])
            )

            conn.commit()
            
    except sqlite3.Error as e:
        conn.rollback()
        st.error(f"Mock data generation failed: {str(e)}")
        raise
    except Exception as e:
        conn.rollback()
        st.error(f"Unexpected error: {str(e)}")
        raise

# Initialize database and generate data if empty
init_db()

@st.cache_data(ttl=300)
def fetch_fish_schools():
    conn = sqlite3.connect("marine_data.db")
    df = pd.read_sql("SELECT * FROM fish_schools", conn)
    conn.close()
    return df

@st.cache_data(ttl=300)
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
    picking_radius=300,
    auto_highlight=True,
    pickable=True,
)

st.pydeck_chart(pdk.Deck(layers=[layer_migration, direction_layer], initial_view_state=view_state))

if st.button("Update Migration Data"):
    generate_mock_data()
    st.rerun()



# Add at the top after imports
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

# Add toggle in appropriate section
st.session_state.auto_refresh = st.checkbox("Enable auto-refresh (30 seconds)")

if st.session_state.auto_refresh:
    st.write("Next update in", 30 - (time.time() % 30), "seconds")
    time.sleep(1)
    st.rerun()
