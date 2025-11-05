import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import hashlib

@st.cache_resource
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict)
    scoped_creds = creds.with_scopes([
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(scoped_creds)

@st.cache_data
def load_user_database():
    # coba baca dari local dulu
    try:
        return pd.read_csv("data/database.csv")
    except FileNotFoundError:
        # fallback: ambil dari Streamlit secrets
        data = st.secrets.get("users", {})
        if not data:
            st.error("No user data found. Please upload 'data/database.csv' or configure Streamlit secrets.")
            return pd.DataFrame(columns=["StudentID", "FullName", "Password"])
        df = pd.DataFrame([
            {"StudentID": k, "FullName": v, "Password": k[-6:]} for k, v in data.items()
        ])
        return df

def login():
    db = load_user_database()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None

    if not st.session_state.logged_in:
        st.title("🔐 Student Login")

        nim = st.text_input("Student ID (NIM)")
        password = st.text_input("Password (6 digits from your NIM)", type="password")

        if st.button("Login"):
            hashed_pw = hashlib.sha256(password.encode()).hexdigest()
            user = db[
                (db["Student ID"].astype(str) == nim) &
                (db["Password"] == hashed_pw)
            ]
            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = user.iloc[0]["Student ID"]
                st.session_state.user_name = user.iloc[0]["Name"]
                st.session_state.user_faculty = user.iloc[0]["Faculty"]
                st.success(f"Welcome, {st.session_state.user_name}!")
                st.rerun()
            else:
                st.error("❌ Invalid NIM or password.")

    else:
        st.sidebar.success(f"Logged in as: {st.session_state.user_name}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.rerun()
        return True  # Sudah login
    return st.session_state.logged_in
