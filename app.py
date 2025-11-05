import streamlit as st
import pandas as pd
from modules.data_loader import load_clean_data
from modules.scoring import calculate_points
from modules.constants import CATEGORY_ORDER, FACULTY_ORDER, LEVEL_ORDER
from modules.charts import faculty_chart, level_pie_chart

st.set_page_config(page_title="Student Achievement Dashboard", layout="wide")
st.title("🚀 Achievement Dashboard OSC Batch 7")

# Tombol refresh cache
if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

# Load data
df_clean = load_clean_data()

if not df_clean.empty:
    st.header("Achievement Summary")

    # Total pencapaian
    total_records = len(df_clean.dropna(subset=['StudentID']))
    st.metric("Total Recorded Achievements", value=total_records)

    # Jumlah per kategori
    category_counts = df_clean['Category'].value_counts().reindex(CATEGORY_ORDER, fill_value=0)
    cols = st.columns(len(category_counts))
    for i, (cat, count) in enumerate(category_counts.items()):
        cols[i].metric(cat, count)

    st.markdown("---")

    # Top 5 per batch
    st.header("🏆 Top 5 Students by Batch")
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

    # Distribusi capaian
    st.header("📊 Achievement Distribution")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("By Faculty")
        faculty_chart(df_clean, FACULTY_ORDER)
    with col2:
        st.subheader("By Level")
        level_pie_chart(df_clean, LEVEL_ORDER)

    st.markdown("---")

    st.header("📈 Monthly Achievement Trends")

    if 'Month_Year' in df_clean.columns:
        valid_monthly = df_clean.dropna(subset=['Achievement_Date', 'Month_Year'])

        monthly_counts = (
            valid_monthly
            .groupby('Month_Year')
            .size()
            .sort_index()
        )

        st.line_chart(monthly_counts)

    else:
        st.warning("Column 'Month_Year' (with date) not found.")



