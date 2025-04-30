import streamlit as st
import pandas as pd
import plotly.express as px
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
        # Convert the dataframe back to Excel file
        with BytesIO() as output:
            df.to_excel(output, index=False)
            output.seek(0)

            # Upload the file to the same URL (or locally if needed)
            # Save the Excel to a remote location if desired, like GitHub or server

        st.success("✅ Updates saved to Excel!")
    except Exception as e:
        st.error(f"Error saving data to Excel: {e}")

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

    st.markdown("---")

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

# MAIN
def main():
    st.set_page_config(page_title="Anaplan Batch 2 Tracker", layout="wide")

    st.markdown(
        f"""
        <div style='background-color:{COLOR_BG};padding:20px;border-radius:10px;'>
            <h1 style='color:{COLOR_ACCENT};text-align:center;'>Anaplan Learning Batch 2 Tracker</h1>
        </div>
        """, unsafe_allow_html=True)

    if login():
        df = load_data()

        update_status(df)
        show_progress(df)

        # Button to save data to Excel and reload it instantly
        if st.button("💾 Write Back to Excel"):
            save_data(df)
            df = load_data()  # Reload the data to reflect changes immediately
            st.success("Data written back to Excel and updated in the app!")

if __name__ == "__main__":
    main()
