import gc
import streamlit as st
from helper_functions import add_logo

st.set_page_config(
    page_title="Introduction",
    page_icon="👋",
    layout="wide",
    initial_sidebar_state="expanded",
)

add_logo()

with open("style.css") as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

st.title("Streamlit for Healthcare Network Graphs")

gc.collect()

st.markdown(
"""
This is a collection of examples demonstrating the display of network graphs in Streamlit.
"""
)