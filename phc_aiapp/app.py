# app.py - PHC AI Dashboard (final)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from prophet import Prophet
from sqlalchemy import create_engine
from deep_translator import GoogleTranslator
from datetime import timedelta

# -----------------------------
# Connection configuration (explicit)
# -----------------------------
REDSHIFT_HOST = "dfa-datafest.962626097808.eu-north-1.redshift-serverless.amazonaws.com"
REDSHIFT_PORT = "5439"
REDSHIFT_DB = "dev"
REDSHIFT_USER = "admin"
REDSHIFT_PASSWORD = "Newpassword0703"   # <-- your password

# staging table names (as you provided)
TABLE_FACILITIES = "staging_Nigeria_phc"
TABLE_WORKERS = "staging_health_workers"
TABLE_PATIENTS = "staging_patients_dataset"
TABLE_DISEASES = "staging_disease_report"
TABLE_INVENTORY = "staging_inventory_dataset"

# -----------------------------
# Utility: translator wrapper
# -----------------------------
LANG_MAP = {"English": "en", "Igbo": "ig", "Yoruba": "yo", "Hausa": "ha"}

def translate_text(text: str, target_lang: str) -> str:
    """Translate text to target_lang (ISO) using deep-translator (GoogleTranslator backend)."""
    if not text or target_lang == "en":
        return text
    try:
        return GoogleTranslator(source="auto", target=target_lang).translate(text)
    except Exception:
        return text

# -----------------------------
# Load data from Redshift
# -----------------------------
@st.cache_data(ttl=3600)
def load_all_tables():
    """Load staging tables from Redshift into pandas DataFrames."""
    from sqlalchemy import create_engine

    engine = create_engine(
        f"postgresql+psycopg2://{REDSHIFT_USER}:{REDSHIFT_PASSWORD}@{REDSHIFT_HOST}:{REDSHIFT_PORT}/{REDSHIFT_DB}",
        connect_args={"sslmode": "prefer"},
        execution_options={"isolation_level": "AUTOCOMMIT"}
    )

    facilities = pd.read_sql(f"SELECT * FROM {TABLE_FACILITIES}", engine)
    workers = pd.read_sql(f"SELECT * FROM {TABLE_WORKERS}", engine)
    patients = pd.read_sql(f"SELECT * FROM {TABLE_PATIENTS}", engine)
    diseases = pd.read_sql(f"SELECT * FROM {TABLE_DISEASES}", engine)
    inventory = pd.read_sql(f"SELECT * FROM {TABLE_INVENTORY}", engine)

    # normalize columns
    for df in (facilities, workers, patients, diseases, inventory):
        df.columns = [c.lower() for c in df.columns]

    # parse dates
    if "visit_date" in patients.columns:
        patients["visit_date"] = pd.to_datetime(patients["visit_date"], errors="coerce")
    if "month" in diseases.columns:
        diseases["month_dt"] = pd.to_datetime(diseases["month"], errors="coerce")
    if "last_restock_date" in inventory.columns:
        inventory["last_restock_date"] = pd.to_datetime(inventory["last_restock_date"], errors="coerce")

    return facilities, workers, patients, diseases, inventory

facilities_df, workers_df, patients_df, diseases_df, inventory_df = load_all_tables()

# -----------------------------
# Streamlit UI setup
# -----------------------------
st.set_page_config(page_title="PHC AI Dashboard", layout="wide")
st.title("PHC AI Dashboard — Facility-level AI Insights")
st.markdown("Interactive dashboard with forecasting and a multilingual chatbot (English, Igbo, Yoruba, Hausa).")

# Global sidebar filters
with st.sidebar:
    st.header("Context & Filters")
    facility_options = ["All"] + list(facilities_df["facility_name"].fillna("Unnamed").unique())
    selected_facility = st.selectbox("Select facility (applies across tabs)", facility_options, index=0)
    state_options = ["All"] + list(facilities_df["state"].dropna().unique())
    selected_state = st.selectbox("Filter facilities by state (map/tab)", state_options, index=0)
    show_low_stock_only = st.checkbox("Inventory: show only low-stock", value=False)
    st.markdown("---")
    st.markdown("Languages for chatbot replies:")
    chat_lang = st.selectbox("Chatbot language", ["English", "Igbo", "Yoruba", "Hausa"], index=0)
    st.markdown("---")
    st.caption("Tip: select a facility to make chatbot answers facility-specific (no need to type the name).")

# helper: facility id resolution
def facility_id_from_name(name):
    if name is None or name == "All":
        return None
    row = facilities_df[facilities_df["facility_name"].str.lower() == str(name).lower()]
    if row.empty:
        return None
    return row.iloc[0]["facility_id"]

