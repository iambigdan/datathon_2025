import streamlit as st
import pandas as pd
import plotly.express as px
import psycopg2
from deep_translator import GoogleTranslator

# ==============================
# DATABASE CONNECTION
# ==============================
def get_connection():
    return psycopg2.connect(
        host="dfa-datafest.962626097808.eu-north-1.redshift-serverless.amazonaws.com",
        port="5439",
        dbname="dev",
        user="admin",
        password="Newpassword0703"
    )

# ==============================
# LOAD DATA
# ==============================
@st.cache_data
def load_data():
    conn = get_connection()

    nigeria_phc = pd.read_sql("SELECT * FROM staging_Nigeria_phc", conn)
    health_workers = pd.read_sql("SELECT * FROM staging_health_workers", conn)
    patients_dataset = pd.read_sql("SELECT * FROM staging_patients_dataset", conn)
    disease_reports = pd.read_sql("SELECT * FROM staging_disease_report", conn)
    inventory_dataset = pd.read_sql("SELECT * FROM staging_inventory_dataset", conn)

    conn.close()
    return nigeria_phc, health_workers, patients_dataset, disease_reports, inventory_dataset

nigeria_phc, health_workers, patients_dataset, disease_reports, inventory_dataset = load_data()

# ==============================
# STREAMLIT APP CONFIG
# ==============================
st.set_page_config(page_title="PHC Data Intelligence Dashboard", layout="wide")
st.title("🩺 Primary Health Care (PHC) Data Intelligence System")
st.markdown("**Empowering public health through AI-driven data insights.**")

tabs = st.tabs(["🏥 Facilities", "👩‍⚕️ Health Workers", "🧍 Patients", "🦠 Diseases", "💊 Inventory", "🤖 Chatbot"])

# ------------------------------
# 1. FACILITY DASHBOARD
# ------------------------------
with tabs[0]:
    st.header("Facility Overview")

    selected_state = st.selectbox("Select a State", nigeria_phc["state"].unique())
    filtered_facilities = nigeria_phc[nigeria_phc["state"] == selected_state]

    st.dataframe(filtered_facilities)

    fig = px.scatter_mapbox(
        filtered_facilities,
        lat="latitude",
        lon="longitude",
        hover_name="facility_name",
        color="operational_status",
        mapbox_style="open-street-map",
        zoom=5,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# 2. HEALTH WORKERS DASHBOARD
# ------------------------------
with tabs[1]:
    st.header("Health Worker Distribution")

    facility_choice = st.selectbox("Select Facility", nigeria_phc["facility_name"].unique())
    facility_id = nigeria_phc.loc[nigeria_phc["facility_name"] == facility_choice, "facility_id"].values[0]

    filtered_workers = health_workers[health_workers["facility_id"] == facility_id]
    st.dataframe(filtered_workers)

    if not filtered_workers.empty:
        role_count = filtered_workers["role"].value_counts().reset_index()
        fig = px.bar(role_count, x="index", y="role", title=f"Role Distribution at {facility_choice}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No health workers data available for this facility.")

# ------------------------------
# 3. PATIENTS DASHBOARD
# ------------------------------
with tabs[2]:
    st.header("Patient Visits")

    facility_choice2 = st.selectbox("Select Facility for Patients", nigeria_phc["facility_name"].unique())
    facility_id2 = nigeria_phc.loc[nigeria_phc["facility_name"] == facility_choice2, "facility_id"].values[0]

    patient_data = patients_dataset[patients_dataset["facility_id"] == facility_id2]

    if not patient_data.empty:
        patient_count = patient_data.groupby("diagnosis").size().reset_index(name="count")
        fig = px.bar(patient_count, x="diagnosis", y="count", title=f"Patient Diagnosis Count - {facility_choice2}")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No patient data available for this facility.")

# ------------------------------
# 4. DISEASE REPORTS
# ------------------------------
with tabs[3]:
    st.header("Disease Reports")

    disease_summary = disease_reports.groupby("disease")[["cases_reported", "deaths"]].sum().reset_index()
    fig = px.bar(
        disease_summary,
        x="disease",
        y=["cases_reported", "deaths"],
        barmode="group",
        title="Disease Cases and Deaths"
    )
    st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# 5. INVENTORY DASHBOARD
# ------------------------------
with tabs[4]:
    st.header("Inventory Levels")

    facility_choice3 = st.selectbox("Select Facility for Inventory", nigeria_phc["facility_name"].unique())
    facility_id3 = nigeria_phc.loc[nigeria_phc["facility_name"] == facility_choice3, "facility_id"].values[0]

    facility_inventory = inventory_dataset[inventory_dataset["facility_id"] == facility_id3]

    st.dataframe(facility_inventory)

    if not facility_inventory.empty:
        fig = px.bar(
            facility_inventory,
            x="item_name",
            y="stock_level",
            color="stock_level",
            title=f"Stock Levels at {facility_choice3}"
        )
        st.plotly_chart(fig, use_container_width=True)

# ------------------------------
# 6. CHATBOT (Facility-Aware)
# ------------------------------
with tabs[5]:
    st.header("AI Chat Assistant")

    facility_chat = st.selectbox("Select Facility for Chat", nigeria_phc["facility_name"].unique())
    facility_id_chat = nigeria_phc.loc[nigeria_phc["facility_name"] == facility_chat, "facility_id"].values[0]

    user_input = st.text_input("Ask me anything about this facility:", placeholder="e.g. What is the stock level for paracetamol?")

    if user_input:
        # Simple rule-based chatbot
        response = ""

        if "stock" in user_input.lower():
            result = inventory_dataset[inventory_dataset["facility_id"] == facility_id_chat]
            if not result.empty:
                response = f"Here’s the inventory summary for {facility_chat}:"
                st.dataframe(result[["item_name", "stock_level", "reorder_level"]])
            else:
                response = "No inventory data available for this facility."

        elif "worker" in user_input.lower() or "staff" in user_input.lower():
            result = health_workers[health_workers["facility_id"] == facility_id_chat]
            if not result.empty:
                response = f"There are {len(result)} health workers at {facility_chat}."
            else:
                response = "No health worker data available for this facility."

        elif "disease" in user_input.lower() or "cases" in user_input.lower():
            result = disease_reports[disease_reports["facility_id"] == facility_id_chat]
            if not result.empty:
                response = f"Disease report for {facility_chat}:"
                st.dataframe(result[["disease", "cases_reported", "deaths"]])
            else:
                response = "No disease report available for this facility."

        else:
            response = GoogleTranslator(source='auto', target='en').translate("Sorry, I didn’t understand that question.")

        st.success(response)
