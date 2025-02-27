import pydeck as pdk
import pandas as pd

import pydeck as pdk

# Fish migration path data
fish_paths_data = [
    {
        "start": [40, -5],
        "end": [42, -6],
        "color": [255, 0, 0]  # Red for Tuna
    },
    {
        "start": [38, -8],
        "end": [39, -9],
        "color": [0, 255, 0]  # Green for Kingfish
    },
    {
        "start": [39, -10],
        "end": [41, -11],
        "color": [0, 0, 255]  # Blue for Sharks
    },
    {
        "start": [41, -4],
        "end": [42, -5],
        "color": [255, 255, 0] # Yellow for Sardines
    },
    {
        "start": [42, -7],
        "end": [44, -6],
        "color": [255, 0, 255] # Magenta for Billfish
    }
]

# Fish locations (scatterplot data)
fish_locations_data = [
    {"coordinates": [40, -5], "species": "Tuna"},
    {"coordinates": [38, -8], "species": "Kingfish"},
    {"coordinates": [39, -10], "species": "Shark"},
    {"coordinates": [41, -4], "species": "Sardines"},
    {"coordinates": [42, -7], "species": "Billfish"},
]

# View state
INITIAL_VIEW_STATE = pdk.ViewState(
    latitude=-6,
    longitude=40,
    zoom=5,
    pitch=0,
    bearing=0,
)

# Scatterplot layer for fish locations
scatterplot_layer = pdk.Layer(
    "ScatterplotLayer",
    fish_locations_data,
    radius_scale=20,
    get_position="coordinates",
    get_fill_color=[0, 128, 255],  # Blue for fish locations
    get_radius=100,
    pickable=True,
    auto_highlight=True,
    get_tooltip = {"html": "<b>Species:</b> {species}"}

)

# Line layer for migration paths
line_layer = pdk.Layer(
    "LineLayer",
    fish_paths_data,
    get_source_position="start",
    get_target_position="end",
    get_color="color",
    get_width=3,
    highlight_color=[255, 255, 0],
    picking_radius=10,
    auto_highlight=True,
    pickable=True,
)

# Combine layers and render
layers = [scatterplot_layer, line_layer]
r = pdk.Deck(layers=layers, initial_view_state=INITIAL_VIEW_STATE)
r.to_html("fish_migration_full.html")

#print("Fish migration map generated (fish_migration_full.html)")