active_facility_id = facility_id_from_name(selected_facility)

# Layout tabs
tabs = st.tabs(["Facilities", "Health Workers", "Patients", "Inventory", "Disease Reports", "Chatbot"])

# -----------------------------
# TAB: Facilities (map + table)
# -----------------------------
with tabs[0]:
    st.header("Facilities Overview")
    ff = facilities_df.copy()
    if selected_state and selected_state != "All":
        ff = ff[ff["state"] == selected_state]
    if ff.empty:
        st.info("No facility data for current filters.")
    else:
        if {"latitude", "longitude"}.issubset(ff.columns):
            fig = px.scatter_mapbox(
                ff,
                lat="latitude",
                lon="longitude",
                color="operational_status" if "operational_status" in ff.columns else None,
                hover_name="facility_name",
                hover_data=[c for c in ["state", "lga", "ownership", "type"] if c in ff.columns],
                zoom=5,
                height=550
            )
            fig.update_layout(mapbox_style="open-street-map")
            st.plotly_chart(fig, use_container_width=True)
        st.subheader("Facilities table")
        st.dataframe(ff, use_container_width=True)
        st.download_button("Download Facilities CSV", ff.to_csv(index=False).encode("utf-8"), file_name="facilities.csv")

# -----------------------------
# TAB: Health Workers
# -----------------------------
with tabs[1]:
    st.header("Health Worker Overview")
    hw = workers_df.copy()
    if active_facility_id is not None:
        hw = hw[hw["facility_id"] == active_facility_id]
    if hw.empty:
        st.info("No health worker data for current selection.")
    else:
        st.subheader("Counts by role")
        if "role" in hw.columns:
            role_counts = hw["role"].value_counts().reset_index()
            role_counts.columns = ["role", "count"]
            st.plotly_chart(px.bar(role_counts, x="role", y="count", title="Staff by Role"), use_container_width=True)
        st.dataframe(hw, use_container_width=True)
        st.download_button("Download Health Workers CSV", hw.to_csv(index=False).encode("utf-8"), file_name="health_workers.csv")

# -----------------------------
# TAB: Patients (trend + forecast)
# -----------------------------
with tabs[2]:
    st.header("Patients & Visits")
    pt = patients_df.copy()
    if active_facility_id is not None:
        pt = pt[pt["facility_id"] == active_facility_id]
    if pt.empty:
        st.info("No patient records for this selection.")
    else:
        st.subheader("Visits over time")
        if "visit_date" in pt.columns:
            visits = pt.dropna(subset=["visit_date"]).groupby("visit_date").size().reset_index(name="visits")
            visits = visits.sort_values("visit_date")
            visits_plot = visits.rename(columns={"visit_date": "ds", "visits": "y"})
            st.line_chart(visits.set_index("visit_date")["visits"])
            # Forecast if enough points
            if len(visits_plot) >= 8:
                try:
                    m = Prophet()
                    m.fit(visits_plot)
                    future = m.make_future_dataframe(periods=30)
                    forecast = m.predict(future)
                    figf = px.line(forecast, x="ds", y="yhat", title="Predicted Patient Visits (30 days)")
                    st.plotly_chart(figf, use_container_width=True)
                except Exception as e:
                    st.warning("Forecast failed: " + str(e))
            else:
                st.info("Not enough data points to produce a reliable forecast (need >=8).")
        # demographics
        if "age" in pt.columns:
            st.subheader("Age distribution")
            st.plotly_chart(px.histogram(pt, x="age", nbins=20, color="gender" if "gender" in pt.columns else None), use_container_width=True)
        if "outcome" in pt.columns:
            st.subheader("Outcomes")
            outc = pt["outcome"].value_counts().reset_index()
            outc.columns = ["outcome", "count"]
            st.plotly_chart(px.bar(outc, x="outcome", y="count"), use_container_width=True)
        st.dataframe(pt, use_container_width=True)
        st.download_button("Download Patients CSV", pt.to_csv(index=False).encode("utf-8"), file_name="patients.csv")

