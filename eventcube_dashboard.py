import streamlit as st
import requests
import pandas as pd
from collections import defaultdict

# --- Config ---
BASE_URL = "https://socawkndr.eventcube.io/api/v1"
API_KEY = "b2c12817-45f5-459a-85d6-18258df74387"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

# --- Page Setup ---
st.set_page_config(page_title="Ticket Sales Dashboard", layout="wide")
st.title("📊 Ticket Sales Dashboard")

# --- Refresh Button ---
if st.button("🔄 Refresh All Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# --- Tabs ---
tab1, tab2 = st.tabs(["Soca Wkndr (Eventcube)", "Events Int (Wix)"])

# ================================
# TAB 1: Eventcube Ticket Summary
# ================================
with tab1:
    st.header("🎟️ Soca Wkndr - Eventcube Tickets")

    # --- API Calls ---
    @st.cache_data
    def fetch_events():
        r = requests.get(f"{BASE_URL}/events", headers=HEADERS)
        return r.json().get("results", []) if r.status_code == 200 else []

    @st.cache_data
    def fetch_all_orders_paginated():
        all_orders = []
        page = 1
        while True:
            url = f"{BASE_URL}/orders?page={page}"
            r = requests.get(url, headers=HEADERS)
            if r.status_code != 200:
                break
            data = r.json()
            batch = data.get("results", [])
            if not batch:
                break
            all_orders.extend(batch)
            page += 1
        return all_orders

    # --- Fetch Data ---
    events = fetch_events()
    orders = fetch_all_orders_paginated()

    st.info(f"📦 Total Eventcube Orders: {len(orders)}")
    st.divider()

    # --- Calculate Totals Per Event ---
    event_totals = defaultdict(int)

    for order in orders:
        for item in order.get("items", []):
            ticket = item.get("ticket", {})
            event = ticket.get("event", {})
            event_title = event.get("title", "Unknown Event")
            quantity = item.get("quantity", 1)
            event_totals[event_title] += quantity

    # --- Create Summary Table ---
    df_summary = pd.DataFrame([
        {"Event Name": event, "Tickets Sold": total}
        for event, total in event_totals.items()
    ]).sort_values(by="Tickets Sold", ascending=False)

    st.table(df_summary)

# ================================
# TAB 2: Wix (Coming Soon)
# ================================
with tab2:
    st.header("🌍 Events Int - Wix Events")
    st.warning("🔧 This tab is under construction. API integration coming soon!")
