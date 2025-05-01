import streamlit as st
import pandas as pd
import plotly.express as px

# === CONFIGURATION ===
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1NThKamueqtVdkUIAQTEM8LpO9HThCUGIw47Qvi4XEao/edit?usp=sharing"
SHEET_NAME = "Sheet1"

# COLORS
COLOR_BG = "#FFFFFF"  # White background
COLOR_ACCENT = "#1E90FF"  # Blue Accent
COLOR_SECONDARY = "#D3D3D3"
TEXT_COLOR = "#000000"  # Dark text color

# USERS - Only admin user allowed
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
}

# === Helper: Get CSV export URL ===
def get_csv_url(sheet_url, sheet_name):
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# === Load data from Google Sheet ===
@st.cache_data(ttl=30)
def load_data():
    csv_url = get_csv_url(GOOGLE_SHEET_URL, SHEET_NAME)
    df = pd.read_csv(csv_url)
    df.columns = df.columns.str.strip()  # Strip any leading/trailing spaces from column names
    
    # Normalize 'Status' column to case-insensitive
    df['Status'] = df['Status'].fillna('').str.strip().str.lower().map(lambda x: 'Completed' if 'completed' in x and 'not' not in x else 'Not Completed')
    return df.copy()

# === Login system ===
def login():
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    if st.session_state.logged_in:
        return "admin", "admin"

    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button("Login"):
        user = USERS.get(username)
        if user and user["password"] == password:
            st.session_state.logged_in = True
            return username, user["role"]
        else:
            st.sidebar.error("Invalid username or password.")
    return None, None

# === Logout system ===
def logout_button():
    if st.sidebar.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.experimental_rerun()

# === Update tracker (Read-only view) ===
def update_status(df, selected_mentor, selected_week):
    st.subheader("✍️ Tracker View (Read-Only)")
    filtered_df = df[(df["Mentor"] == selected_mentor) & (df["Schedule"] == selected_week)]

    for i, row in filtered_df.iterrows():
        col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
        with col1:
            st.markdown(f"**👤 {row['Resource']}**")
        with col2:
            st.markdown(f"📅 Week: `{row['Schedule']}`")
        with col3:
            st.markdown(f"📌 Status: `{row['Status']}`")
        with col4:
            comment = row['Comments'] if pd.notna(row['Comments']) else "—"
            st.markdown(f"💬 Comment: {comment}")

    st.info("This is a live view from Google Sheet. Edit data directly in the Sheet.")

# === Chart visuals ===
def plot_completion_charts(df, selected_mentor, selected_week):
    # First Graph: Resource-wise completion status where Mentor and Week are filters
    df_filtered = df[(df["Mentor"] == selected_mentor) & (df["Schedule"] == selected_week)]
    df_bar = df_filtered.groupby(["Resource", "Schedule", "Status"]).size().reset_index(name="Count")
    
    bar_chart = px.bar(
        df_bar,
        x="Resource",
        y="Count",
        color="Status",
        title="📊 Completion Status by Resource (Filtered by Mentor and Week)",
        color_discrete_map={"Completed": "green", "Not Completed": "#FF6347"},
        barmode="stack",
        labels={"Status": "Completion Status"}
    )
    
    bar_chart.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(color=TEXT_COLOR),
        xaxis_title="Resource",
        yaxis_title="Count",
        title_x=0.5,
        title_y=0.95,
        title_font=dict(size=20),
    )

    # Second Graph: Mentor-wise completion status across all weeks (aggregated)
    df_mentor = df.groupby(["Mentor", "Status"]).size().reset_index(name="Count")
    
    mentor_chart = px.bar(
        df_mentor,
        x="Mentor",
        y="Count",
        color="Status",
        title="🎯 Mentor-wise Completion Status (Aggregated)",
        color_discrete_map={"Completed": "green", "Not Completed": "#FF6347"},
        barmode="stack",
        labels={"Status": "Completion Status"}
    )
    
    mentor_chart.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(color=TEXT_COLOR),
        xaxis_title="Mentor",
        yaxis_title="Count",
        title_x=0.5,
        title_y=0.95,
        title_font=dict(size=20),
    )

    return bar_chart, mentor_chart

# === Show progress ===
def show_progress(df):
    st.subheader("📈 Progress Overview")

    # Filters for Mentor and Week with unique keys for each selectbox
    mentors = df["Mentor"].dropna().unique()
    selected_mentor = st.selectbox("Select Mentor", mentors, key="mentor_selectbox")
    
    schedules = df["Schedule"].dropna().unique()
    selected_week = st.selectbox("Select Week", schedules, key="week_selectbox")

    bar, mentor_bar = plot_completion_charts(df, selected_mentor, selected_week)
    st.plotly_chart(bar, use_container_width=True)
    st.plotly_chart(mentor_bar, use_container_width=True)

# === MAIN APP ===
def main():
    st.set_page_config(page_title="Anaplan Batch 2 Tracker", layout="wide")

    # Adding a logo above the title (using the provided URL)
    st.markdown(
        f"""
        <div style='text-align:center;'>
            <img src='https://rb.gy/ilooum' width='200'/>
            <h1 style='color:{COLOR_ACCENT};text-align:center;'>Anaplan Learning Batch 2 Tracker</h1>
        </div>
        """,
        unsafe_allow_html=True
    )

    user, role = login()  # Fixed the syntax here
    if user and role == "admin":
        logout_button()
        df = load_data()

        tab1, tab2 = st.tabs(["✏️ Tracker View", "📊 Progress Overview"])
        with tab1:
            selected_mentor = st.selectbox("Select Mentor", df["Mentor"].dropna().unique(), key="mentor_selectbox_tab1")
            selected_week = st.selectbox("Select Week", df["Schedule"].dropna().unique(), key="week_selectbox_tab1")
            update_status(df, selected_mentor, selected_week)
        with tab2:
            show_progress(df)
    else:
        st.warning("Please login as admin to access the dashboard.")

if __name__ == "__main__":
    main()
