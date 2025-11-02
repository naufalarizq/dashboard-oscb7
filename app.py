import streamlit as st
import pandas as pd
import gspread
from google.oauth2.service_account import Credentials
import time
import altair as alt

# ==========================
# GOOGLE SHEETS CONNECTION
# ==========================
@st.cache_resource
def get_gspread_client():
    creds_dict = st.secrets["gcp_service_account"]
    creds = Credentials.from_service_account_info(creds_dict)
    scoped_creds = creds.with_scopes([
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ])
    client = gspread.authorize(scoped_creds)
    return client

# ==========================
# LOAD DATA
# ==========================
@st.cache_data(ttl=60)
def load_clean_data():
    try:
        SHEET_KEY = "1LoptadYNUgEJ9fHJShdwwCz2O-F-cxLAJ6YgucO2UrA"
        WORKSHEET_NAME = "OlahData"

        client = get_gspread_client()
        worksheet = client.open_by_key(SHEET_KEY).worksheet(WORKSHEET_NAME)

        data = worksheet.get_all_values()
        if not data or len(data) < 2:
            st.warning("The cleaned spreadsheet is empty or contains only headers.")
            return pd.DataFrame()

        headers = data[0]
        df = pd.DataFrame(data[1:], columns=headers)
        df.replace(["#N/A", "#ERROR!", "#VALUE!", "#REF!", ""], pd.NA, inplace=True)

        if 'Year' in df.columns:
            df['Achievement_Date'] = pd.to_datetime(df['Year'], format='%m/%d/%Y', errors='coerce')
            df['Month_Year'] = df['Achievement_Date'].dt.to_period('M').astype(str)
        if 'Batch' in df.columns:
            df['Batch'] = pd.to_numeric(df['Batch'], errors='coerce').astype('Int64')

        return df

    except gspread.exceptions.WorksheetNotFound:
        st.error(f"Worksheet '{WORKSHEET_NAME}' not found.")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Error while fetching data: {e}")
        return pd.DataFrame()

