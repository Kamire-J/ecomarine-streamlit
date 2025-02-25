import streamlit as st
from PIL import Image

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

# Mock Data for Products
products = [
    {"name": "Fresh Salmon", "price": "$15/kg", "image": "https://images.unsplash.com/photo-1585688964690-97f5853eb141?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
    {"name": "Fish", "price": "$25/kg", "image": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
    {"name": "Tuna", "price": "$18/kg", "image": "https://images.unsplash.com/photo-1519708227418-c8fd9a32b7a2?q=80&w=1170&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
    {"name": "Crabs", "price": "$22/kg", "image": "https://images.unsplash.com/photo-1510130387422-82bed34b37e9?q=80&w=1335&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
    {"name": "Prawns", "price": "$20/kg", "image": "https://images.unsplash.com/photo-1510130387422-82bed34b37e9?q=80&w=1335&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
    {"name": "Oysters", "price": "$30/kg", "image": "https://images.unsplash.com/photo-1510130387422-82bed34b37e9?q=80&w=1335&auto=format&fit=crop&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"},
]

# Product Grid Layout (3 columns)
st.subheader("🛍️ Featured Products")
cols = st.columns(3)

for index, product in enumerate(products):
    with cols[index % 3]:  # Distribute products across columns
        st.image(product["image"], use_container_width=True)
        st.write(f"**{product['name']}**")
        st.write(f"💰 {product['price']}")
        st.button("Add to Cart", key=product["name"])

# Footer
st.markdown("---")
st.caption("🌊 Sustainable. Fresh. Direct from Fishers.")
