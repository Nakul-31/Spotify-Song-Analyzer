import streamlit as st
import pandas as pd

# Load the dataset
df = pd.read_csv('dataset.csv')

# Display the dataset in a fully scrollable table
st.title("Dataset Display")

st.subheader("Entire Dataset")
st.dataframe(df, use_container_width=True)

# Expander for full screen view
with st.expander("View Dataset in Full Screen", expanded=False):
    st.dataframe(df, use_container_width=True)