# ==========================
# SCORING FUNCTION (FINAL)
# ==========================
def calculate_points(df):
    """
    Hitung skor prestasi berdasarkan kombinasi Category, Achievement, dan Level.
    """
    scoring_table = {
        # ===============================
        # 🏆 COMPETITION (KOMPETISI)
        # ===============================
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "International"): 45,
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "Regional"): 35,
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "National"): 25,
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "Province"): 20,
        ("Competition (Kompetisi)", "Juara-1 Perorangan", "Local/IPB"): 0,

        ("Competition (Kompetisi)", "Juara-2 Perorangan", "International"): 40,
        ("Competition (Kompetisi)", "Juara-2 Perorangan", "Regional"): 30,
        ("Competition (Kompetisi)", "Juara-2 Perorangan", "National"): 20,
        ("Competition (Kompetisi)", "Juara-2 Perorangan", "Province"): 15,
        ("Competition (Kompetisi)", "Juara-2 Perorangan", "Local/IPB"): 0,

        ("Competition (Kompetisi)", "Juara-3 Perorangan", "International"): 35,
        ("Competition (Kompetisi)", "Juara-3 Perorangan", "Regional"): 25,
        ("Competition (Kompetisi)", "Juara-3 Perorangan", "National"): 15,
        ("Competition (Kompetisi)", "Juara-3 Perorangan", "Province"): 10,
        ("Competition (Kompetisi)", "Juara-3 Perorangan", "Local/IPB"): 0,

        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "International"): 28,
        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "Regional"): 20,
        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "National"): 12,
        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "Province"): 8,
        ("Competition (Kompetisi)", "Juara Kategori Perorangan", "Local/IPB"): 0,

        ("Competition (Kompetisi)", "Juara-1 Beregu", "International"): 35,
        ("Competition (Kompetisi)", "Juara-1 Beregu", "Regional"): 25,
        ("Competition (Kompetisi)", "Juara-1 Beregu", "National"): 15,
        ("Competition (Kompetisi)", "Juara-1 Beregu", "Province"): 10,
        ("Competition (Kompetisi)", "Juara-1 Beregu", "Local/IPB"): 0,

        ("Competition (Kompetisi)", "Juara-2 Beregu", "International"): 30,
        ("Competition (Kompetisi)", "Juara-2 Beregu", "Regional"): 20,
        ("Competition (Kompetisi)", "Juara-2 Beregu", "National"): 10,
        ("Competition (Kompetisi)", "Juara-2 Beregu", "Province"): 7,
        ("Competition (Kompetisi)", "Juara-2 Beregu", "Local/IPB"): 0,

        ("Competition (Kompetisi)", "Juara-3 Beregu", "International"): 25,
        ("Competition (Kompetisi)", "Juara-3 Beregu", "Regional"): 15,
        ("Competition (Kompetisi)", "Juara-3 Beregu", "National"): 8,
        ("Competition (Kompetisi)", "Juara-3 Beregu", "Province"): 6,
        ("Competition (Kompetisi)", "Juara-3 Beregu", "Local/IPB"): 0,

        ("Competition (Kompetisi)", "Juara Kategori Beregu", "International"): 20,
        ("Competition (Kompetisi)", "Juara Kategori Beregu", "Regional"): 13,
        ("Competition (Kompetisi)", "Juara Kategori Beregu", "National"): 7,
        ("Competition (Kompetisi)", "Juara Kategori Beregu", "Province"): 5,
        ("Competition (Kompetisi)", "Juara Kategori Beregu", "Local/IPB"): 0,

        # ===============================
        # 🧩 RECOGNITION (PENGAKUAN)
        # ===============================
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "International"): 50,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "Regional"): 40,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "National"): 30,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "Province"): 20,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri berlisensi", "Local/IPB"): 0,

        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "International"): 25,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "Regional"): 20,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "National"): 15,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "Province"): 10,
        ("Recognition (Pengakuan)", "Pelatih/Wasit/Juri tidak berlisensi", "Local/IPB"): 0,

        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "International"): 25,
        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "Regional"): 20,
        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "National"): 15,
        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "Province"): 10,
        ("Recognition (Pengakuan)", "Nara sumber/pembicara", "Local/IPB"): 5,

        ("Recognition (Pengakuan)", "Moderator", "International"): 20,
        ("Recognition (Pengakuan)", "Moderator", "Regional"): 15,
        ("Recognition (Pengakuan)", "Moderator", "National"): 10,
        ("Recognition (Pengakuan)", "Moderator", "Province"): 5,
        ("Recognition (Pengakuan)", "Moderator", "Local/IPB"): 5,

        ("Recognition (Pengakuan)", "Lainnya", "International"): 20,
        ("Recognition (Pengakuan)", "Lainnya", "Regional"): 15,
        ("Recognition (Pengakuan)", "Lainnya", "National"): 10,
        ("Recognition (Pengakuan)", "Lainnya", "Province"): 5,
        ("Recognition (Pengakuan)", "Lainnya", "Local/IPB"): 5,

        # ===============================
        # 🪙 AWARD (PENGHARGAAN)
        # ===============================
        ("Award (Penghargaan)", "Tanda Jasa", "International"): 50,
        ("Award (Penghargaan)", "Tanda Jasa", "Regional"): 40,
        ("Award (Penghargaan)", "Tanda Jasa", "National"): 30,
        ("Award (Penghargaan)", "Tanda Jasa", "Province"): 20,
        ("Award (Penghargaan)", "Tanda Jasa", "Local/IPB"): 0,

        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "International"): 36,
        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "Regional"): 30,
        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "National"): 20,
        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "Province"): 10,
        ("Award (Penghargaan)", "Penerima Hibah Kompetisi", "Local/IPB"): 0,

        ("Award (Penghargaan)", "Grand Final Emas", "International"): 25,
        ("Award (Penghargaan)", "Grand Final Emas", "Regional"): 20,
        ("Award (Penghargaan)", "Grand Final Emas", "National"): 10,
        ("Award (Penghargaan)", "Grand Final Emas", "Province"): 5,
        ("Award (Penghargaan)", "Grand Final Emas", "Local/IPB"): 3,

        ("Award (Penghargaan)", "Grand Final Perak", "International"): 25,
        ("Award (Penghargaan)", "Grand Final Perak", "Regional"): 15,
        ("Award (Penghargaan)", "Grand Final Perak", "National"): 7,
        ("Award (Penghargaan)", "Grand Final Perak", "Province"): 3,
        ("Award (Penghargaan)", "Grand Final Perak", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Grand Final Perunggu", "International"): 20,
        ("Award (Penghargaan)", "Grand Final Perunggu", "Regional"): 10,
        ("Award (Penghargaan)", "Grand Final Perunggu", "National"): 5,
        ("Award (Penghargaan)", "Grand Final Perunggu", "Province"): 3,
        ("Award (Penghargaan)", "Grand Final Perunggu", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Piagam Partisipasi", "International"): 10,
        ("Award (Penghargaan)", "Piagam Partisipasi", "Regional"): 5,
        ("Award (Penghargaan)", "Piagam Partisipasi", "National"): 3,
        ("Award (Penghargaan)", "Piagam Partisipasi", "Province"): 2,
        ("Award (Penghargaan)", "Piagam Partisipasi", "Local/IPB"): 1,

        ("Award (Penghargaan)", "Lainnya", "International"): 10,
        ("Award (Penghargaan)", "Lainnya", "Regional"): 5,
        ("Award (Penghargaan)", "Lainnya", "National"): 3,
        ("Award (Penghargaan)", "Lainnya", "Province"): 2,
        ("Award (Penghargaan)", "Lainnya", "Local/IPB"): 1,
        
        # ===============================
        # 🎨 CREATIVE WORKS (HASIL KARYA)
        # ===============================
        ("Creative Works (Hasil Karya)", "Patent", "International"): 50,
        ("Creative Works (Hasil Karya)", "Patent", "National"): 45,
        ("Creative Works (Hasil Karya)", "Patent Sederhana", "National"): 30,
        ("Creative Works (Hasil Karya)", "Hak Cipta", "National"): 30,
        ("Creative Works (Hasil Karya)", "Buku ber-ISBN penulis utama", "National"): 30,
        ("Creative Works (Hasil Karya)", "Buku ber-ISBN penulis kedua", "National"): 20,
        ("Creative Works (Hasil Karya)", "Penulis utama/korepondensi karya ilmiah bereputasi", "International"): 50,
        ("Creative Works (Hasil Karya)", "Penulis kedua karya ilmiah bereputasi", "International"): 30,
        ("Creative Works (Hasil Karya)", "Lainnya", "National"): 10,

        # ===============================
        # 🤝 HUMANITARIAN ACTION (PEMBERDAYAAN / AKSI KEMANUSIAAN)
        # ===============================
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Pemrakarsa / Pendiri", "International"): 50,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Pemrakarsa / Pendiri", "National"): 40,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Pemrakarsa / Pendiri", "Province"): 30,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Koordinator Relawan", "International"): 35,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Koordinator Relawan", "National"): 25,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Koordinator Relawan", "Province"): 15,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Relawan", "International"): 25,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Relawan", "National"): 15,
        ("Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)", "Relawan", "Province"): 5,

        # ===============================
        # 💼 ENTREPRENEURSHIP (KEWIRAUSAHAAN)
        # ===============================
        ("Entrepreneurship (Kewirausahaan)", "Kewirausahaan", "International"): 50,
        ("Entrepreneurship (Kewirausahaan)", "Kewirausahaan", "National"): 40,
        ("Entrepreneurship (Kewirausahaan)", "Kewirausahaan", "Province"): 30,
        ("Entrepreneurship (Kewirausahaan)", "Kewirausahaan", "Local/IPB"): 10,
    }

    required_cols = {"Category", "Achievement", "Level"}
    if not required_cols.issubset(df.columns):
        st.warning("Some required columns are missing: Category, Achievement, or Level.")
        df["Points"] = 0
        return df

    def get_score(row):
        key = (row["Category"], row["Achievement"], row["Level"])
        return scoring_table.get(key, 0)

    df["Points"] = df.apply(get_score, axis=1)
    return df



