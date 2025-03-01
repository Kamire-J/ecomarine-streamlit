import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import sqlite3
import time
from math import radians, sin, cos, sqrt, atan2

# Page Title
st.title("East African Fish Migration Tracker 🐟")
st.write("Monitor natural migration patterns of fish species along the East African coastline.")

# Initialize SQLite database
def init_db():
    """Initialize database with proper error handling and transactions."""
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

def generate_east_african_data(schools_count: int = 50, migrations_count: int = 50) -> None:
    """
    Generate synthetic marine data for East African coastline with realistic migration patterns.
    
    Args:
        schools_count: Number of fish school records to generate
        migrations_count: Number of migration records to generate
    """
    try:
        with sqlite3.connect("marine_data.db") as conn:
            c = conn.cursor()
            c.execute("BEGIN TRANSACTION")

            # Clear existing data
            c.execute("DELETE FROM fish_schools")
            c.execute("DELETE FROM migrations")

            # Generate fish school data along East African coastline
            np.random.seed(42)
            # East African coastline approximate coordinates (Kenya, Tanzania, Mozambique)
            lats = np.random.uniform(-15, 5, schools_count)  # From Mozambique to Somalia
            lons = np.random.uniform(39, 45, schools_count)  # Indian Ocean coastline
            confidences = np.random.uniform(50, 100, schools_count)
            
            c.executemany(
                "INSERT INTO fish_schools (lat, lon, confidence) VALUES (?, ?, ?)",
                zip(lats, lons, confidences)
            )

            # Generate migration data with East African species and seasonal patterns
            east_african_species = [
                "Yellowfin Tuna", "Kingfish", "Black Marlin", "Sailfish", 
                "Dorado", "Barracuda", "Skipjack Tuna", "Wahoo"
            ]
            
            # Current month to determine seasonal patterns
            current_month = pd.Timestamp.now().month
            
            # Define seasonal migration patterns based on month
            # 1-3: Northeast monsoon, 4-5: Transition, 6-9: Southeast monsoon, 10-12: Transition
            is_northeast_monsoon = 1 <= current_month <= 3
            is_southeast_monsoon = 6 <= current_month <= 9
            
            species = np.random.choice(east_african_species, migrations_count)
            
            # Base coordinates along the coastline
            base_lats = np.random.uniform(-15, 5, migrations_count)
            base_lons = np.random.uniform(39, 45, migrations_count)
            
            # Realistic speeds for different fish species
            speeds = []
            for s in species:
                if s in ["Yellowfin Tuna", "Skipjack Tuna"]:
                    speeds.append(np.random.uniform(4, 7))  # Faster swimmers
                elif s in ["Black Marlin", "Sailfish"]:
                    speeds.append(np.random.uniform(6, 10))  # Very fast swimmers
                elif s == "Wahoo":
                    speeds.append(np.random.uniform(5, 8))  # Fast swimmers
                else:
                    speeds.append(np.random.uniform(2, 5))  # Average swimmers
            
            # Directional bias based on species and season
            directions = []
            for i, s in enumerate(species):
                if is_northeast_monsoon:
                    # During NE monsoon, many species move southward along the coast
                    if s in ["Yellowfin Tuna", "Skipjack Tuna", "Dorado"]:
                        directions.append(np.random.uniform(150, 210))  # Southward
                    elif s in ["Kingfish", "Barracuda"]:
                        directions.append(np.random.uniform(120, 240))  # South/Southeast
                    else:
                        directions.append(np.random.uniform(90, 270))  # Variable but mostly southward
                elif is_southeast_monsoon:
                    # During SE monsoon, many species move northward
                    if s in ["Black Marlin", "Sailfish", "Wahoo"]:
                        directions.append(np.random.uniform(330, 30))  # Northward
                    elif s in ["Yellowfin Tuna", "Kingfish"]:
                        directions.append(np.random.uniform(300, 60))  # North/Northeast
                    else:
                        directions.append(np.random.uniform(270, 90))  # Variable but mostly northward
                else:
                    # Transition periods have more mixed patterns
                    directions.append(np.random.uniform(0, 360))
                    
                # Add some randomness to make patterns more natural
                directions[-1] = (directions[-1] + np.random.uniform(-20, 20)) % 360
            
            # Vectorized coordinate calculations for target positions
            # Larger delta for more visible migration paths
            delta = np.array(speeds) / 20  # Adjust for more visible paths
            target_lats = base_lats + delta * np.sin(np.radians(directions))
            target_lons = base_lons + delta * np.cos(np.radians(directions))
            
            # Timestamps with seasonal patterns
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

