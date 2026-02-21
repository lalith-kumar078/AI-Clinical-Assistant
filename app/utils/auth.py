import streamlit as st
import bcrypt
from database.db import get_user, create_user, save_login_history


def hash_password(password):
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def register_user(username, password, role):
    hashed = hash_password(password)
    create_user(username, hashed, role)


def login_user(username, password, selected_role):
    user = get_user(username)

    if user:
        _, db_username, db_password, db_role = user

        if db_role == selected_role and verify_password(password, db_password):
            st.session_state["authenticated"] = True
            st.session_state["username"] = db_username
            st.session_state["role"] = db_role
            save_login_history(db_username, db_role)
            return True

    return False


def logout_user():
    st.session_state.clear()


def check_auth():
    return st.session_state.get("authenticated", False)


def get_role():
    return st.session_state.get("role")