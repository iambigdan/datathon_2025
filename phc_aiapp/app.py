# app.py
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
from sqlalchemy import create_engine
from googletrans import Translator
from datetime import datetime

# ------------------------------
# DATABASE CONNECTION
# ------------------------------
host = "dfa-datafest.962626097808.eu-north-1.redshift-serverless.amazonaws.com"
port = 5439
dbname = "dev"
user = "admin"
password = "Newpassword0703"

@st.cache_data(ttl=3600)
def load_data():
    engine = create_engine(f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}")
    facilities = pd.read_sql("SELECT * FROM phc_facilities", engine)
    workers = pd.read_sql("SELECT * FROM health_workers", engine)
    patients = pd.read_sql("SELECT * FROM patients", engine)
    disease_reports = pd.read_sql("SELECT * FROM disease_reports", engine)
    inventory = pd.read_sql("SELECT * FROM inventory", engine)
    return facilities, workers, patients, disease_reports, inventory

facilities_df, workers_df, patients_df, disease_df, inventory_df = load_data()
translator = Translator()

# ------------------------------
# DASHBOARD SETUP
# ------------------------------
st.set_page_config(page_title="PHC AI Dashboard", layout="wide")
st.title("PHC AI Dashboard")

tabs = st.tabs(["Facilities", "Patients", "Health Workers", "Inventory", "Disease Reports", "Chatbot"])

# ------------------------------
# FACILITY FILTER WIDGET
# ------------------------------
selected_facility = st.selectbox(
    "Select Facility for All Views",
    ["All"] + list(facilities_df['facility_name'].unique())
)

def filter_by_facility(df, facility_col='facility_id'):
    if selected_facility != "All":
        fid = facilities_df[facilities_df['facility_name'] == selected_facility]['facility_id'].values[0]
        return df[df[facility_col] == fid]
    return df

# ------------------------------
# 1. FACILITIES TAB
# ------------------------------
with tabs[0]:
    st.header("Facilities Overview")
    filtered_facilities = facilities_df.copy()
    selected_state = st.selectbox("Filter by State", ["All"] + list(facilities_df['state'].unique()), key="state")
    if selected_state != "All":
        filtered_facilities = filtered_facilities[filtered_facilities['state'] == selected_state]

    fig = px.scatter_mapbox(
        filtered_facilities,
        lat="latitude",
        lon="longitude",
        color="operational_status",
        hover_name="facility_name",
        hover_data=["ownership", "type"],
        zoom=4,
        height=500
    )
    fig.update_layout(mapbox_style="open-street-map")
    st.plotly_chart(fig)
    st.dataframe(filtered_facilities)

    st.download_button(
        label="Download Facilities CSV",
        data=filtered_facilities.to_csv(index=False).encode('utf-8'),
        file_name='facilities.csv',
        mime='text/csv'
    )

# ------------------------------
# 2. PATIENTS TAB
# ------------------------------
with tabs[1]:
    st.header("Patient Statistics")
    patients_filtered = filter_by_facility(patients_df)
    patients_filtered['visit_date'] = pd.to_datetime(patients_filtered['visit_date'])
    
    # Patient visits over time
    st.subheader("Patient Visits Over Time")
    visits = patients_filtered.groupby('visit_date').size().reset_index(name='visits')
    if not visits.empty:
        m = Prophet()
        visits_prophet = visits.rename(columns={'visit_date':'ds','visits':'y'})
        m.fit(visits_prophet)
        future = m.make_future_dataframe(periods=30)
        forecast = m.predict(future)
        fig = px.line(forecast, x='ds', y='yhat', title='Predicted Patient Visits (Next 30 Days)')
        st.plotly_chart(fig)
    
    st.subheader("Age Distribution")
    if not patients_filtered.empty:
        fig2 = px.histogram(patients_filtered, x="age", nbins=20, color="gender")
        st.plotly_chart(fig2)

    st.download_button(
        label="Download Patients CSV",
        data=patients_filtered.to_csv(index=False).encode('utf-8'),
        file_name='patients.csv',
        mime='text/csv'
    )

# ------------------------------
# 3. HEALTH WORKERS TAB
# ------------------------------
with tabs[2]:
    st.header("Health Worker Overview")
    workers_filtered = filter_by_facility(workers_df)
    if not workers_filtered.empty:
        workers_count = workers_filtered.groupby(['role']).size().reset_index(name='count')
        fig = px.bar(workers_count, x='role', y='count', color='role', title="Staff Distribution")
        st.plotly_chart(fig)
        st.dataframe(workers_count)

    st.download_button(
        label="Download Health Workers CSV",
        data=workers_filtered.to_csv(index=False).encode('utf-8'),
        file_name='health_workers.csv',
        mime='text/csv'
    )

