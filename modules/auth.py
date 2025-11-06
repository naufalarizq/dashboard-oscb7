import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import hashlib

# === KONFIGURASI ===
SHEET_KEY_DB = "1LoptadYNUgEJ9fHJShdwwCz2O-F-cxLAJ6YgucO2UrA"
WORKSHEET_NAME_DB = "DatabaseScholars"

# ✅ hash password
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

# ✅ koneksi aman ke Google Sheet (optional)
@st.cache_resource
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict)
    scoped_creds = creds.with_scopes([
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    return gspread.authorize(scoped_creds)

#load user database
@st.cache_data
def load_user_database():
    gc = get_gspread_client()
    sh = gc.open_by_key(SHEET_KEY_DB    )
    ws = sh.worksheet(WORKSHEET_NAME_DB)
    data = ws.get_all_records()
    return pd.DataFrame(data), ws

# === LOGIN ===
def login():
    df, _ = load_user_database()

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_name = None
        st.session_state.user_faculty = None
        st.session_state.user_batch = None

    if not st.session_state.logged_in:
        st.subheader("🔐 Student Login")

        nim = st.text_input("Student ID (NIM)")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            hashed_pw = hash_password(password)
            user = df[
                (df["Student ID"].astype(str) == nim) &
                ((df["Password"] == password) | (df["PasswordHash"] == hashed_pw))
            ]

            if not user.empty:
                user_data = user.iloc[0]
                st.session_state.logged_in = True
                st.session_state.user_id = user_data["Student ID"]
                st.session_state.user_name = user_data["Name"]
                st.session_state.user_faculty = user_data["Faculty"]
                st.session_state.user_batch = user_data["Batch"]
                st.success(f"Welcome, {user_data['Name']}!")
                st.rerun()
            else:
                st.error("❌ Invalid NIM or password.")
    else:
        st.sidebar.success(f"Logged in as: {st.session_state.user_name}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.session_state.user_faculty = None
            st.session_state.user_batch = None
            st.rerun()

        return True

    return st.session_state.logged_in


# === GANTI PASSWORD ===
def change_password():
    if not st.session_state.get("logged_in"):
        st.warning("Please log in first.")
        return

    st.subheader("🔑 Change Your Password")

    current_pw = st.text_input("Current Password", type="password")
    new_pw = st.text_input("New Password", type="password")
    confirm_pw = st.text_input("Confirm New Password", type="password")

    if st.button("Update Password"):
        if new_pw != confirm_pw:
            st.error("❌ New passwords do not match.")
            return

        df, ws = load_user_database()
        user_id = st.session_state.user_id
        user_idx = df.index[df["Student ID"].astype(str) == str(user_id)].tolist()

        if not user_idx:
            st.error("User not found in database.")
            return

        i = user_idx[0]
        stored_pw = str(df.iloc[i]["Password"])
        stored_hash = str(df.iloc[i]["PasswordHash"])

        # verifikasi current password
        if current_pw != stored_pw and hash_password(current_pw) != stored_hash:
            st.error("❌ Current password incorrect.")
            return

        # hash dan update di Google Sheet
        new_hash = hash_password(new_pw)
        pw_col = df.columns.get_loc("Password") + 1
        hash_col = df.columns.get_loc("PasswordHash") + 1
        ws.update_cell(i + 2, pw_col, new_pw)
        ws.update_cell(i + 2, hash_col, new_hash)

        st.success("✅ Password updated successfully!")
