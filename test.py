import streamlit as st
import pandas as pd
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIGURATION ===
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1NThKamueqtVdkUIAQTEM8LpO9HThCUGIw47Qvi4XEao"
SHEET_NAME = "Sheet1"

# === UI COLORS ===
COLOR_BG = "#000000"
COLOR_ACCENT = "#CD1C18"
COLOR_SECONDARY = "#D3D3D3"
TEXT_COLOR = "#FFFFFF"
COLOR_COMPLETED = "#28A745"

# === Dummy user login ===
USERS = {
    "admin": {"password": "anaplan@batch2@A", "role": "admin"},
}

# === Service Account Credential (Embedded) ===
service_account_info = {
  "type": "service_account",
  "project_id": "anaplantracker",
  "private_key_id": "c0883a271986e1f69eaf7ce1a4b6faec790b27d7",
  "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQCY8Le/qRTZFnMl\nP01G1MtnXiriSrSfvxXg0h950b3/MmbLC8iZ2m65x8wbbORBhFWl9hqyEeBkCrBu\nKhopT27cbd65+1tulu8PmL7/Kp1rAekKuZP4MpnqouBhlteLjUzDH2uh0/SmzkCS\nmzHH0Yxj4GDmm5u4MihIIGtoUOkiWDRDZfwOPpXkI29tgJg9iPSO5YifSnJ3wYsu\nV7q3fEyszLv+UBfpzfGBkW82p24V1zBsmXZ5aMDQdH97AUENJ+zOKdJwk6WdgjKb\n/sJ/uMGFxoDNgu0t9Rcr5FAZTuKH3lzbyRJ69bDhwDWFldVy0KuHP/V+IPh1lVAG\noa/HFIYrAgMBAAECggEAHRPHG51d5VgrVC2Q16KleWWh6Zwicyy1UCUi7to9sUM3\n3+rBnN62poOh/qTZUMuELSV5NdnIO7z8hjVi+++qOCZ7bgin/YKcuO5lgcXsX+fh\nErTtuQaF1OJanrM7D8ExkvdqUz4lCYG1LSpscH0an/KM+csj9AU1O2FOimq3qFup\nReHfRYDQ7cs9/HJVoZ5BUmAnC1qFxBLHafOs1ccEqjDegx28VJg3SAFB67kenUgH\njlri5yPZXT1S0P+pWkzXjeY2u3J2mIJdhKtl2xHIy3M7IHfV5ccd69Kf94cSjj5K\n1vwZFWmReMbGItJEwBuJkk9MkAgCCa76l0rgn76OIQKBgQDUdX/olZg3rY5ZpybQ\nj5vC8I6POSpABMA5Ie2F/MJVDTCg25f2xm/KrwnVL/ZnxBvTKjx2xCpRTOkGwn42\nWgVGFMo5zvhYq9Nx9eln1S80+jLnUrmT8x6EymBFE71Wx9x14+g6G9NdfmOtzJAX\nGxZBb4kQ/yygC/XNAa6503H49QKBgQC4SJ2RJFQNib9++bVfD7oD/naq7KCLPFef\niDN/PVF2aC/bR51EWMaGzrz7JXKZirZqhh0y8tMYIYcIVDKeV57fs+m7m2sZb7tI\n7ZBUiK9wKq6qvobQXK09bO2SARF2RfLCH8JFj9Bph4RUPlCe+25HSpFbrM0E9kyq\na6XK6oeOnwKBgHLuoWQz0OWF2PT87I10sqFxOt2V4hpBt67wgKq0Ani6Ku1J/do8\nnOs7Z4lRae3Wc+r29UCWfAIBJipG+rnyVtoDkyZUpZpqUXdbvYkzFVeGZhUndkbo\nBUF2rT+RHyMb+VI5GT6eIOh53/h8KhKlz5NUgASW1hA6iBz/5QKXtRclAoGAIKm+\nQ9uMilm/92GLJC5Fai/QGLuYORWY8k3R0turdLFCyjsHRPX3Oi2qkVkx1sUfUAI1\narJfeAd5R6Ck2CvvnPbmlroVYYzMRUDWNCWF8vudueXLP2Mt0ZVdBmPqFGyRepbm\neC3lYs8CRWxGHeeyxDATU4xtSlPdgtdRq4WmQUECgYEAzwmfPh/qiIsv6Iy7OdQt\np3TfmYZ8CaTA//CL1y9DL7Pifq/v4XJQaV+Kaw6zTErWj2h3/K1p2PVjIaI9Fk5B\nKQNQJObDBlXmvt188yF2nIo0fp37hKavDRvrDsOsIc48DkcFWWYgTFTeIZxtHiSI\n/lXjxguXqabzOseeqE9D3jg=\n-----END PRIVATE KEY-----\n",
  "client_email": "streamlit-sheets-bot@anaplantracker.iam.gserviceaccount.com",
  "client_id": "106601757238526571140",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/streamlit-sheets-bot%40anaplantracker.iam.gserviceaccount.com",
  "universe_domain": "googleapis.com"
}