# Initialize database
init_db()

# Check if we need to generate East African data
if st.sidebar.button("Generate East African Migration Data"):
    generate_east_african_data()
    st.sidebar.success("Generated new East African fish migration data!")
    st.rerun()

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

# Load data
fish_schools = fetch_fish_schools()
migrations = fetch_migrations()

# East African Map View
east_african_view = pdk.ViewState(
    latitude=-5,  # Centered on Tanzania/Kenya
    longitude=42,  # Indian Ocean coastline
    zoom=5,
    pitch=0
)

# Sidebar for filtering options
st.sidebar.title("Filter Options")

# Species selection for migration patterns
species_list = migrations["species"].unique().tolist()
selected_species = st.sidebar.multiselect(
    "Select Fish Species", 
    species_list,
    default=species_list[:2] if len(species_list) >= 2 else species_list
)

# Time window for migrations
time_window = st.sidebar.slider("Time Window (minutes)", 10, 120, 60)
latest_time = pd.Timestamp.now() - pd.Timedelta(minutes=time_window)

# Filter migrations based on species and time
if selected_species:
    filtered_migrations = migrations[
        (migrations["species"].isin(selected_species)) & 
        (migrations["timestamp"] >= latest_time)
    ]
else:
    filtered_migrations = migrations[migrations["timestamp"] >= latest_time]

# Main content area
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("East African Fish Migration Patterns")
    
    # Create species-specific migration layers with different colors
    migration_layers = []
    
    # Color map for different species
    species_colors = {
        "Yellowfin Tuna": [255, 0, 0],
        "Kingfish": [0, 0, 255],
        "Black Marlin": [128, 0, 128],
        "Sailfish": [0, 128, 128],
        "Dorado": [255, 165, 0],
        "Barracuda": [0, 128, 0],
        "Skipjack Tuna": [255, 0, 128],
        "Wahoo": [0, 255, 128]
    }
    
    for species in selected_species:
        species_data = filtered_migrations[filtered_migrations["species"] == species]
        
        if not species_data.empty:
            # Points layer for the species
            point_layer = pdk.Layer(
                "ScatterplotLayer",
                species_data,
                get_position=["longitude", "latitude"],
                get_fill_color=species_colors.get(species, [200, 200, 200]),
                get_radius=3000,
                pickable=True,
                auto_highlight=True,
                get_tooltip = {"html": f"<b>Species:</b> {species}<br><b>Speed:</b> {{speed}} km/h"}
            )
            
            # Path layer showing migration direction
            path_layer = pdk.Layer(
                "LineLayer",
                species_data,
                get_source_position=["longitude", "latitude"],
                get_target_position=["target_longitude", "target_latitude"],
                get_color=species_colors.get(species, [200, 200, 200]),
                get_width=2,
                highlight_color=[255, 255, 0],
                picking_radius=10,
                auto_highlight=True,
                pickable=True,
            )
            
            # Add arrow layer to show direction more clearly
            arrow_layer = pdk.Layer(
                "TextLayer",
                species_data,
                get_position=["target_longitude", "target_latitude"],
                get_text="▶",  # Arrow character
                get_size=16,
                get_color=species_colors.get(species, [200, 200, 200]),
                get_angle="direction",
                pickable=True,
            )
            
            migration_layers.extend([point_layer, path_layer, arrow_layer])
    
    # Create the deck with all layers and tooltips
    deck = pdk.Deck(
        layers=migration_layers,
        initial_view_state=east_african_view,
        tooltip={
            "html": """
            <div style="background-color: rgba(0, 0, 0, 0.7); color: white; padding: 10px; border-radius: 5px;">
                <h3 style="margin-top: 0;">{species}</h3>
                <p><b>Location:</b> {latitude:.4f}, {longitude:.4f}</p>
                <p><b>Speed:</b> {speed:.1f} km/h</p>
                <p><b>Direction:</b> {direction:.1f}°</p>
                <p><i>Click for migration details</i></p>
            </div>
            """,
            "style": {"color": "white"}
        },
        map_provider="mapbox",
        map_style=pdk.map_styles.SATELLITE,
    )
    
    # Display the map
    st.pydeck_chart(deck)
    
    # Legend for species colors
    st.subheader("Species Legend")
    legend_cols = st.columns(4)
    for i, (species, color) in enumerate(species_colors.items()):
        if species in selected_species:
            col_idx = i % 4
            with legend_cols[col_idx]:
                st.markdown(
                    f"<div style='display: flex; align-items: center;'>"
                    f"<div style='background-color: rgb({color[0]}, {color[1]}, {color[2]}); "
                    f"width: 15px; height: 15px; margin-right: 5px; border-radius: 50%;'></div>"
                    f"<span>{species}</span>"
                    f"</div>",
                    unsafe_allow_html=True
                )

