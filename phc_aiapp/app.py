import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
from deep_translator import GoogleTranslator
import redshift_connector
from datetime import timedelta

# -------------------------------------------------
# Database Connection (Amazon Redshift Serverless)
# -------------------------------------------------
REDSHIFT_HOST = "dfa-datafest.962626097808.eu-north-1.redshift-serverless.amazonaws.com"
REDSHIFT_PORT = 5439
REDSHIFT_DB = "dev"
REDSHIFT_USER = "admin"
REDSHIFT_PASSWORD = "Newpassword0703"

TABLE_FACILITIES = "staging_Nigeria_phc"
TABLE_WORKERS = "staging_health_workers"
TABLE_PATIENTS = "staging_patients_dataset"
TABLE_DISEASES = "staging_disease_report"
TABLE_INVENTORY = "staging_inventory_dataset"

# -------------------------------------------------
# Translation (Deep Translator)
# -------------------------------------------------
LANG_MAP = {"English": "en", "Igbo": "ig", "Yoruba": "yo", "Hausa": "ha"}

def translate_text(text, lang):
    if lang == "English":
        return text
    try:
        return GoogleTranslator(source="auto", target=LANG_MAP.get(lang, "en")).translate(text)
    except Exception:
        return text

# -------------------------------------------------
# Connect and Load Data from Redshift
# -------------------------------------------------
@st.cache_data(ttl=3600)
def load_all_tables():
    conn = redshift_connector.connect(
        host=REDSHIFT_HOST,
        port=REDSHIFT_PORT,
        database=REDSHIFT_DB,
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD
    )
    cursor = conn.cursor()

    def read_table(table_name):
        query = f"SELECT * FROM {table_name};"
        cursor.execute(query)
        columns = [desc[0] for desc in cursor.description]
        data = cursor.fetchall()
        return pd.DataFrame(data, columns=columns)

    facilities = read_table(TABLE_FACILITIES)
    workers = read_table(TABLE_WORKERS)
    patients = read_table(TABLE_PATIENTS)
    diseases = read_table(TABLE_DISEASES)
    inventory = read_table(TABLE_INVENTORY)

    cursor.close()
    conn.close()

    # Normalize columns
    for df in (facilities, workers, patients, diseases, inventory):
        df.columns = [c.lower() for c in df.columns]

    # Parse dates
    if "visit_date" in patients.columns:
        patients["visit_date"] = pd.to_datetime(patients["visit_date"], errors="coerce")
    if "month" in diseases.columns:
        diseases["month_dt"] = pd.to_datetime(diseases["month"], errors="coerce")
    if "last_restock_date" in inventory.columns:
        inventory["last_restock_date"] = pd.to_datetime(inventory["last_restock_date"], errors="coerce")

    return facilities, workers, patients, diseases, inventory

facilities_df, workers_df, patients_df, diseases_df, inventory_df = load_all_tables()

# -------------------------------------------------
# Streamlit UI
# -------------------------------------------------
st.set_page_config(page_title="PHC AI Dashboard", layout="wide")

st.title("🏥 PHC AI Data Dashboard (Redshift Serverless)")

tabs = st.tabs(["📊 Facility Dashboard", "🤖 AI Chatbot", "📈 Forecasting"])

# -------------------------------------------------
# Facility Dashboard
# -------------------------------------------------
with tabs[0]:
    st.header("Facility Overview")

    facility_name = st.selectbox("Select a PHC facility", facilities_df["facility_name"].unique())
    selected_facility = facilities_df[facilities_df["facility_name"] == facility_name]
    facility_id = selected_facility["facility_id"].values[0]

    st.subheader(f"📍 {facility_name}")

    # Workers per facility
    workers_in_facility = workers_df[workers_df["facility_id"] == facility_id]
    st.metric("👩‍⚕️ Number of Health Workers", len(workers_in_facility))

    # Inventory status
    inventory_in_facility = inventory_df[inventory_df["facility_id"] == facility_id]
    st.dataframe(inventory_in_facility[["item_name", "stock_level", "reorder_level"]])

    # Patient visits chart
    facility_patients = patients_df[patients_df["facility_id"] == facility_id]
    if not facility_patients.empty:
        visits = facility_patients.groupby("visit_date").size().reset_index(name="visits")
        st.plotly_chart(px.line(visits, x="visit_date", y="visits", title="📅 Patient Visits Over Time"))

# -------------------------------------------------
# Chatbot
# -------------------------------------------------
with tabs[1]:
    st.header("🤖 PHC Chatbot Assistant")
    lang = st.selectbox("Select Language", list(LANG_MAP.keys()), index=0)
    query = st.text_input("Ask a question (e.g. 'What’s the stock level for Paracetamol in Oyo PHC?')")

    if st.button("Ask"):
        query_lower = query.lower()

        response = "I’m not sure how to answer that yet."

        # Detect stock queries
        if "stock" in query_lower:
            for name in facilities_df["facility_name"]:
                if name.lower() in query_lower:
                    f_id = facilities_df[facilities_df["facility_name"] == name]["facility_id"].values[0]
                    items = inventory_df[inventory_df["facility_id"] == f_id]
                    if "paracetamol" in query_lower:
                        items = items[items["item_name"].str.contains("paracetamol", case=False)]
                    if not items.empty:
                        response = "Here’s the stock status:\n" + items[["item_name", "stock_level", "reorder_level"]].to_string(index=False)
                    break

        st.markdown("### 💬 Response:")
        st.write(translate_text(response, lang))

# -------------------------------------------------
# Forecasting Tab
# -------------------------------------------------
with tabs[2]:
    st.header("📈 Disease Case Forecasting")

    disease = st.selectbox("Select Disease", diseases_df["disease"].unique())
    data = diseases_df[diseases_df["disease"] == disease].groupby("month_dt")["cases_reported"].sum().reset_index()

    if len(data) > 2:
        data.columns = ["ds", "y"]
        model = Prophet()
        model.fit(data)
        future = model.make_future_dataframe(periods=6, freq="M")
        forecast = model.predict(future)
        st.plotly_chart(px.line(forecast, x="ds", y="yhat", title=f"Forecast for {disease} Cases"))
    else:
        st.warning("Not enough data to forecast for this disease.")
