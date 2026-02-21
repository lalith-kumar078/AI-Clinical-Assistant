import matplotlib
matplotlib.use("Agg")

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

from database.db import (
    get_statistics,
    get_consultations,
    get_login_history
)
from utils.auth import check_auth, get_role


# =====================================================
# AUTH PROTECTION
# =====================================================
if not check_auth():
    st.warning("Please login to access this page.")
    st.stop()

if get_role() != "doctor":
    st.warning("Doctor access only.")
    st.stop()


# =====================================================
# PAGE HEADER
# =====================================================
st.title("📊 Doctor Analytics Dashboard")
st.markdown("Monitor system activity and patient engagement.")
st.divider()


# =====================================================
# STATISTICS SECTION
# =====================================================
total, avg_age, doctor_data = get_statistics()

col1, col2, col3 = st.columns(3)

col1.metric("Total Consultations", total or 0)
col2.metric("Average Patient Age", f"{avg_age:.1f}" if avg_age else "N/A")
col3.metric("Most Consulted Doctor", doctor_data[0] if doctor_data else "N/A")

st.divider()


# =====================================================
# DOCTOR DISTRIBUTION CHART
# =====================================================
st.subheader("📈 Doctor Consultation Distribution")

consultations = get_consultations()

if consultations:

    df = pd.DataFrame(
        consultations,
        columns=[
            "id",
            "patient_username",
            "name",
            "age",
            "doctor",
            "date",
            "time",
            "symptoms"
        ]
    )

    doctor_counts = df["doctor"].value_counts()

    fig, ax = plt.subplots(figsize=(6, 4))
    doctor_counts.plot(kind="bar", ax=ax)

    ax.set_xlabel("Doctor")
    ax.set_ylabel("Number of Consultations")
    ax.set_title("Consultations per Doctor")
    plt.xticks(rotation=30)

    st.pyplot(fig)

else:
    st.info("No consultation data available.")

st.divider()


# =====================================================
# LOGIN HISTORY
# =====================================================
st.subheader("🔐 System Login History")

login_data = get_login_history()

if login_data:

    login_df = pd.DataFrame(
        login_data,
        columns=["ID", "Username", "Role", "Login Time"]
    )

    st.dataframe(login_df, use_container_width=True, height=300)

else:
    st.info("No login history available.")