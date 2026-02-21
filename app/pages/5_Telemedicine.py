import streamlit as st
import io
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter

from utils.auth import check_auth, get_role
from database.db import save_consultation, get_consultations_by_user


# =====================================================
# AUTH CHECK
# =====================================================
if not check_auth():
    st.warning("Please login to access this page.")
    st.stop()

role = get_role()
username = st.session_state.get("username")

st.title("🏥 Smart Telemedicine & Virtual Consultation System")

# =====================================================
# =============== CONSULTATION FORM ===================
# =====================================================

st.header("📅 Book a Consultation")

col1, col2 = st.columns(2)

with col1:
    name = st.text_input("Patient Name")
    age = st.number_input("Age", 1, 120, 25)

    doctor = st.selectbox(
        "Select Doctor",
        [
            "Dr. Sharma (Cardiologist)",
            "Dr. Mehta (General Physician)",
            "Dr. Rao (Neurologist)"
        ]
    )

with col2:
    date = st.date_input("Select Date")
    time = st.time_input("Select Time")

symptoms = st.text_area("Describe Symptoms")

# =====================================================
# CONFIRM BUTTON
# =====================================================

if st.button("Confirm Appointment"):

    if not name or not symptoms:
        st.error("Please fill all required fields.")
    else:

        save_consultation(
            username,
            name,
            age,
            doctor,
            str(date),
            str(time),
            symptoms
        )

        st.success("✅ Appointment Confirmed Successfully!")

        # ================= PDF =================
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph("Medical Consultation Report", styles['Title']))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph(f"Booked By: {username}", styles['Normal']))
        elements.append(Paragraph(f"Patient Name: {name}", styles['Normal']))
        elements.append(Paragraph(f"Age: {age}", styles['Normal']))
        elements.append(Paragraph(f"Doctor: {doctor}", styles['Normal']))
        elements.append(Paragraph(f"Date: {date}", styles['Normal']))
        elements.append(Paragraph(f"Time: {time}", styles['Normal']))
        elements.append(Spacer(1, 12))

        elements.append(Paragraph("Symptoms:", styles['Heading2']))
        elements.append(Paragraph(symptoms, styles['Normal']))

        doc.build(elements)
        buffer.seek(0)

        st.download_button(
            "📥 Download Consultation Report",
            data=buffer,
            file_name="consultation_report.pdf",
            mime="application/pdf"
        )


# =====================================================
# ================= HISTORY SECTION ===================
# =====================================================

st.divider()

if role == "doctor":
    st.subheader("👨‍⚕ All Consultations")

    history = get_consultations_by_user(username, "doctor")

else:
    st.subheader("📂 Your Consultation History")

    history = get_consultations_by_user(username, "patient")


if history:
    for record in history:
        with st.expander(f"{record[5]} - {record[2]}"):
            st.write(f"Booked By: {record[1]}")
            st.write(f"Patient Name: {record[2]}")
            st.write(f"Age: {record[3]}")
            st.write(f"Doctor: {record[4]}")
            st.write(f"Time: {record[6]}")
            st.write(f"Symptoms: {record[7]}")
else:
    st.info("No consultation records available.")