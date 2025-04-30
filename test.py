import streamlit as st
import pandas as pd
import plotly.express as px
import openpyxl
from io import BytesIO

# CONFIGURATION
EXCEL_URL = "https://github.com/ankitverma4503/Batch2-Status/raw/main/Batch%202%20tracker.xlsx"
SHEET_NAME = 0

# COLORS
COLOR_BG = "#000000"
COLOR_ACCENT = "#CD1C18"
COLOR_SECONDARY = "#D3D3D3"
TEXT_COLOR = "#FFFFFF"
COLOR_COMPLETED = "#28A745"  # Green for Completed

# USERS
USERS = {
    "admin": {"password": "anaplan@batch2@A", "role": "admin"},
}

# Load Excel
@st.cache_data
def load_data():
    try:
        df = pd.read_excel(EXCEL_URL, sheet_name=SHEET_NAME)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        st.stop()

def save_data(df):
    try:
        # Save to Excel
        with BytesIO() as buffer:
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Sheet1')
            buffer.seek(0)
            with open(EXCEL_URL, 'wb') as f:
                f.write(buffer.read())
        st.success("✅ Updates saved!")
    except Exception as e:
        st.error(f"Error saving file: {e}")

# Login
def login():
    st.sidebar.title("🔐 Login")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.username = None

    if not st.session_state.logged_in:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.session_state.username = username
                st.sidebar.success(f"Welcome back, {st.session_state.username}! 👋")
                st.rerun()
            else:
                st.sidebar.error("Invalid username or password.")
    else:
        st.sidebar.success(f"Welcome, {st.session_state.username}!")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.rerun()

    return st.session_state.logged_in

# Update Tracker
def update_status(df):
    st.subheader("✍️ Update Tracker")
    mentors = df["Mentor"].dropna().unique()

    for mentor in mentors:
        with st.expander(f"👨‍🏫 Mentor: {mentor}", expanded=False):
            mentor_df = df[df["Mentor"] == mentor].reset_index(drop=True)
            schedules = mentor_df["Schedule"].dropna().unique()
            selected_schedule = st.selectbox(f"Select Week for {mentor}", schedules, key=f"week_select_{mentor}")
            filtered_df = mentor_df[mentor_df["Schedule"] == selected_schedule]

            for i, row in filtered_df.iterrows():
                col1, col2, col3, col4, col5 = st.columns([2, 2, 2, 3, 3])
                with col1:
                    st.markdown(f"**👤 {row['Resource']}**")
                with col2:
                    st.markdown(f"📆 Week: {row['Schedule']}")
                with col3:
                    status = st.selectbox(
                        "Status", ["Completed", "Not Completed"],
                        index=0 if row["Status"] == "Completed" else 1,
                        key=f"status_{mentor}_{i}"
                    )
                with col4:
                    comments = st.text_input(
                        "Comment", value=row["Comments"] if pd.notna(row["Comments"]) else "",
                        key=f"comment_{mentor}_{i}"
                    )
                with col5:
                    save_col, reset_col, del_col = st.columns(3)
                    with save_col:
                        if st.button("💾", key=f"save_{mentor}_{i}"):
                            df.loc[(df["Mentor"] == mentor) & (df["Resource"] == row["Resource"]) & (df["Schedule"] == row["Schedule"]), "Status"] = status
                            df.loc[(df["Mentor"] == mentor) & (df["Resource"] == row["Resource"]) & (df["Schedule"] == row["Schedule"]), "Comments"] = comments
                            save_data(df)
                            st.experimental_rerun()
                    with reset_col:
                        if st.button("♻️", key=f"reset_{mentor}_{i}"):
                            df.loc[(df["Mentor"] == mentor) & (df["Resource"] == row["Resource"]) & (df["Schedule"] == row["Schedule"]), "Status"] = ""
                            df.loc[(df["Mentor"] == mentor) & (df["Resource"] == row["Resource"]) & (df["Schedule"] == row["Schedule"]), "Comments"] = ""
                            save_data(df)
                            st.experimental_rerun()
                    with del_col:
                        if st.button("❌", key=f"delete_{mentor}_{i}"):
                            df.drop(index=row.name, inplace=True)
                            df.reset_index(drop=True, inplace=True)
                            save_data(df)
                            st.experimental_rerun()

    st.markdown("---")
    if st.button("🔁 Reset Entire Dashboard"):
        df["Status"] = ""
        df["Comments"] = ""
        save_data(df)
        st.experimental_rerun()

# Enhanced Charts
def show_progress(df):
    st.subheader("📊 Progress Overview")

    # Week and Mentor Filters
    st.markdown("### 📅 Filter by Week and Mentor")
    selected_week = st.selectbox("Select Week", options=["All"] + sorted(df["Schedule"].dropna().unique()), key="week_filter")
    selected_mentor = st.selectbox("Select Mentor", options=["All"] + sorted(df["Mentor"].dropna().unique()), key="mentor_filter")

    # Filter data based on Week and Mentor
    filtered_df = df[df["Status"].isin(["Completed", "Not Completed"])]
    if selected
::contentReference[oaicite:7]{index=7}
 