# ==========================
# DASHBOARD CONFIG
# ==========================
st.set_page_config(page_title="Student Achievement Dashboard", layout="wide")
st.title("🚀 Student Achievement Dashboard (OSC Batch 7)")

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

df_clean = load_clean_data()

# ==========================
# STATIC LABELS
# ==========================
CATEGORY_ORDER = [
    "Competition (Kompetisi)",
    "Recognition (Pengakuan)",
    "Award (Penghargaan)",
    "Organizational Career (Karier Organisasi)",
    "Creative Works (Hasil Karya)",
    "Humanitarian Action (Pemberdayaan/Aksi Kemanusiaan)",
    "Entrepreneurship (Kewirausahaan)"
]

FACULTY_ORDER = [
    "Fakultas Pertanian",
    "Sekolah Kedokteran Hewan dan Biomedis",
    "Fakultas Perikanan dan Ilmu Kelautan",
    "Fakultas Peternakan",
    "Fakultas Kehutanan",
    "Fakultas Teknologi Pertanian",
    "Fakultas Matematika dan IPA",
    "Fakultas Ekonomi dan Manajemen",
    "Fakultas Ekologi Manusia",
    "Sekolah Vokasi",
    "Sekolah Bisnis",
    "Fakultas Kedokteran",
    "Sekolah Sains data, Matematika dan Informatika"
]

