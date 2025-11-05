import gspread
from google.oauth2.service_account import Credentials
import streamlit as st
import pandas as pd
import hashlib

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

# ✅ load user database (bisa dari lokal atau secrets)
@st.cache_data
def load_user_database():
    # 1️⃣ coba baca dari file CSV lokal dulu
    try:
        df = pd.read_csv("data/database.csv")
        if "StudentID" not in df.columns or "PasswordHash" not in df.columns:
            st.warning("File database.csv tidak memiliki kolom yang sesuai.")
            return pd.DataFrame(columns=["StudentID", "FullName", "Faculty", "Batch", "Email", "PasswordHash"])
        return df
    except FileNotFoundError:
        # 2️⃣ fallback ke secrets.toml
        users = st.secrets.get("users", {})
        if not users:
            st.warning("⚠️ Tidak ada data user ditemukan di secrets.toml")
            return pd.DataFrame(columns=["StudentID", "FullName", "Faculty", "Batch", "Email", "PasswordHash"])

        data = []
        for sid, info in users.items():
            raw_pw = str(info.get("password", sid[-6:]))  # pakai password dari secrets atau default
            data.append({
                "StudentID": sid,
                "FullName": info.get("name", "Unknown"),
                "Faculty": info.get("faculty", "-"),
                "Batch": info.get("batch", "-"),
                "Email": info.get("email", "-"),
                "PasswordHash": hash_password(raw_pw)
            })

        return pd.DataFrame(data)

# ✅ fungsi login
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
            hashed_pw = hash_password(password)
            user = db[
                (db["StudentID"].astype(str) == nim) &
                (db["PasswordHash"] == hashed_pw)
            ]

            if not user.empty:
                st.session_state.logged_in = True
                st.session_state.user_id = user.iloc[0]["StudentID"]
                st.session_state.user_name = user.iloc[0]["FullName"]
                st.session_state.user_faculty = user.iloc[0]["Faculty"]
                st.session_state.user_email = user.iloc[0]["Email"]
                st.success(f"Welcome, {st.session_state.user_name}! 🎉")
                st.rerun()
            else:
                st.error("❌ Invalid Student ID or password.")

    else:
        st.sidebar.success(f"Logged in as: {st.session_state.user_name}")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_name = None
            st.rerun()
        return True  # sudah login
    return st.session_state.logged_in


# ✅ ubah password (opsional)
def change_password(student_id, old_password, new_password):
    db = load_user_database()
    hashed_old = hash_password(old_password)
    user = db[
        (db["StudentID"].astype(str) == student_id) &
        (db["PasswordHash"] == hashed_old)
    ]

    if user.empty:
        return False, "Password lama salah."

    db.loc[db["StudentID"] == student_id, "PasswordHash"] = hash_password(new_password)
    db.to_csv("data/database.csv", index=False)
    return True, "Password berhasil diubah."
