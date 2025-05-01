import streamlit as st
import pandas as pd
import plotly.express as px

# === CONFIGURATION ===
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1NThKamueqtVdkUIAQTEM8LpO9HThCUGIw47Qvi4XEao/edit?usp=sharing"
SHEET_NAME = "Sheet1"

# COLORS for better visibility
COLOR_BG = "#FFFFFF"  # White background for better contrast
COLOR_ACCENT = "#1E90FF"  # Blue for accents
COLOR_SECONDARY = "#FF6347"  # Tomato red for secondary color (for Not Completed)
TEXT_COLOR = "#000000"  # Black text for visibility

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
    df.columns = df.columns.str.strip()

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
def update_status(df):
    st.subheader("✍️ Tracker View (Read-Only)")
    mentors = df["Mentor"].dropna().unique()

    selected_mentor = st.selectbox("Select Mentor", mentors)
    schedules = df["Schedule"].dropna().unique()
    selected_week = st.selectbox("Select Week", schedules)

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
def plot_completion_charts(df):
    # First Graph: Completion by Week
    df_filtered = df[df["Status"].isin(["Completed", "Not Completed"])]
    
    # Group by Week and Status (Completed vs Not Completed)
    df_bar = df_filtered.groupby(["Schedule", "Status"]).size().reset_index(name="Count")
    
    # Plot bar chart: Week on Y-axis, Count of Completion Status on X-axis
    bar_chart = px.bar(
        df_bar,
        y="Schedule",
        x="Count",
        color="Status",
        title="📊 Completion Status by Week (Count)",
        color_discrete_map={"Completed": COLOR_ACCENT, "Not Completed": COLOR_SECONDARY},
        barmode="stack",
        labels={"Status": "Completion Status", "Count": "Count of Completion"},
        category_orders={"Status": ["Completed", "Not Completed"]}
    )
    
    bar_chart.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(color=TEXT_COLOR),
        yaxis_title="Week",
        xaxis_title="Count of Completion Status",
        title_x=0.5,
        title_y=0.95,
        title_font=dict(size=20),
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True)
    )

    # Second Graph: Mentor-wise Completion by Week
    df_mentor = df_filtered.groupby(["Mentor", "Schedule", "Status"]).size().reset_index(name="Count")
    
    mentor_chart = px.bar(
        df_mentor,
        y="Schedule",
        x="Count",
        color="Mentor",
        title="🎯 Mentor-wise Completion Status (by Week)",
        color_discrete_sequence=px.colors.qualitative.Set1,
        barmode="stack",
        labels={"Status": "Completion Status"}
    )
    
    mentor_chart.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(color=TEXT_COLOR),
        yaxis_title="Week",
        xaxis_title="Count of Resources Completed",
        title_x=0.5,
        title_y=0.95,
        title_font=dict(size=20),
        xaxis=dict(showgrid=True),
        yaxis=dict(showgrid=True)
    )

    return bar_chart, mentor_chart

# === Show progress ===
def show_progress(df):
    st.subheader("📈 Progress Overview")

    bar, mentor_bar = plot_completion_charts(df)
    st.plotly_chart(bar, use_container_width=True)
    st.plotly_chart(mentor_bar, use_container_width=True)

# === MAIN APP ===
def main():
    st.set_page_config(page_title="Anaplan Batch 2 Tracker", layout="wide")

    st.markdown(
        f"""
        <div style='background-color:{COLOR_ACCENT};padding:20px;border-radius:10px;'>
            <h1 style='color:#FFFFFF;text-align:center;'>Anaplan Learning Batch 2 Tracker</h1>
            <p style='text-align:center;color:#FFFFFF;'>Powered by <strong>Ankit</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    user, role = login()
    if user and role == "admin":
        logout_button()
        df = load_data()

        tab1, tab2 = st.tabs(["✏️ Tracker View", "📊 Progress Overview"])
        with tab1:
            update_status(df)
        with tab2:
            show_progress(df)
    else:
        st.warning("Please login as admin to access the dashboard.")

if __name__ == "__main__":
    main()
