#app.py

import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from prophet import Prophet
from deep_translator import GoogleTranslator
import re

# -----------------------------
# DATABASE CONNECTION
# -----------------------------
REDSHIFT_HOST = "dfa-datafest.962626097808.eu-north-1.redshift-serverless.amazonaws.com"
REDSHIFT_PORT = "5439"
REDSHIFT_DB = "dev"
REDSHIFT_USER = "admin"
REDSHIFT_PASSWORD = "Newpassword0703"

@st.cache_data
def load_data():
    engine = create_engine(
        f"postgresql+psycopg2://{REDSHIFT_USER}:{REDSHIFT_PASSWORD}@{REDSHIFT_HOST}:{REDSHIFT_PORT}/{REDSHIFT_DB}"
    )

    facilities = pd.read_sql("SELECT * FROM phc_facilities", engine)
    workers = pd.read_sql("SELECT * FROM health_workers", engine)
    patients = pd.read_sql("SELECT * FROM patients", engine)
    diseases = pd.read_sql("SELECT * FROM disease_reports", engine)
    inventory = pd.read_sql("SELECT * FROM inventory", engine)
    return facilities, workers, patients, diseases, inventory

facilities_df, workers_df, patients_df, diseases_df, inventory_df = load_data()

# -----------------------------
# STREAMLIT APP UI
# -----------------------------
st.set_page_config(page_title="PHC AI Dashboard", layout="wide")

st.title("🏥 PHC AI Dashboard")
st.markdown("A unified AI-powered dashboard for monitoring Primary Health Care (PHC) facilities in Nigeria.")

tabs = st.tabs(["Facilities", "Health Workers", "Patients", "Disease Reports", "Inventory", "Chatbot"])

# -----------------------------
# FACILITY FILTER
# -----------------------------
with st.sidebar:
    selected_facility = st.selectbox("Select a Facility", facilities_df['facility_name'].unique())
    facility_id = facilities_df.loc[facilities_df['facility_name'] == selected_facility, 'facility_id'].values[0]
    st.write(f"**Facility ID:** {facility_id}")

# -----------------------------
# TAB 1: FACILITIES
# -----------------------------
with tabs[0]:
    st.header("Facility Overview")
    fig = px.scatter_mapbox(
        facilities_df,
        lat="latitude",
        lon="longitude",
        hover_name="facility_name",
        color="operational_status",
        zoom=5,
        height=500,
        title="PHC Facilities Map"
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(facilities_df)

# -----------------------------
# TAB 2: HEALTH WORKERS
# -----------------------------
with tabs[1]:
    st.header("Health Worker Distribution")
    facility_workers = workers_df[workers_df['facility_id'] == facility_id]
    st.metric("Total Workers", len(facility_workers))
    st.bar_chart(facility_workers['role'].value_counts())
    st.dataframe(facility_workers)

# -----------------------------
# TAB 3: PATIENTS
# -----------------------------
with tabs[2]:
    st.header("Patient Visits and Outcomes")
    facility_patients = patients_df[patients_df['facility_id'] == facility_id]
    st.metric("Total Patients", len(facility_patients))
    outcome_counts = facility_patients['outcome'].value_counts()
    st.bar_chart(outcome_counts)

    # Predict future visits
    st.subheader("📈 Predictive Patient Forecast")
    if len(facility_patients) > 5:
        df_forecast = facility_patients.groupby('visit_date').size().reset_index(name='y')
        df_forecast.rename(columns={'visit_date': 'ds'}, inplace=True)
        model = Prophet()
        model.fit(df_forecast)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        fig2 = px.line(forecast, x='ds', y='yhat', title='Predicted Patient Visits (Next 30 Days)')
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Not enough patient data to generate a forecast.")

# -----------------------------
# TAB 4: DISEASE REPORTS
# -----------------------------
with tabs[3]:
    st.header("Disease Trends")
    facility_diseases = diseases_df[diseases_df['facility_id'] == facility_id]
    st.dataframe(facility_diseases)
    fig3 = px.bar(facility_diseases, x='disease', y='cases_reported', color='month', title="Disease Cases by Month")
    st.plotly_chart(fig3, use_container_width=True)

# -----------------------------
# TAB 5: INVENTORY
# -----------------------------
with tabs[4]:
    st.header("Inventory Status")
    facility_inventory = inventory_df[inventory_df['facility_id'] == facility_id]
    st.dataframe(facility_inventory)

    low_stock = facility_inventory[facility_inventory['stock_level'] < facility_inventory['reorder_level']]
    if not low_stock.empty:
        st.warning("⚠️ Low Stock Items Detected!")
        st.dataframe(low_stock)
    else:
        st.success("✅ All inventory items are well stocked.")

# -----------------------------
# TAB 6: CHATBOT
# -----------------------------
with tabs[5]:
    st.header("💬 AI Chatbot Assistant")

    def translate_text(text, target_lang):
        try:
            return GoogleTranslator(source='auto', target=target_lang).translate(text)
        except Exception:
            return text

    user_input = st.text_input("Ask me anything about this PHC facility...")

    if user_input:
        query = user_input.lower()

        if "stock" in query or "inventory" in query:
            response_df = inventory_df[inventory_df['facility_id'] == facility_id][['item_name', 'stock_level']]
            response = f"Here’s the current stock for {selected_facility}: \n\n{response_df.to_string(index=False)}"
        elif "worker" in query:
            total_workers = len(workers_df[workers_df['facility_id'] == facility_id])
            response = f"{selected_facility} has {total_workers} active health workers."
        elif "patient" in query:
            total_patients = len(patients_df[patients_df['facility_id'] == facility_id])
            response = f"There are {total_patients} patient visits recorded at {selected_facility}."
        elif "disease" in query:
            common_disease = diseases_df[diseases_df['facility_id'] == facility_id]['disease'].mode()[0]
            response = f"The most commonly reported disease at {selected_facility} is {common_disease}."
        else:
            response = "I can tell you about stock, workers, patients, or diseases. Try asking something like 'Show stock for this facility'."

        st.markdown("**English:** " + response)
        st.markdown("**Yoruba:** " + translate_text(response, 'yo'))
        st.markdown("**Igbo:** " + translate_text(response, 'ig'))

# -----------------------------
# END OF APP
# -----------------------------
