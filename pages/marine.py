import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

# Page Title
st.title("Marine Data 🌊")
st.write("Track fish schools, ocean currents, and pollution patterns.")

# Generate mock data for fish schools with confidence levels
np.random.seed(42)
num_schools = 50
fish_schools = pd.DataFrame({
    "lat": np.random.uniform(30, 50, num_schools),  # Random latitudes
    "lon": np.random.uniform(-130, -110, num_schools),  # Random longitudes
    "confidence": np.random.uniform(50, 100, num_schools),  # Confidence scores 50-100%
})

# Confidence Level Slider
confidence_threshold = st.slider(
    "Select minimum confidence level for fish school predictions:",
    min_value=50,
    max_value=100,
    value=70,  # Default threshold
    step=5
)

# Filter fish schools based on selected confidence level
filtered_schools = fish_schools[fish_schools["confidence"] >= confidence_threshold]

# Display summary statistics
st.metric(label="Total Fish Schools Detected", value=len(filtered_schools))

# Visualization with PyDeck
st.subheader("Fish School Locations")

# Define color scale based on confidence
filtered_schools["color"] = filtered_schools["confidence"].apply(
    lambda x: [0, 255, 0, 160] if x > 85 else [255, 165, 0, 160] if x > 70 else [255, 0, 0, 160]
)

# PyDeck Map
layer = pdk.Layer(
    "ScatterplotLayer",
    data=filtered_schools,
    get_position=["lon", "lat"],
    get_radius=5000,  # Marker size
    get_color="color",
    pickable=True,
)

view_state = pdk.ViewState(latitude=40, longitude=-120, zoom=4, pitch=0)

map = pdk.Deck(layers=[layer], initial_view_state=view_state, tooltip={"text": "Confidence: {confidence}%"})
st.pydeck_chart(map)
