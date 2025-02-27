import streamlit as st
import sqlite3
import pandas as pd
import numpy as np

st.title("Analytics 📊")
st.write("View trends in oceanic data.")

# Initialize SQLite database
def init_db():
    conn = sqlite3.connect("marine_data.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS weather_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    week INTEGER,
                    temperature REAL)''')
    c.execute('''CREATE TABLE IF NOT EXISTS pollution_trends (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    month TEXT,
                    litter_collected REAL)''')
    conn.commit()
    conn.close()

# Generate mock data
def generate_mock_data():
    conn = sqlite3.connect("marine_data.db")
    c = conn.cursor()
    
    weather_data = [(i, np.random.uniform(22, 30)) for i in range(1, 5)]
    c.executemany("INSERT INTO weather_patterns (week, temperature) VALUES (?, ?)", weather_data)
    
    pollution_data = [(month, np.random.randint(400, 1000)) for month in ["Jan", "Feb", "Mar"]]
    c.executemany("INSERT INTO pollution_trends (month, litter_collected) VALUES (?, ?)", pollution_data)
    
    conn.commit()
    conn.close()

# Fetch data
def fetch_weather_data():
    conn = sqlite3.connect("marine_data.db")
    df = pd.read_sql("SELECT * FROM weather_patterns", conn)
    conn.close()
    return df

def fetch_pollution_data():
    conn = sqlite3.connect("marine_data.db")
    df = pd.read_sql("SELECT * FROM pollution_trends", conn)
    conn.close()
    return df

# Initialize DB and generate mock data
init_db()
generate_mock_data()

# Create tabs
tabs = st.tabs(["Weather Patterns", "Pollution Trends", "Fish Movement"])

with tabs[0]:
    st.subheader("Weather Patterns")
    st.write("View historical and current weather data affecting marine life.")
    weather_df = fetch_weather_data()
    st.line_chart(weather_df.set_index("week"))

with tabs[1]:
    st.subheader("Pollution Trends")
    st.write("Analyze trends in marine pollution levels.")
    pollution_df = fetch_pollution_data()
    st.bar_chart(pollution_df.set_index("month"))

with tabs[2]:
    st.subheader("Fish Movement Trends")
    st.write("Monitor fish school movement patterns.")
    st.line_chart({"Week": [1, 2, 3, 4], "Fish Schools": [10, 15, 13, 20]})

