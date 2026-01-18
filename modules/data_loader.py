import pandas as pd
import streamlit as st
import gspread
from google.oauth2.service_account import Credentials
from modules.auth import get_gspread_client

@st.cache_data(ttl=60)
def load_clean_data():
    # SHEET_KEY = "1LoptadYNUgEJ9fHJShdwwCz2O-F-cxLAJ6YgucO2UrA"
    SHEET_KEY = "1Z_B-LYO3-EtTWliyXEm_8TJREwGEQaKN-5p1T68K484"
    # WORKSHEET_NAME = "OlahData"
    WORKSHEET_NAME = "ImportData"

    try:
        client = get_gspread_client()
        worksheet = client.open_by_key(SHEET_KEY).worksheet(WORKSHEET_NAME)
        data = worksheet.get_all_values()

        if not data or len(data) < 2:
            st.warning("Spreadsheet is empty or has only headers.")
            return pd.DataFrame()

        df = pd.DataFrame(data[1:], columns=data[0])
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
        st.error(f"Error fetching data: {e}")
        return pd.DataFrame()
