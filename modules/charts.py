import altair as alt
import streamlit as st

def faculty_chart(df, FACULTY_ORDER):
    faculty_counts = (
        df['Faculty']
        .value_counts()
        .reindex(FACULTY_ORDER, fill_value=0)
        .reset_index()
    )
    faculty_counts.columns = ['Faculty', 'Count']

    chart = (
        alt.Chart(faculty_counts)
        .mark_bar(size=20)
        .encode(
            x=alt.X('Count:Q', title='Number of Achievements'),
            y=alt.Y('Faculty:N', sort='-x', title=None),
            color=alt.Color('Faculty:N', legend=None),
            tooltip=['Faculty', 'Count']
        )
        .properties(width=700, height=500, title="Achievement Distribution by Faculty")
    )
    st.altair_chart(chart, use_container_width=False)


def level_pie_chart(df, LEVEL_ORDER):
    level_counts = (
        df['Level']
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