# ------------------------------
# 4. INVENTORY TAB
# ------------------------------
with tabs[3]:
    st.header("Inventory Monitoring")
    inventory_filtered = filter_by_facility(inventory_df)
    
    # Color-coded alerts
    def style_stock(row):
        if row['stock_level'] <= row['reorder_level']:
            return ['background-color: red']*len(row)
        elif row['stock_level'] <= row['reorder_level']*1.5:
            return ['background-color: yellow']*len(row)
        else:
            return ['background-color: green']*len(row)
    
    st.dataframe(inventory_filtered.style.apply(style_stock, axis=1))
    
    # Low stock alerts table
    low_stock = inventory_filtered[inventory_filtered['stock_level'] <= inventory_filtered['reorder_level']]
    if not low_stock.empty:
        st.subheader("Low Stock Alerts")
        st.dataframe(low_stock)
    else:
        st.write("All items are sufficiently stocked ✅")
    
    st.download_button(
        label="Download Inventory CSV",
        data=inventory_filtered.to_csv(index=False).encode('utf-8'),
        file_name='inventory.csv',
        mime='text/csv'
    )

# ------------------------------
# 5. DISEASE REPORTS TAB
# ------------------------------
with tabs[4]:
    st.header("Disease Reports")
    disease_filtered = filter_by_facility(disease_df)
    
    selected_disease = st.selectbox("Select Disease", ["All"] + list(disease_df['disease'].unique()))
    if selected_disease != "All":
        disease_filtered = disease_filtered[disease_filtered['disease'] == selected_disease]
    
    st.dataframe(disease_filtered)
    
    disease_trend = disease_filtered.groupby('month')['cases_reported'].sum().reset_index()
    if not disease_trend.empty:
        fig = px.line(disease_trend, x='month', y='cases_reported', title="Disease Trend")
        st.plotly_chart(fig)

    st.download_button(
        label="Download Disease Reports CSV",
        data=disease_filtered.to_csv(index=False).encode('utf-8'),
        file_name='disease_reports.csv',
        mime='text/csv'
    )

# ------------------------------
# 6. CHATBOT TAB
# ------------------------------
with tabs[5]:
    st.header("PHC Chatbot")
    user_input = st.text_input("Ask a question about PHC data:")
    selected_language = st.selectbox("Language", ["English", "Igbo", "Yoruba"])
    
    if user_input:
        # Translate input to English
        if selected_language != "English":
            user_input_en = translator.translate(user_input, src=selected_language.lower(), dest='en').text
        else:
            user_input_en = user_input.lower()
        
        response = "I couldn't find an answer. Try asking about patients, stock, or disease trends."
        
        # Facility detection
        facility_name = None
        for name in facilities_df['facility_name'].unique():
            if name.lower() in user_input_en:
                facility_name = name
                break
        if not facility_name and selected_facility != "All":
            facility_name = selected_facility

        # Stock query
        if "stock" in user_input_en:
            if facility_name:
                fid = facilities_df[facilities_df['facility_name'] == facility_name]['facility_id'].values[0]
                inv = inventory_df[inventory_df['facility_id']==fid]
                response = f"Stock levels for {facility_name}:\n" + "\n".join([f"{row['item_name']}: {row['stock_level']}" for idx,row in inv.iterrows()])
        
        # Patients query
        elif "patients" in user_input_en:
            if facility_name:
                fid = facilities_df[facilities_df['facility_name'] == facility_name]['facility_id'].values[0]
                count = patients_df[patients_df['facility_id']==fid].shape[0]
                response = f"Total patients at {facility_name}: {count}"
            else:
                response = f"Total patients overall: {patients_df.shape[0]}"
        
        # Disease query
        elif "disease" in user_input_en or "cases" in user_input_en:
            if facility_name:
                fid = facilities_df[facilities_df['facility_name'] == facility_name]['facility_id'].values[0]
                cases = disease_df[disease_df['facility_id']==fid]['cases_reported'].sum()
                response = f"Reported cases at {facility_name}: {cases}"
            else:
                cases = disease_df['cases_reported'].sum()
                response = f"Reported cases overall: {cases}"
        
        # Translate back if needed
        if selected_language != "English":
            response = translator.translate(response, src='en', dest=selected_language.lower()).text
        
        st.text_area("Chatbot Response", value=response, height=200)