with col2:
    st.subheader("Migration Details")
    
    # Option to select migration point
    if not filtered_migrations.empty:
        migration_options = [
            f"{row['species']} #{row['id']} (Speed: {row['speed']:.1f} km/h)" 
            for _, row in filtered_migrations.iterrows()
        ]
        
        selected_migration_idx = st.selectbox(
            "Select Migration Point", 
            options=range(len(migration_options)),
            format_func=lambda x: migration_options[x] if x < len(migration_options) else "",
            key="migration_select"
        )
        
        if selected_migration_idx is not None:
            selected_migration = filtered_migrations.iloc[selected_migration_idx]
            
            st.write(f"**Selected Migration Information:**")
            st.write(f"- Species: {selected_migration['species']}")
            st.write(f"- Current Location: {selected_migration['latitude']:.4f}, {selected_migration['longitude']:.4f}")
            st.write(f"- Swimming Speed: {selected_migration['speed']:.1f} km/h")
            st.write(f"- Direction: {selected_migration['direction']:.1f}°")
            
            # Convert direction to cardinal direction
            def direction_to_cardinal(direction):
                cardinals = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", 
                             "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
                idx = round(direction / 22.5) % 16
                return cardinals[idx]
            
            cardinal = direction_to_cardinal(selected_migration['direction'])
            st.write(f"- Cardinal Direction: {cardinal}")
            
            # Calculate projected position after 24 hours
            speed_km_per_day = selected_migration['speed'] * 24
            
            # Simple projection (not accounting for Earth's curvature for short distances)
            direction_rad = np.radians(selected_migration['direction'])
            lat_change = speed_km_per_day * np.sin(direction_rad) / 111  # Approx 111 km per degree of latitude
            lon_change = speed_km_per_day * np.cos(direction_rad) / (111 * np.cos(np.radians(selected_migration['latitude'])))
            
            projected_lat = selected_migration['latitude'] + lat_change
            projected_lon = selected_migration['longitude'] + lon_change
            
            st.write("**Projected Movement:**")
            st.write(f"- After 24 hours: {projected_lat:.4f}, {projected_lon:.4f}")
            st.write(f"- Distance traveled: ~{speed_km_per_day:.1f} km")
            
            # Show small map of projected movement
            projection_df = pd.DataFrame({
                'points': ['Current', 'Projected'],
                'lat': [selected_migration['latitude'], projected_lat],
                'lon': [selected_migration['longitude'], projected_lon],
                'color': [[species_colors.get(selected_migration['species'], [200, 200, 200])], 
                          [species_colors.get(selected_migration['species'], [200, 200, 200])]]
            })
            
            projection_layer = pdk.Layer(
                "ScatterplotLayer",
                projection_df,
                get_position=["lon", "lat"],
                get_radius=3000,
                get_fill_color="color",
                pickable=True,
            )
            
            path_df = pd.DataFrame({
                'path': [[
                    [selected_migration['longitude'], selected_migration['latitude']],
                    [projected_lon, projected_lat]
                ]],
                'color': [species_colors.get(selected_migration['species'], [200, 200, 200])]
            })
            
            projection_path = pdk.Layer(
                "PathLayer",
                path_df,
                get_path="path",
                get_color="color",
                width_scale=20,
                width_min_pixels=2,
                get_width=5,
            )
            
            projection_view = pdk.ViewState(
                latitude=(selected_migration['latitude'] + projected_lat) / 2,
                longitude=(selected_migration['longitude'] + projected_lon) / 2,
                zoom=7,
                pitch=0
            )
            
            st.pydeck_chart(pdk.Deck(
                layers=[projection_layer, projection_path],
                initial_view_state=projection_view,
                map_provider="mapbox",
                map_style=pdk.map_styles.SATELLITE,
            ))
            
            # Seasonal context
            current_month = pd.Timestamp.now().month
            season = ""
            if 1 <= current_month <= 3:
                season = "Northeast Monsoon (December-March)"
            elif 4 <= current_month <= 5:
                season = "Transition Period (April-May)"
            elif 6 <= current_month <= 9:
                season = "Southeast Monsoon (June-September)"
            else:
                season = "Transition Period (October-November)"
            
            st.write("**Seasonal Context:**")
            st.write(f"- Current Season: {season}")
            
            # Species-specific information
            st.write("**Species Information:**")
            species_info = {
                "Yellowfin Tuna": "Highly migratory pelagic species. During NE monsoon, they often move southward along the East African coast.",
                "Kingfish": "Found in coastal waters. Seasonal movements follow baitfish migrations.",
                "Black Marlin": "Deep-water species that follows warm currents. More abundant during SE monsoon.",
                "Sailfish": "Fast swimmers that migrate along the coast seasonally. Peak season is November-March.",
                "Dorado": "Also known as Mahi-mahi. Follows warm water and congregates around floating debris.",
                "Barracuda": "Coastal predator that makes limited seasonal movements.",
                "Skipjack Tuna": "Schooling species that follows warm water and food sources.",
                "Wahoo": "Fast pelagic predator that follows seasonal temperature changes."
            }
            
            st.write(species_info.get(selected_migration['species'], "No specific information available."))
    else:
        st.write("No migration points match the current filters.")

    # Statistics section
    st.subheader("Migration Statistics")
    
    if not filtered_migrations.empty:
        # Migration statistics by species
        st.write("**Migration Counts by Species:**")
        species_counts = filtered_migrations["species"].value_counts()
        for species, count in species_counts.items():
            st.write(f"- {species}: {count}")
        
        # Average speeds
        st.write("**Average Speeds:**")
        for species in selected_species:
            species_data = filtered_migrations[filtered_migrations["species"] == species]
            if not species_data.empty:
                avg_speed = species_data["speed"].mean()
                st.write(f"- {species}: {avg_speed:.1f} km/h")
        
        # Dominant directions
        st.write("**Dominant Migration Directions:**")
        for species in selected_species:
            species_data = filtered_migrations[filtered_migrations["species"] == species]
            if not species_data.empty:
                # Calculate the most common direction range
                direction_bins = pd.cut(species_data["direction"], 
                                       bins=[0, 45, 90, 135, 180, 225, 270, 315, 360],
                                       labels=["N-NE", "NE-E", "E-SE", "SE-S", "S-SW", "SW-W", "W-NW", "NW-N"])
                dominant_direction = direction_bins.mode()[0]
                st.write(f"- {species}: {dominant_direction}")

# Auto-refresh option
if "auto_refresh" not in st.session_state:
    st.session_state.auto_refresh = False

st.sidebar.title("Refresh Options")
st.session_state.auto_refresh = st.sidebar.checkbox("Enable auto-refresh (30 seconds)")

if st.session_state.auto_refresh:
    st.sidebar.write("Next update in", 30 - (time.time() % 30), "seconds")
    time.sleep(1)
    st.rerun()