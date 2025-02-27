import streamlit as st

# Set page title
st.set_page_config(page_title="EcoMarine", layout="wide")

# Sidebar Navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Marine Map", "Marketplace", "Analytics"])

# Home Page
if page == "Home":
    st.title("Welcome to EcoMarine 🌊")
    st.subheader("Mapping the Ocean for a Sustainable Future")

    # Hero Section
    st.image("./images/fish.jpg", use_container_width=True)

    # Quick Statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Fish Schools Tracked", value="1,250")
    with col2:
        st.metric(label="Marine Litter Detected", value="3,480 kg")
    with col3:
        st.metric(label="Active Fishers", value="5,200")

    # Info Cards
    st.subheader("Key Insights")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.image("./images/yellow.jpg")
        st.write("📍 **Real-time Fish Tracking**")
        st.write("Monitor fish movements to improve fishing efficiency.")

    with col2:
        st.image("./images/litter.jpg")
        st.write("🌱 **Marine Litter Analysis**")
        st.write("Identify pollution hotspots and support clean-up efforts.")

    with col3:
        st.image("./images/litter.jpg")
        st.write("🛒 **Fisher-Buyer Market**")
        st.write("Connect fishers directly with buyers for fair trade.")

# Load other pages
elif page == "Marine Map":
    exec(open("pages/marine.py").read())
elif page == "Marketplace":
    exec(open("pages/market.py").read())
elif page == "Analytics":
    exec(open("pages/analytics.py").read())
