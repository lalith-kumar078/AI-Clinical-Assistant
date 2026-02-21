import streamlit as st
from utils.auth import (
    login_user,
    logout_user,
    check_auth,
    get_role,
    register_user
)
from database.db import (
    init_db,
    init_login_table,
    init_user_table
)

# =====================================================
# PAGE CONFIG (MUST BE FIRST)
# =====================================================
st.set_page_config(
    page_title="AI Clinical Assistant",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 🔥 Hide default Streamlit multipage sidebar
st.markdown("""
    <style>
        [data-testid="stSidebarNav"] {display: none;}
    </style>
""", unsafe_allow_html=True)

# =====================================================
# INITIALIZE DATABASE
# =====================================================
init_db()
init_login_table()
init_user_table()

# =====================================================
# LANGUAGE SELECTOR (Always visible)
# =====================================================
language = st.sidebar.selectbox(
    "🌍 Select Language",
    ["English", "Hindi"],
    key="language_selector"
)

st.session_state["language"] = language


# =====================================================
# AUTHENTICATION SECTION
# =====================================================
if not check_auth():

    st.title("🏥 AI Healthcare System")

    auth_option = st.radio(
        "Select Option",
        ["Sign In", "Register"],
        horizontal=True
    )

    # ================= SIGN IN =================
    if auth_option == "Sign In":

        role = st.selectbox("Login As", ["doctor", "patient"])
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Sign In"):
            if login_user(username, password, role):
                st.success("Login Successful")
                st.rerun()
            else:
                st.error("Invalid Credentials")

    # ================= REGISTER =================
    else:

        reg_username = st.text_input("Username")
        reg_password = st.text_input("Password", type="password")
        reg_role = st.selectbox("Register As", ["doctor", "patient"])

        if st.button("Register"):
            try:
                register_user(reg_username, reg_password, reg_role)
                st.success("Registration Successful! Please Sign In.")
            except:
                st.error("Username already exists.")

    st.stop()


# =====================================================
# LOGGED IN VIEW
# =====================================================
role = get_role()
username = st.session_state.get("username")

st.sidebar.success(f"👤 {username} ({role.upper()})")

if st.sidebar.button("🔄 Switch Account"):
    logout_user()
    st.rerun()


# =====================================================
# ROLE-BASED NAVIGATION
# =====================================================
if role == "doctor":
    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Disease Prediction",
            "Heart Risk",
            "Medical Report Analyzer",
            "Telemedicine",
            "Admin Analytics"
        ]
    )

elif role == "patient":
    menu = st.sidebar.radio(
        "Navigation",
        [
            "Dashboard",
            "Disease Prediction",
            "Heart Risk",
            "Medical Report Analyzer",
            "Telemedicine"
        ]
    )


# =====================================================
# PAGE ROUTING (Using Streamlit Pages Folder)
# =====================================================

if menu == "Dashboard":

    if role == "doctor":
        st.title("🧑‍⚕️ Doctor Dashboard")
        st.markdown(f"""
Welcome Dr. *{username}*

- View Patient Consultations  
- Access Admin Analytics  
- Review Reports  
- Manage Telemedicine  
""")

    else:
        st.title("👤 Patient Dashboard")
        st.markdown(f"""
Welcome *{username}*

- Predict Diseases  
- Check Heart Risk  
- Upload Medical Reports  
- Book Telemedicine  
""")


elif menu == "Disease Prediction":
    st.switch_page("pages/2_Disease_Predictor.py")

elif menu == "Heart Risk":
    st.switch_page("pages/3_Heart_Risk.py")

elif menu == "Medical Report Analyzer":
    st.switch_page("pages/4_Report_Analyzer.py")

elif menu == "Telemedicine":
    st.switch_page("pages/5_Telemedicine.py")

elif menu == "Admin Analytics":
    st.switch_page("pages/9_Admin_Dashboard.py")