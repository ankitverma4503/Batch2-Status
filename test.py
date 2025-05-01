import streamlit as st
import pandas as pd
import plotly.express as px

# === CONFIGURATION ===
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1NThKamueqtVdkUIAQTEM8LpO9HThCUGIw47Qvi4XEao/edit?usp=sharing"
SHEET_NAME = "Sheet1"  # Ensure this matches your sheet tab name

# COLORS
COLOR_BG = "#000000"
COLOR_ACCENT = "#CD1C18"
COLOR_SECONDARY = "#D3D3D3"
TEXT_COLOR = "#FFFFFF"

# USERS - Only admin user allowed
USERS = {
    "admin": {"password": "admin123", "role": "admin"},
}

# === Helper: Get CSV export URL ===
def get_csv_url(sheet_url, sheet_name):
    sheet_id = sheet_url.split("/d/")[1].split("/")[0]
    return f"https://docs.google.com/spreadsheets/d/{sheet_id}/gviz/tq?tqx=out:csv&sheet={sheet_name}"

# === Load data from Google Sheet ===
@st.cache_data(ttl=30)  # refresh every 30 seconds
def load_data():
    csv_url = get_csv_url(GOOGLE_SHEET_URL, SHEET_NAME)
    df = pd.read_csv(csv_url)
    df.columns = df.columns.str.strip()  # clean column names
    return df.copy()

# === Login system ===
def login():
    st.sidebar.title("🔐 Login")
    username = st.sidebar.text_input("Username")
    password = st.sidebar.text_input("Password", type="password")
    if st.sidebar.button("Login"):
        user = USERS.get(username)
        if user and user["password"] == password:
            return username, user["role"]
        else:
            st.sidebar.error("Invalid username or password.")
    return None, None

# === Update tracker (Read-only view) ===
def update_status(df):
    st.subheader("✍️ Tracker View (Read-Only)")
    mentors = df["Mentor"].dropna().unique()

    for mentor in mentors:
        with st.expander(f"👨‍🏫 Mentor: {mentor}", expanded=False):
            mentor_df = df[df["Mentor"] == mentor].reset_index(drop=True)
            schedules = mentor_df["Schedule"].dropna().unique()

            selected_schedule = st.selectbox(
                f"Select Week for {mentor}", schedules, key=f"week_{mentor}"
            )

            filtered_df = mentor_df[mentor_df["Schedule"] == selected_schedule]

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
    df_filtered = df[df["Status"].isin(["Completed", "Not Completed"])]
    df_grouped = df_filtered.groupby(["Schedule", "Status"]).size().reset_index(name="Count")

    bar_chart = px.bar(
        df_grouped,
        x="Schedule",
        y="Count",
        color="Status",
        title="📊 Completion by Week",
        color_discrete_sequence=[COLOR_ACCENT, COLOR_SECONDARY]
    )

    pie_data = df_filtered["Status"].value_counts().reset_index()
    pie_data.columns = ["Status", "Count"]
    pie_chart = px.pie(
        pie_data,
        names="Status",
        values="Count",
        title="🎯 Overall Completion Distribution",
        color_discrete_sequence=[COLOR_ACCENT, COLOR_SECONDARY]
    )

    bar_chart.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(color=TEXT_COLOR)
    )
    pie_chart.update_layout(
        paper_bgcolor=COLOR_BG,
        plot_bgcolor=COLOR_BG,
        font=dict(color=TEXT_COLOR)
    )

    return bar_chart, pie_chart

# === Show progress ===
def show_progress(df):
    st.subheader("📈 Progress Overview")

    bar, pie = plot_completion_charts(df)
    st.plotly_chart(bar, use_container_width=True)
    st.plotly_chart(pie, use_container_width=True)

# === MAIN APP ===
def main():
    st.set_page_config(page_title="Anaplan Batch 2 Tracker", layout="wide")

    st.markdown(
        f"""
        <div style='background-color:{COLOR_BG};padding:20px;border-radius:10px;'>
            <h1 style='color:{COLOR_ACCENT};text-align:center;'>Anaplan Learning Batch 2 Tracker</h1>
            <p style='text-align:center;color:{TEXT_COLOR};'>Powered by <strong>Ankit</strong></p>
        </div>
        """,
        unsafe_allow_html=True
    )

    user, role = login()
    if user and role == "admin":
        df = load_data()

        # Optional: Manual refresh
        if st.button("🔄 Refresh Now"):
            st.cache_data.clear()
            st.experimental_rerun()

        tab1, tab2 = st.tabs(["✏️ Tracker View", "📊 Progress Overview"])
        with tab1:
            update_status(df)
        with tab2:
            show_progress(df)
    else:
        st.warning("Please login as admin to access the dashboard.")

if __name__ == "__main__":
    main()
