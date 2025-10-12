import streamlit as st
import pandas as pd
import plotly.express as px
from prophet import Prophet
from deep_translator import GoogleTranslator
import redshift_connector

# -----------------------------
# Database Connection
# -----------------------------
REDSHIFT_HOST = "dfa-datafest.962626097808.eu-north-1.redshift-serverless.amazonaws.com"
REDSHIFT_PORT = 5439
REDSHIFT_DB = "datafest"
REDSHIFT_USER = "admin"
REDSHIFT_PASSWORD = "Newpassword0703"

TABLE_FACILITIES = "staging.staging_nigeria_phc"
TABLE_WORKERS = "staging.staging_health_workers"
TABLE_PATIENTS = "staging.staging_patients_dataset"
TABLE_DISEASES = "staging.staging_disease_report"
TABLE_INVENTORY = "staging.staging_inventory_dataset"

# -----------------------------
# Translation
# -----------------------------
LANG_MAP = {"English": "en", "Igbo": "ig", "Yoruba": "yo", "Hausa": "ha"}

def translate_text(text, lang):
    if lang == "English":
        return text
    try:
        return GoogleTranslator(source="auto", target=LANG_MAP.get(lang, "en")).translate(text)
    except Exception:
        return text

# -----------------------------
# Load Data with Caching
# -----------------------------
@st.cache_data(ttl=3600)
def load_table(table_name, columns, limit=1000):
    conn = redshift_connector.connect(
        host=REDSHIFT_HOST,
        port=REDSHIFT_PORT,
        database=REDSHIFT_DB,
        user=REDSHIFT_USER,
        password=REDSHIFT_PASSWORD
    )
    cursor = conn.cursor()
    query = f"SELECT {columns} FROM {table_name} LIMIT {limit};"
    cursor.execute(query)
    col_names = [desc[0] for desc in cursor.description]
    data = cursor.fetchall()
    cursor.close()
    conn.close()
    df = pd.DataFrame(data, columns=[c.lower() for c in col_names])
    return df

# -----------------------------
# Load All Tables
# -----------------------------
facilities_df = load_table(TABLE_FACILITIES,
                           "facility_id, facility_name, state, lga, ownership, type, latitude, longitude, operational_status, number_of_beds, average_daily_patients, health_workers")

workers_df = load_table(TABLE_WORKERS,
                        "worker_id, facility_id, name, role, qualification, years_experience, gender, specialization, shift, availability_status")

patients_df = load_table(TABLE_PATIENTS,
                         "patient_id, facility_id, gender, age, visit_date, diagnosis, treatment, outcome")
patients_df["visit_date"] = pd.to_datetime(patients_df["visit_date"], errors="coerce")

diseases_df = load_table(TABLE_DISEASES,
                         "report_id, facility_id, month, disease, cases_reported, deaths")
diseases_df["month_dt"] = pd.to_datetime(diseases_df["month"], errors="coerce")

inventory_df = load_table(TABLE_INVENTORY,
                          "item_id, facility_id, item_name, stock_level, reorder_level, last_restock_date")
inventory_df["last_restock_date"] = pd.to_datetime(inventory_df["last_restock_date"], errors="coerce")

# -----------------------------
# Streamlit Sidebar & Tabs
# -----------------------------
st.set_page_config(page_title="PHC AI Dashboard", layout="wide")

st.sidebar.title("🏥 PHC Dashboard")
tab_selection = st.sidebar.radio("Navigation", [
    "Facility Dashboard", "PHC Chatbot", "Disease Forecasting", "Inventory Overview", "Operational Status"
])

# -----------------------------
# 1. Facility Dashboard
# -----------------------------
if tab_selection == "Facility Dashboard":
    st.header("Facility Overview")
    facility_name = st.selectbox("Select a PHC facility", facilities_df["facility_name"].unique())
    facility = facilities_df[facilities_df["facility_name"] == facility_name]
    facility_id = facility["facility_id"].values[0]

    st.subheader(f"📍 {facility_name}")
    # Metrics
    st.metric("👩‍⚕️ Number of Health Workers",
              len(workers_df[workers_df["facility_id"] == facility_id]))
    st.metric("🏥 Number of Beds",
              int(facility["number_of_beds"].values[0]))
    st.metric("👨‍👩‍👧‍👦 Average Daily Patients",
              int(facility["average_daily_patients"].values[0]))

    # Patient visits chart
    visits_df = patients_df[patients_df["facility_id"] == facility_id]
    if not visits_df.empty:
        visits_chart = visits_df.groupby("visit_date").size().reset_index(name="visits")
        st.plotly_chart(px.line(visits_chart, x="visit_date", y="visits",
                                title="📅 Patient Visits Over Time"))