# === GOOGLE SHEET AUTH ===
def authorize_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    gc = gspread.authorize(creds)
    return gc

# === LOAD & SAVE DATA ===
def load_data():
    try:
        gc = authorize_gsheet()
        worksheet = gc.open_by_url(GOOGLE_SHEET_URL).worksheet(SHEET_NAME)
        df = pd.DataFrame(worksheet.get_all_records())
        return df, worksheet
    except Exception as e:
        st.error(f"Failed to load Google Sheet: {e}")
        st.stop()

def save_data(df, worksheet):
    try:
        worksheet.clear()
        worksheet.update([df.columns.values.tolist()] + df.values.tolist())
        st.success("✅ Data saved to Google Sheet!")
    except Exception as e:
        st.error(f"Error saving data: {e}")

# === USER LOGIN ===
def login():
    st.sidebar.title("🔐 Login")
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        username = st.sidebar.text_input("Username")
        password = st.sidebar.text_input("Password", type="password")
        if st.sidebar.button("Login"):
            user = USERS.get(username)
            if user and user["password"] == password:
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.sidebar.error("Invalid credentials")
    else:
        st.sidebar.success("Logged in")
        if st.sidebar.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()
    return st.session_state.logged_in

# === UPDATE UI ===
def update_status(df):
    st.subheader("✍️ Update Tracker")
    mentors = df["Mentor"].dropna().unique()

    for mentor in mentors:
        with st.expander(f"👨‍🏫 Mentor: {mentor}"):
            mentor_df = df[df["Mentor"] == mentor].reset_index(drop=True)
            weeks = mentor_df["Schedule"].dropna().unique()
            selected_week = st.selectbox(f"Select Week for {mentor}", weeks, key=f"week_{mentor}")

            filtered_df = mentor_df[mentor_df["Schedule"] == selected_week]
            for i, row in filtered_df.iterrows():
                col1, col2, col3, col4 = st.columns([2, 2, 2, 4])
                with col1:
                    st.markdown(f"👤 {row['Resource']}")
                with col2:
                    st.markdown(f"📅 {row['Schedule']}")
                with col3:
                    status = st.selectbox("Status", ["Completed", "Not Completed"],
                                          index=0 if row["Status"] == "Completed" else 1,
                                          key=f"status_{mentor}_{i}")
                    df.loc[(df["Mentor"] == mentor) &
                           (df["Resource"] == row["Resource"]) &
                           (df["Schedule"] == row["Schedule"]), "Status"] = status
                with col4:
                    comment = st.text_input("Comment", value=row.get("Comments", ""), key=f"comment_{mentor}_{i}")
                    df.loc[(df["Mentor"] == mentor) &
                           (df["Resource"] == row["Resource"]) &
                           (df["Schedule"] == row["Schedule"]), "Comments"] = comment

# === CHART ===
def show_progress(df):
    st.subheader("📊 Progress Overview")
    week_filter = st.selectbox("Filter by Week", ["All"] + sorted(df["Schedule"].dropna().unique()))
    mentor_filter = st.selectbox("Filter by Mentor", ["All"] + sorted(df["Mentor"].dropna().unique()))

    filtered = df.copy()
    if week_filter != "All":
        filtered = filtered[filtered["Schedule"] == week_filter]
    if mentor_filter != "All":
        filtered = filtered[filtered["Mentor"] == mentor_filter]

    if filtered.empty:
        st.warning("No data to display.")
        return

    chart_data = filtered.groupby(["Mentor", "Resource", "Status"]).size().reset_index(name="Count")
    fig = px.bar(chart_data, x="Resource", y="Count", color="Status", barmode="stack",
                 color_discrete_map={"Completed": COLOR_COMPLETED, "Not Completed": COLOR_SECONDARY})
    fig.update_layout(paper_bgcolor=COLOR_BG, plot_bgcolor=COLOR_BG, font=dict(color=TEXT_COLOR))
    st.plotly_chart(fig, use_container_width=True)

# === MAIN ===
def main():
    st.set_page_config(page_title="Anaplan Batch 2 Tracker", layout="wide")
    st.markdown(f"<div style='background-color:{COLOR_BG};padding:20px;border-radius:10px;'><h1 style='color:{COLOR_ACCENT};text-align:center;'>Anaplan Learning Batch 2 Tracker</h1></div>", unsafe_allow_html=True)

    if login():
        df, worksheet = load_data()

        update_status(df)
        show_progress(df)

        if st.button("💾 Save Changes to Google Sheet"):
            save_data(df, worksheet)
            df, worksheet = load_data()
            st.success("Data reloaded after update!")

if __name__ == "__main__":
    main()
