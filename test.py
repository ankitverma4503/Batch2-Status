import streamlit as st
import pandas as pd
import plotly.express as px
import os
import requests
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

# GitHub setup
GITHUB_TOKEN = st.secrets["github"]["github_token"]
REPO_NAME = "Batch2-Status"
BRANCH_NAME = "main"
FILE_PATH = "Batch 2 tracker.xlsx"
GITHUB_API_URL = f"https://api.github.com/repos/ankitverma4503/{REPO_NAME}/contents/{FILE_PATH}"

# Load Excel
def load_data():
    try:
        # Fetch the latest version of the file from GitHub
        response = requests.get(EXCEL_URL)
        if response.status_code == 200:
            df = pd.read_excel(BytesIO(response.content), sheet_name=SHEET_NAME)
            df.columns = df.columns.str.strip()  # Clean column names
            return df
        else:
            st.error("Error fetching the Excel file from GitHub.")
            st.stop()
    except Exception as e:
        st.error(f"Error loading Excel file: {e}")
        st.stop()

# Save Excel file back to GitHub
def save_data(df):
    try:
        # Convert the dataframe back to Excel file
        with BytesIO() as output:
            df.to_excel(output, index=False)
            output.seek(0)
            file_content = output.read()

        # Fetch the current file details from GitHub (for versioning)
        response = requests.get(GITHUB_API_URL, headers={"Authorization": f"token {GITHUB_TOKEN}"})
        if response.status_code == 200:
            file_info = response.json()
            sha = file_info["sha"]  # Get the sha of the file to update

            # Prepare data for GitHub API to update file
            update_data = {
                "message": "Update tracker data",
                "sha": sha,
                "content": file_content.encode("base64"),  # Base64 encode the file
                "branch": BRANCH_NAME
            }

            # Send PUT request to GitHub to update the file
            update_response = requests.put(GITHUB_API_URL, json=update_data, headers={"Authorization": f"token {GITHUB_TOKEN}"})

            if update_response.status_code == 200:
                st.success("✅ Updates saved to GitHub!")
            else:
                st.error(f"Failed to update file on GitHub: {update_response.text}")
        else:
            st.error(f"Failed to fetch file info from GitHub: {response.text}")

    except Exception as e:
        st.error(f"Error saving file to GitHub: {e}")

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
                    with reset_col:
                        if st.button("♻️", key=f"reset_{mentor}_{i}"):
                            df.loc[(df["Mentor"] == mentor) & (df["Resource"] == row["Resource"]) & (df["Schedule"] == row["Schedule"]), "Status"] = ""
                            df.loc[(df["Mentor"] == mentor) & (df["Resource"] == row["Resource"]) & (df["Schedule"] == row["Schedule"]), "Comments"] = ""
                            save_data(df)
                    with del_col:
                        if st.button("❌", key=f"delete_{mentor}_{i}"):
                            df.drop(index=row.name, inplace=True)
                            df.reset_index(drop=True, inplace=True)
                            save_data(df)
                            st.rerun()

    st.markdown("---")
    if st.button("🔁 Reset Entire Dashboard"):
        df["Status"] = ""
        df["Comments"] = ""
        save_data(df)
        st.rerun()

# Enhanced Charts
def show_progress(df):
    st.subheader("📊 Progress Overview")

    # Week and Mentor Filters
    st.markdown("### 📅 Filter by Week and Mentor")
    selected_week = st.selectbox("Select Week", options=["All"] + sorted(df["Schedule"].dropna().unique()), key="week_filter")
    selected_mentor = st.selectbox("Select Mentor", options=["All"] + sorted(df["Mentor"].dropna().unique()), key="mentor_filter")

    # Filter data based on Week and Mentor
    filtered_df = df[df["Status"].isin(["Completed", "Not Completed"])]
    if selected_week != "All":
        filtered_df = filtered_df[filtered_df["Schedule"] == selected_week]
    if selected_mentor != "All":
        filtered_df = filtered_df[filtered_df["Mentor"] == selected_mentor]

    # Bar Chart - Resources progress under selected mentor and week
    bar_data = filtered_df.groupby(["Mentor", "Resource", "Status"]).size().reset_index(name="Count")
    bar_chart = px.bar(
        bar_data,
        x="Resource",
        y="Count",
        color="Status",
        title=f"🔍 Progress for Mentor: {selected_mentor} (Week: {selected_week})",
        color_discrete_map={"Completed": COLOR_COMPLETED, "Not Completed": COLOR_SECONDARY}
    )

    bar_chart.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(color=TEXT_COLOR),
        xaxis=dict(tickmode='linear'),
        barmode="stack",
        xaxis_title="Resource",
        yaxis_title="Count",
        bargap=0.1
    )

    st.plotly_chart(bar_chart, use_container_width=True)

    # Bar Chart - Overall progress across all mentors and weeks
    overall_progress_data = df.groupby(["Mentor", "Status"]).size().reset_index(name="Count")
    overall_bar_chart = px.bar(
        overall_progress_data,
        x="Mentor",
        y="Count",
        color="Status",
        title="🔍 Overall Progress Across All Mentors & Weeks",
        color_discrete_map={"Completed": COLOR_COMPLETED, "Not Completed": COLOR_SECONDARY}
    )

    overall_bar_chart.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(color=TEXT_COLOR),
        xaxis=dict(tickmode='linear'),
        barmode="stack",
        xaxis_title="Mentor",
        yaxis_title="Count",
        bargap=0.1
    )

    st.plotly_chart(overall_bar_chart, use_container_width=True)

# MAIN
def main():
    st.set_page_config(page_title="Anaplan Batch 2 Tracker", layout="wide")

    st.markdown(
        f"""
        <div style='background-color:{COLOR_BG};padding:20px;border-radius:10px;'>
            <h1 style='color:{COLOR_ACCENT};text-align:center;'>Anaplan Learning Batch 2 Tracker</h1>
            <p style='text-align:center;color:{TEXT_COLOR};'>Powered by <strong>Anaplan</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    if login():
        df = load_data()
        tab1, tab2 = st.tabs(["✏️ Update Tracker", "📈 Progress Overview"])
        with tab1:
            update_status(df)
        with tab2:
            show_progress(df)
    else:
        st.warning("Please login as admin to access the dashboard.")

if __name__ == "__main__":
    main()