# -----------------------------
# 2. PHC Chatbot
# -----------------------------
elif tab_selection == "PHC Chatbot":
    st.header("🤖 PHC Chatbot Assistant")

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    selected_facility_name = st.selectbox("Select Facility", facilities_df["facility_name"].unique())
    selected_facility_id = facilities_df[facilities_df["facility_name"] == selected_facility_name]["facility_id"].values[0]

    items_list = inventory_df[inventory_df["facility_id"] == selected_facility_id]["item_name"].unique()
    selected_item = st.selectbox("Select Item (optional)", ["Any"] + list(items_list))

    lang = st.selectbox("Select Language", list(LANG_MAP.keys()), index=0)
    user_query = st.text_input("Type your question here...")

    if st.button("Send") and user_query:
        query_lower = user_query.lower()
        response = "I’m not sure how to answer that yet."

        # Stock query handling
        if "stock" in query_lower or "inventory" in query_lower:
            items = inventory_df[inventory_df["facility_id"] == selected_facility_id]
            if selected_item != "Any":
                items = items[items["item_name"].str.contains(selected_item, case=False)]
            if not items.empty:
                low_stock_items = items[items["stock_level"].astype(int) <= items["reorder_level"].astype(int)]
                response = "Here’s the stock status:\n" + items[["item_name", "stock_level", "reorder_level"]].to_string(index=False)
                if not low_stock_items.empty:
                    response += "\n\n⚠️ Low stock alert for:\n" + low_stock_items["item_name"].to_string(index=False)

        st.session_state.chat_history.append(("You", user_query))
        st.session_state.chat_history.append(("Bot", translate_text(response, lang)))

    # Display chat history with colors
    for speaker, message in st.session_state.get("chat_history", []):
        if speaker == "You":
            st.markdown(f"<div style='text-align:right; background-color:#D6EAF8; color:#1B4F72; padding:10px; border-radius:10px; margin:4px 0'>{message}</div>", unsafe_allow_html=True)
        else:
            message = message.replace("⚠️ Low stock alert", "<span style='color:red; font-weight:bold'>⚠️ Low stock alert</span>")
            st.markdown(f"<div style='text-align:left; background-color:#FADBD8; color:#641E16; padding:10px; border-radius:10px; margin:4px 0'>{message}</div>", unsafe_allow_html=True)

# -----------------------------
# 3. Disease Forecasting
# -----------------------------
elif tab_selection == "Disease Forecasting":
    st.header("📈 Disease Case Forecasting")
    disease = st.selectbox("Select Disease", diseases_df["disease"].unique())
    df = diseases_df[diseases_df["disease"] == disease].groupby("month_dt")["cases_reported"].sum().reset_index()
    if len(df) > 2:
        df.columns = ["ds", "y"]
        model = Prophet()
        model.fit(df)
        future = model.make_future_dataframe(periods=6, freq="M")
        forecast = model.predict(future)
        st.plotly_chart(px.line(forecast, x="ds", y="yhat", title=f"Forecast for {disease} Cases"))
    else:
        st.warning("Not enough data to forecast for this disease.")

# -----------------------------
# 4. Inventory Overview
# -----------------------------
elif tab_selection == "Inventory Overview":
    st.header("📦 Inventory Overview")
    facility_select = st.selectbox("Select Facility", facilities_df["facility_name"].unique())
    f_id = facilities_df[facilities_df["facility_name"] == facility_select]["facility_id"].values[0]
    inv_df = inventory_df[inventory_df["facility_id"] == f_id].copy()
    if not inv_df.empty:
        inv_df["low_stock"] = inv_df["stock_level"].astype(int) <= inv_df["reorder_level"].astype(int)
        st.dataframe(inv_df.style.applymap(lambda v: 'color:red;' if isinstance(v,bool) and v else '', subset=["low_stock"]))

# -----------------------------
# 5. Facility Operational Status
# -----------------------------
elif tab_selection == "Operational Status":
    st.header("🏥 Facility Operational Status")
    status_df = facilities_df[["facility_name", "state", "lga", "operational_status"]].copy()
    status_df["status_color"] = status_df["operational_status"].apply(lambda x: 'green' if x.lower() == "operational" else 'red')
    st
