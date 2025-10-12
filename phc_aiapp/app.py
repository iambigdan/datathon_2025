# app.py

import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
import plotly.express as px
from prophet import Prophet
from googletrans import Translator

# -----------------------------
# Redshift Credentials (direct)
# -----------------------------
host = "dfa-datafest.962626097808.eu-north-1.redshift-serverless.amazonaws.com"
port = "5439"
dbname = "dev"
user = "admin"
password = "Newpassword0703"

# -----------------------------
# Connect to Redshift
# -----------------------------
@st.cache_data
def get_engine():
    url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}"
    return create_engine(url)

engine = get_engine()
def run_query(query):
    return pd.read_sql(query, engine)

# -----------------------------
# Load Data
# -----------------------------
@st.cache_data
def load_data():
    facilities = run_query("SELECT * FROM phc_facilities")
    workers = run_query("SELECT * FROM health_workers")
    patients = run_query("SELECT * FROM patients")
    disease_reports = run_query("SELECT * FROM disease_reports")
    inventory = run_query("SELECT * FROM inventory")
    return facilities, workers, patients, disease_reports, inventory

facilities, workers, patients, disease_reports, inventory = load_data()

# -----------------------------
# Streamlit Layout
# -----------------------------
st.set_page_config(layout="wide", page_title="PHC AI Dashboard")
st.title("PHC AI Dashboard - Hackathon Edition")

tabs = st.tabs([
    "Facilities", "Health Workers", "Patients", "Disease Reports",
    "Inventory", "Predictions", "Chatbot"
])

translator = Translator()

# -----------------------------
# Tab 1: Facilities
# -----------------------------
with tabs[0]:
    st.header("PHC Facilities Map & Summary")
    state_filter = st.multiselect("Filter by State:", facilities['state'].unique(), default=facilities['state'].unique())
    filtered_facilities = facilities[facilities['state'].isin(state_filter)]
    
    fig_map = px.scatter_mapbox(
        filtered_facilities, lat="latitude", lon="longitude",
        hover_name="facility_name", color="operational_status",
        zoom=5, mapbox_style="carto-positron"
    )
    st.plotly_chart(fig_map, use_container_width=True)
    
    st.subheader("Facility Counts by State")
    st.dataframe(filtered_facilities.groupby('state').size().reset_index(name='facility_count'))

# -----------------------------
# Tab 2: Health Workers
# -----------------------------
with tabs[1]:
    st.header("Health Workers Overview")
    role_filter = st.multiselect("Filter by Role:", workers['role'].unique(), default=workers['role'].unique())
    filtered_workers = workers[workers['role'].isin(role_filter)]
    
    role_summary = filtered_workers.groupby('role').size().reset_index(name='count')
    fig_workers = px.bar(role_summary, x='role', y='count', title="Staff by Role")
    st.plotly_chart(fig_workers)
    
    st.subheader("Available Staff by Facility")
    st.dataframe(filtered_workers[filtered_workers['availability_status']=='available'][['facility_id','name','role','specialization']])

# -----------------------------
# Tab 3: Patients
# -----------------------------
with tabs[2]:
    st.header("Patient Demographics & Visits")
    patients['age_group'] = pd.cut(patients['age'], bins=[0,12,18,35,50,65,100],
                                   labels=['0-12','13-18','19-35','36-50','51-65','66+'])
    
    age_group_summary = patients.groupby('age_group').size().reset_index(name='count')
    fig_age = px.bar(age_group_summary, x='age_group', y='count', title="Patient Count by Age Group")
    st.plotly_chart(fig_age)
    
    st.subheader("Patient Visits by Facility")
    visits_summary = patients.groupby('facility_id').size().reset_index(name='visits')
    st.dataframe(visits_summary)

# -----------------------------
# Tab 4: Disease Reports
# -----------------------------
with tabs[3]:
    st.header("Disease Trends & Alerts")
    disease_summary = disease_reports.groupby('disease')['cases_reported'].sum().reset_index()
    fig_disease = px.bar(disease_summary, x='disease', y='cases_reported', color='cases_reported',
                         title="Total Cases by Disease", color_continuous_scale='Reds')
    st.plotly_chart(fig_disease)
    
    st.subheader("Recent Disease Reports")
    st.dataframe(disease_reports.sort_values('month', ascending=False))

