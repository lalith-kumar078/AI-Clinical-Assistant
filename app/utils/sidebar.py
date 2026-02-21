import streamlit as st

def render_sidebar():

    language = st.sidebar.selectbox(
        "🌍 Select Language",
        ["English", "Hindi"]
    )

    st.session_state["language"] = language

    return language