# -----------------------------
# TAB: Inventory (alerts + optional depletion projection)
# -----------------------------
with tabs[3]:
    st.header("Inventory & Stock Management")
    inv = inventory_df.copy()
    if active_facility_id is not None:
        inv = inv[inv["facility_id"] == active_facility_id]

    if inv.empty:
        st.info("No inventory data for this selection.")
    else:
        # basic color-coded view: (we'll show plain table, and low-stock table)
        st.subheader("Inventory table")
        st.dataframe(inv, use_container_width=True)

        # low stock (stock_level <= reorder_level)
        if {"stock_level", "reorder_level"}.issubset(inv.columns):
            inv["stock_level_float"] = pd.to_numeric(inv["stock_level"], errors="coerce").fillna(0)
            inv["reorder_level_float"] = pd.to_numeric(inv["reorder_level"], errors="coerce").fillna(0)
            low = inv[inv["stock_level_float"] <= inv["reorder_level_float"]]
            near = inv[(inv["stock_level_float"] > inv["reorder_level_float"]) & (inv["stock_level_float"] <= inv["reorder_level_float"] * 1.5)]
            if not low.empty:
                st.warning(f"Low stock items ({len(low)}):")
                st.dataframe(low[["item_name", "stock_level", "reorder_level", "last_restock_date"]], use_container_width=True)
            elif not near.empty:
                st.info("Some items are near reorder level:")
                st.dataframe(near[["item_name", "stock_level", "reorder_level"]], use_container_width=True)
            else:
                st.success("No items currently below reorder levels.")

        # attempt: depletion projection only if we have historical snapshots for items (multiple rows per item over time)
        st.subheader("Stock depletion projection (if historical inventory snapshots available)")
        # detect if inventory table has multiple snapshots per item (by item_name or item_id and last_restock_date)
        if "item_name" in inventory_df.columns and "last_restock_date" in inventory_df.columns:
            # group by item and see if there are multiple timestamps (this assumes the dataset contains snapshots)
            sample_counts = inventory_df.groupby(["item_name"])["last_restock_date"].nunique().reset_index(name="snapshots")
            candidates = sample_counts[sample_counts["snapshots"] > 1]["item_name"].tolist()
            if candidates:
                st.info("Historical snapshots found for some items. Attempting simple linear consumption estimate.")
                rows = []
                for item in candidates:
                    hist = inventory_df[inventory_df["item_name"] == item].dropna(subset=["last_restock_date"]).sort_values("last_restock_date")
                    # compute daily change between snapshots if possible
                    try:
                        hist["stock_level_num"] = pd.to_numeric(hist["stock_level"], errors="coerce")
                        hist = hist.dropna(subset=["stock_level_num"])
                        if len(hist) >= 2:
                            # compute slope = average daily consumption (positive number)
                            hist = hist.set_index("last_restock_date").resample("D").mean().interpolate()
                            hist = hist.reset_index()
                            hist["delta"] = hist["stock_level_num"].diff() * -1  # positive if decreasing
                            avg_daily_consumption = hist["delta"].dropna().mean()
                            latest_stock = hist["stock_level_num"].iloc[-1]
                            if avg_daily_consumption > 0:
                                days_left = latest_stock / avg_daily_consumption
                                rows.append({"item_name": item, "avg_daily_consumption": round(avg_daily_consumption,2), "latest_stock": int(latest_stock), "est_days_until_zero": int(days_left)})
                    except Exception:
                        continue
                if rows:
                    st.dataframe(pd.DataFrame(rows))
                else:
                    st.info("Could not compute depletion projections from available snapshots.")
            else:
                st.info("No historical inventory snapshots detected in dataset; skipping depletion projections.")

        # show only low stock if requested
        if show_low_stock_only and "stock_level_float" in inv.columns:
            st.subheader("Filtered: low-stock only")
            st.dataframe(inv[inv["stock_level_float"] <= inv["reorder_level_float"]], use_container_width=True)

        st.download_button("Download Inventory CSV", inv.to_csv(index=False).encode("utf-8"), file_name="inventory.csv")

# -----------------------------
# TAB: Disease Reports (trend & per-facility)
# -----------------------------
with tabs[4]:
    st.header("Disease Reports & Trends")
    dr = diseases_df.copy()
    if active_facility_id is not None:
        dr = dr[dr["facility_id"] == active_facility_id]

    if dr.empty:
        st.info("No disease report records for this selection.")
    else:
        # time-series by month if month_dt available
        if "month_dt" in dr.columns:
            trend = dr.groupby("month_dt")["cases_reported"].sum().reset_index()
            st.subheader("Cases over time")
            st.plotly_chart(px.line(trend, x="month_dt", y="cases_reported", title="Cases over time"), use_container_width=True)
            # forecast disease cases if enough points
            if len(trend) >= 8:
                try:
                    tf = trend.rename(columns={"month_dt":"ds", "cases_reported":"y"})
                    model = Prophet()
                    model.fit(tf)
                    future = model.make_future_dataframe(periods=3, freq='M')
                    fcast = model.predict(future)
                    st.plotly_chart(px.line(fcast, x="ds", y="yhat", title="Disease cases forecast (monthly)"), use_container_width=True)
                except Exception as e:
                    st.warning("Disease forecast not available: " + str(e))
        # summary table
        summary = dr.groupby("disease")[["cases_reported","deaths"]].sum().reset_index()
        st.subheader("Summary by disease")
        st.dataframe(summary, use_container_width=True)
        st.download_button("Download Disease Reports CSV", dr.to_csv(index=False).encode("utf-8"), file_name="disease_reports.csv")

