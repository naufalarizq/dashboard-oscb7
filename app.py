import streamlit as st
import pandas as pd
from modules.data_loader import load_clean_data
from modules.scoring import calculate_points
from modules.constants import CATEGORY_ORDER, FACULTY_ORDER, LEVEL_ORDER
from modules.charts import faculty_chart, level_pie_chart
from modules.auth import login  # ✅ import modul login yang tadi

st.set_page_config(page_title="Student Achievement Dashboard", layout="wide")
st.title("🚀 Achievement Dashboard OSC Batch 7")

# === Tombol Refresh ===
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# === Load Data ===
df_clean = load_clean_data()

if not df_clean.empty:
    # --- Bagian Publik ---
    st.header("🏆 Overall Achievement Summary")

    total_records = len(df_clean.dropna(subset=['StudentID']))
    st.metric("Total Recorded Achievements", value=total_records)

    category_counts = df_clean['Category'].value_counts().reindex(CATEGORY_ORDER, fill_value=0)
    cols = st.columns(len(category_counts))
    for i, (cat, count) in enumerate(category_counts.items()):
        cols[i].metric(cat, count)

    st.markdown("---")

    # === Leaderboard Umum ===
    st.header("🏅 Top 5 Students by Batch")
    df_points = calculate_points(df_clean.copy())
    leaderboard = df_points.groupby(['StudentID', 'FullName', 'Batch'])['Points'].sum().reset_index()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Batch 60")
        st.dataframe(
            leaderboard[leaderboard['Batch'] == 60].nlargest(5, 'Points'),
            use_container_width=True, hide_index=True
        )
    with col2:
        st.subheader("Batch 61")
        st.dataframe(
            leaderboard[leaderboard['Batch'] == 61].nlargest(5, 'Points'),
            use_container_width=True, hide_index=True
        )

    st.markdown("---")

    # === Grafik Umum ===
    st.header("📊 Achievement Distribution")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("By Faculty")
        faculty_chart(df_clean, FACULTY_ORDER)
    with col2:
        st.subheader("By Level")
        level_pie_chart(df_clean, LEVEL_ORDER)

    st.markdown("---")

    # === Tren Bulanan Umum ===
    st.header("📈 Monthly Achievement Trends")

    if 'Month_Year' in df_clean.columns:
        valid_monthly = df_clean.dropna(subset=['Achievement_Date'])
        monthly_counts = valid_monthly.dropna(subset=['Month_Year']) \
                        .groupby('Month_Year') \
                        .size().sort_index()

        st.line_chart(monthly_counts)

    else:
        st.warning("Column 'Month_Year' (with date) not found.")

    st.markdown("---")

    # --- Bagian Login Mahasiswa ---
    st.header("🎓 View Your Personal Achievement Records")

    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.info("🔒 Please log in to see your own achievements.")
        login()
    else:
        st.success(f"Welcome back, {st.session_state.user_name}!")
        user_id = st.session_state.user_id
        df_user = df_clean[df_clean["StudentID"] == user_id]

        total_records = len(df_user)

        # Hitung ulang poin user berdasarkan data pribadinya
        df_user_points = calculate_points(df_user.copy())
        total_records = len(df_user_points)
        total_points = df_user_points["Points"].sum()

        # ✅ Tampilkan metric berdampingan
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Your Total Achievements", value=total_records)
        with col2:
            st.metric("🏆 Your Total Points", value=total_points)

        if total_records > 0:
            st.subheader("📋 Your Achievement Records")
            df_user_data = df_user.drop(columns=['Achievement_Date', 'Month_Year', 'Batch', 'Faculty', 'Major'])
            st.dataframe(df_user_data, use_container_width=True, hide_index=True)

            st.subheader("📈 Your Monthly Trend")
            if 'Month_Year' in df_user.columns:
                monthly_counts = (
                    df_user.dropna(subset=['Month_Year'])
                    .groupby('Month_Year')
                    .size()
                    .sort_index()
                )
                st.line_chart(monthly_counts)
        else:
            st.warning("You don’t have any recorded achievements yet.")

else:
    st.error("❌ Failed to load data. Check your secrets configuration.")
