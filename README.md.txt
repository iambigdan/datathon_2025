# PHC AI Dashboard Hackathon

This is a Streamlit dashboard for **Primary Health Care (PHC) data in Africa**.  
It provides interactive dashboards, predictive analytics, and a multilingual chatbot to help health workers and policymakers make data-driven decisions.

---

## Features

- **Multi-tab dashboards**:
  - Facilities
  - Health Workers
  - Patients
  - Disease Reports
  - Inventory

- **Predictive analytics**:
  - Patient visits forecast
  - Disease trends
  - Stock-out predictions

- **Multilingual Chatbot**:
  - Supports **English**, **Igbo**, and **Yoruba**
  - Interactive queries about PHC data

- **Live database connection**:
  - Connected to **AWS Redshift** for up-to-date PHC data

- **Alerts**:
  - Low stock notifications
  - Patient surges
  - Disease outbreak warnings

---

## How to Run

1. Install Python packages:

```bash
pip install -r requirements.txt
2. Run the app:

bash
streamlit run app.py

3. Open your browser at http://localhost:8501 to interact with the dashboard.

