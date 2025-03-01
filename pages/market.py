import streamlit as st
from PIL import Image
import sqlite3
import pandas as pd

# Page Title
st.title("Market Place 🛒")
st.write("Connect directly with fishers and buy fresh seafood.")

# Hero Section
st.image("https://images.unsplash.com/photo-1735968665229-39785549cf7a?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D", use_container_width=True)
st.markdown(
    """
    **Welcome to the Marine Market!**  
    Purchase fresh, sustainably caught seafood directly from fishers.  
    Get the best quality while supporting local communities.
    """
)

# Initialize database tables for marketplace
def init_marketplace_db():
    try:
        with sqlite3.connect("marine_data.db") as conn:
            c = conn.cursor()
            
            # Create fishers table
            c.execute("""CREATE TABLE IF NOT EXISTS fishers (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        location TEXT NOT NULL,
                        contact TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )""")
            
            # Create products table
            c.execute("""CREATE TABLE IF NOT EXISTS products (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        name TEXT NOT NULL,
                        price TEXT NOT NULL,
                        fisher_id INTEGER NOT NULL,
                        stock_level TEXT NOT NULL CHECK(stock_level IN ('High', 'Medium', 'Low')),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (fisher_id) REFERENCES fishers(id)
                    )""")
            
            # Check if we need to insert sample data
            c.execute("SELECT COUNT(*) FROM fishers")
            fisher_count = c.fetchone()[0]
            
            if fisher_count == 0:
                # Insert sample fishers
                fishers = [
                    ("Ocean Harvest Co-op", "North Pacific", "contact@oceanharvest.com"),
                    ("Coastal Fishers Ltd.", "South Bay", "info@coastalfishers.com"),
                    ("Blue Waters Fishing", "East Atlantic", "sales@bluewaters.com"),
                    ("Bay Crabbers Association", "Rocky Shore", "info@baycrabbers.org"),
                    ("Tropical Seafood Co.", "Gulf Waters", "orders@tropicalseafood.com"),
                    ("Reef Harvesters", "Coastal Reefs", "contact@reefharvesters.com")
                ]
                
                c.executemany("INSERT INTO fishers (name, location, contact) VALUES (?, ?, ?)", fishers)
                
                # Get fisher IDs for product references
                c.execute("SELECT id, name FROM fishers")
                fisher_map = {name: id for id, name in c.fetchall()}
                
                # Insert sample products
                products = [
                    ("Fresh Salmon", "$15/kg", fisher_map["Ocean Harvest Co-op"], "High"),
                    ("Fish", "$25/kg", fisher_map["Coastal Fishers Ltd."], "Medium"),
                    ("Tuna", "$18/kg", fisher_map["Blue Waters Fishing"], "Low"),
                    ("Crabs", "$22/kg", fisher_map["Bay Crabbers Association"], "High"),
                    ("Prawns", "$20/kg", fisher_map["Tropical Seafood Co."], "Medium"),
                    ("Oysters", "$30/kg", fisher_map["Reef Harvesters"], "Low")
                ]
                
                c.executemany("INSERT INTO products (name, price, fisher_id, stock_level) VALUES (?, ?, ?, ?)", products)
                
                conn.commit()
    except sqlite3.Error as e:
        st.error(f"Marketplace database initialization failed: {str(e)}")
        return False
    return True

# Connect to SQLite database
@st.cache_resource
def get_connection():
    return sqlite3.connect('marine_data.db', check_same_thread=False)

# Load products from database
@st.cache_data
def load_products():
    conn = get_connection()
    try:
        query = """
        SELECT 
            p.id, 
            p.name, 
            p.price, 
            f.name as fisher_name, 
            f.location, 
            p.stock_level
        FROM 
            products p
        JOIN 
            fishers f ON p.fisher_id = f.id
        """
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Database error: {e}")
        return pd.DataFrame()

# Initialize marketplace database tables and sample data
db_initialized = init_marketplace_db()

if not db_initialized:
    st.error("Failed to initialize marketplace database. Please check the logs.")
else:
    # Image mapping
    product_images = {
        "Fresh Salmon": "https://images.unsplash.com/photo-1585688964690-97f5853eb141?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Fish": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Tuna": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Crabs": "https://images.unsplash.com/photo-1510130387422-82bed34b37e9?q=80&w=1335&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Prawns": "https://images.unsplash.com/photo-1510130387422-82bed34b37e9?q=80&w=1335&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
        "Oysters": "https://images.unsplash.com/photo-1510130387422-82bed34b37e9?q=80&w=1335&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D",
    }

    # Default image for products not in the mapping
    default_image = "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"

    # Load products
    products_df = load_products()

    if products_df.empty:
        st.warning("No products found in the database.")
    else:
        # Filter options
        st.subheader("🔍 Filter Products")
        col1, col2, col3 = st.columns(3)
        with col1:
            fisher_filter = st.selectbox("Fisher", ["All"] + list(products_df["fisher_name"].unique()))
        with col2:
            location_filter = st.selectbox("Location", ["All"] + list(products_df["location"].unique()))
        with col3:
            stock_filter = st.selectbox("Stock Level", ["All", "High", "Medium", "Low"])

        # Apply filters
        filtered_df = products_df.copy()
        if fisher_filter != "All":
            filtered_df = filtered_df[filtered_df["fisher_name"] == fisher_filter]
        if location_filter != "All":
            filtered_df = filtered_df[filtered_df["location"] == location_filter]
        if stock_filter != "All":
            filtered_df = filtered_df[filtered_df["stock_level"] == stock_filter]

        # Product Grid Layout (3 columns)
        st.subheader("🛍️ Featured Products")
        if filtered_df.empty:
            st.info("No products match your filter criteria. Please try different filters.")
        else:
            cols = st.columns(3)
            for index, row in filtered_df.iterrows():
                with cols[index % 3]:  # Distribute products across columns
                    # Get image from mapping or use default
                    image_url = product_images.get(row["name"], default_image)
                    st.image(image_url, use_container_width=True)
                    st.write(f"**{row['name']}**")
                    st.write(f"💰 {row['price']}")
                    
                    # Display fisher and stock information
                    stock_color = {"High": "green", "Medium": "orange", "Low": "red"}[row["stock_level"]]
                    st.markdown(f"🚢 **Source**: {row['fisher_name']}")
                    st.markdown(f"📍 **Location**: {row['location']}")
                    st.markdown(f"📦 **Stock**: <span style='color:{stock_color}'>{row['stock_level']}</span>", unsafe_allow_html=True)
                    
                    st.button("Add to Cart", key=f"product_{row['id']}")

# Footer
st.markdown("---")
st.caption("🌊 Sustainable. Fresh. Direct from Fishers.")