LEVEL_ORDER = ["International", "National", "Regional", "Province", "Local/IPB"]

# ==========================
# MAIN DASHBOARD CONTENT
# ==========================
if not df_clean.empty:
    st.header("Achievement Summary")

    total_records = len(df_clean.dropna(subset=['StudentID']))
    st.metric("Total Recorded Achievements", value=total_records)
    category_counts = (
        df_clean['Category']
        .value_counts()
        .reindex(CATEGORY_ORDER, fill_value=0)
    )

    cols = st.columns(len(category_counts))
    for i, (category, count) in enumerate(category_counts.items()):
        cols[i].metric(label=category, value=count)

    st.markdown("---")

    # === LEADERBOARD ===
    st.header("🏆 Top 3 Students by Batch")
    st.info("Now using official scoring system ✅")

    df_points = calculate_points(df_clean.copy())
    leaderboard = df_points.groupby(['StudentID', 'FullName', 'Batch'])['Points'].sum().reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Batch 60")
        rank_60 = leaderboard[leaderboard['Batch'] == 60].sort_values(by='Points', ascending=False).head(3)
        st.dataframe(rank_60, use_container_width=True, hide_index=True)
    with col2:
        st.subheader("Batch 61")
        rank_61 = leaderboard[leaderboard['Batch'] == 61].sort_values(by='Points', ascending=False).head(3)
        st.dataframe(rank_61, use_container_width=True, hide_index=True)

    st.markdown("---")

    # === DISTRIBUTION CHARTS ===
    st.header("📊 Achievement Distribution")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("By Faculty")
        faculty_counts = (
            df_clean['Faculty']
            .value_counts()
            .reindex(FACULTY_ORDER, fill_value=0)
            .reset_index()
        )
        faculty_counts.columns = ['Faculty', 'Count']
        chart = (
            alt.Chart(faculty_counts)
            .mark_bar(size=20)  # ukuran batang
            .encode(
                x=alt.X('Count:Q', title='Number of Achievements'),
                y=alt.Y('Faculty:N', sort='-x', title=None),
                color=alt.Color('Faculty:N', legend=None),
                tooltip=['Faculty', 'Count']
            )
            .properties(
                width=700,   # lebar chart (default sekitar 400)
                height=500,  # tinggi chart
                title="Achievement Distribution by Faculty"
            )
        )
        st.altair_chart(chart, use_container_width=False)

    with col2:
        st.subheader("By Level")
        level_counts = (
            df_clean['Level']
            .value_counts()
            .reindex(LEVEL_ORDER, fill_value=0)
            .reset_index()
        )
        level_counts.columns = ['Level', 'Count']
        pie_chart = alt.Chart(level_counts).mark_arc(innerRadius=60).encode(
            theta=alt.Theta('Count:Q', stack=True),
            color=alt.Color('Level:N', legend=alt.Legend(title="Level")),
            tooltip=['Level', 'Count']
        ).properties(title="Achievement Distribution by Level")
        st.altair_chart(pie_chart, use_container_width=True)

    st.markdown("---")

    # === TIME SERIES ===
    st.header("📈 Monthly Achievement Trends")
    if 'Month_Year' in df_clean.columns:
        valid_monthly = df_clean.dropna(subset=['Achievement_Date'])
        monthly_counts = valid_monthly.dropna(subset=['Month_Year']) \
                                      .groupby('Month_Year') \
                                      .size() \
                                      .sort_index()
        st.line_chart(monthly_counts)
    else:
        st.warning("Column 'Year' (with date) not found.")
else:
    st.error("Failed to load data. Check your '.streamlit/secrets.toml' configuration.")