# -----------------------------
# Tab 5: Inventory
# -----------------------------
with tabs[4]:
    st.header("Inventory Overview")
    st.dataframe(inventory)
    
    st.subheader("Low Stock Alerts")
    low_stock = inventory[inventory['stock_level'] < inventory['reorder_level']]
    st.dataframe(low_stock.style.applymap(lambda x: 'background-color : red' if isinstance(x,int) and x<5 else ''))

# -----------------------------
# Tab 6: Predictions
# -----------------------------
with tabs[5]:
    st.header("Predictive Analytics")
    
    # Patient Visits Forecast
    st.subheader("Patient Visits Forecast")
    facility_options = patients['facility_id'].unique()
    facility_select = st.selectbox("Select Facility:", facility_options)
    df_fac = patients[patients['facility_id']==facility_select].groupby('visit_date').size().reset_index(name='visits')
    df_fac.rename(columns={'visit_date':'ds','visits':'y'}, inplace=True)
    
    if not df_fac.empty:
        model = Prophet()
        model.fit(df_fac)
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)
        fig_pred = px.line(forecast, x='ds', y='yhat', title=f"Patient Visit Forecast - Facility {facility_select}")
        st.plotly_chart(fig_pred)
    
    # Disease Trend Prediction
    st.subheader("Disease Outbreak Trend")
    disease_future = disease_reports.groupby(['month','disease'])['cases_reported'].sum().reset_index()
    st.line_chart(disease_future.pivot(index='month', columns='disease', values='cases_reported').fillna(0))

# -----------------------------
# Tab 7: Multilingual Chatbot
# -----------------------------
with tabs[6]:
    st.header("Multilingual Chatbot (English, Igbo, Yoruba)")
    user_input = st.text_input("Ask a question:")

    if user_input:
        lang_detected = translator.detect(user_input).lang
        input_en = translator.translate(user_input, src=lang_detected, dest='en').text

        def chatbot_query(user_input):
            user_input = user_input.lower()
            if "low stock" in user_input:
                state = user_input.split("in")[-1].strip()
                query = f"""
                SELECT facility_name, item_name, stock_level
                FROM inventory
                JOIN phc_facilities USING(facility_id)
                WHERE state = '{state}' AND stock_level < reorder_level
                """
                return run_query(query)
            elif "patient" in user_input:
                if "forecast" in user_input:
                    return "Check the Predictions tab for patient forecasts."
                else:
                    query = """
                    SELECT facility_name, COUNT(*) as patient_count
                    FROM patients
                    JOIN phc_facilities USING(facility_id)
                    WHERE visit_date >= DATE_TRUNC('month', CURRENT_DATE - INTERVAL '1 month')
                    GROUP BY facility_name
                    """
                    return run_query(query)
            elif "disease" in user_input:
                disease = user_input.split("of")[-1].strip()
                query = f"""
                SELECT facility_name, SUM(cases_reported) as cases
                FROM disease_reports
                JOIN phc_facilities USING(facility_id)
                WHERE disease = '{disease}'
                GROUP BY facility_name
                """
                return run_query(query)
            elif "staff" in user_input or "worker" in user_input:
                role = user_input.split("available")[-1].strip()
                query = f"""
                SELECT facility_name, name, role
                FROM health_workers
                JOIN phc_facilities USING(facility_id)
                WHERE availability_status='available' AND role ILIKE '%{role}%'
                """
                return run_query(query)
            else:
                return "Sorry, I didn't understand. Ask about low stock, patients, disease, or staff."

        result = chatbot_query(input_en)

        if lang_detected != 'en':
            if isinstance(result, pd.DataFrame):
                result_display = result.applymap(lambda x: translator.translate(str(x), src='en', dest=lang_detected).text)
                st.dataframe(result_display)
            else:
                st.write(translator.translate(result, src='en', dest=lang_detected).text)
        else:
            st.dataframe(result) if isinstance(result, pd.DataFrame) else st.write(result)
