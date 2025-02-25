import streamlit as st

st.title("Analytics 📊")
st.write("View trends in oceanic data.")

st.subheader("Fish Movement Trends")
st.line_chart({"Week": [1, 2, 3, 4], "Fish Schools": [10, 15, 13, 20]})

st.subheader("Marine Litter Trends")
st.bar_chart({"Month": ["Jan", "Feb", "Mar"], "Litter Collected (kg)": [500, 700, 900]})