# -----------------------------
# TAB: Chatbot (facility-aware + multilingual)
# -----------------------------
with tabs[5]:
    st.header("Chatbot — Ask about the selected facility")
    st.markdown("Ask questions like: 'What is the stock?', 'How many patients?', 'Who are the workers?', 'How many malaria cases?'")
    query = st.text_input("Type your question (facility context comes from the sidebar selection):", placeholder="e.g. What stock do we have for malaria drugs?")
    if query:
        q = query.strip().lower()
        response = "I could not find an answer. Try asking specifically about stock, patients, workers, or disease cases."

        # Ensure facility context
        if active_facility_id is None:
            response = "No facility selected. Please choose a facility in the sidebar to get facility-specific answers."
        else:
            try:
                if "stock" in q or "inventory" in q or "drug" in q or "medicine" in q:
                    df_inv = inventory_df[inventory_df["facility_id"] == active_facility_id]
                    if df_inv.empty:
                        response = f"No inventory records for {selected_facility}."
                    else:
                        # optional: check item name in question
                        matched_item = None
                        for it in df_inv["item_name"].dropna().unique():
                            if str(it).lower() in q:
                                matched_item = it
                                break
                        if matched_item:
                            r = df_inv[df_inv["item_name"] == matched_item].iloc[0]
                            response = f"{matched_item}: stock={r['stock_level']}, reorder_level={r['reorder_level']}"
                        else:
                            # list low or all items
                            low_items = df_inv[df_inv["stock_level"].astype(float) <= df_inv["reorder_level"].astype(float)]
                            if not low_items.empty:
                                names = ", ".join(low_items["item_name"].astype(str).head(10).tolist())
                                response = f"Low-stock items at {selected_facility}: {names}"
                            else:
                                # show top items
                                names = ", ".join(df_inv["item_name"].astype(str).head(10).tolist())
                                response = f"Inventory items at {selected_facility}: {names}"

                elif "patient" in q or "visit" in q:
                    df_pat = patients_df[patients_df["facility_id"] == active_facility_id]
                    if df_pat.empty:
                        response = f"No patient records for {selected_facility}."
                    else:
                        # count and top diagnoses
                        total = df_pat.shape[0]
                        top_dx = df_pat["diagnosis"].value_counts().head(3).to_dict() if "diagnosis" in df_pat.columns else {}
                        response = f"{selected_facility} total patient visits: {total}. Top diagnoses: {top_dx}"

                elif "worker" in q or "staff" in q or "nurse" in q or "doctor" in q:
                    df_w = workers_df[workers_df["facility_id"] == active_facility_id]
                    if df_w.empty:
                        response = f"No worker records for {selected_facility}."
                    else:
                        counts = df_w["role"].value_counts().to_dict() if "role" in df_w.columns else {"total": len(df_w)}
                        response = f"{selected_facility} staff summary: {counts}"

                elif "disease" in q or "cases" in q or "malaria" in q or "covid" in q:
                    df_d = diseases_df[diseases_df["facility_id"] == active_facility_id]
                    if df_d.empty:
                        response = f"No disease report for {selected_facility}."
                    else:
                        # detect disease mentioned
                        found = None
                        for d in df_d["disease"].dropna().unique():
                            if str(d).lower() in q:
                                found = d
                                break
                        if found:
                            s = int(df_d[df_d["disease"].str.lower() == str(found).lower()]["cases_reported"].sum())
                            response = f"{selected_facility} reported {s} cases of {found}."
                        else:
                            total = int(df_d["cases_reported"].sum())
                            response = f"{selected_facility} total reported cases: {total}"

                else:
                    response = "I can answer: stock, patients, workers, or disease cases. Try: 'What stock is low?'"
            except Exception as e:
                response = f"Error processing query: {e}"

        # translate and show
        target = LANG_MAP.get(chat_lang, "en")
        answer_en = response
        answer_translated = translate_text(answer_en, target) if target != "en" else answer_en

        st.subheader("Answer")
        st.markdown("**English:**")
        st.text(answer_en)
        if target != "en":
            st.markdown(f"**{chat_lang}:**")
            st.text(answer_translated)

# -----------------------------
# Footer
# -----------------------------
st.markdown("---")
st.caption("PHC AI Dashboard — Demo. For production, move credentials to secure secrets and add authentication/role-based access.")
