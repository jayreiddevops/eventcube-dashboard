import streamlit as st
import requests
import pandas as pd
from collections import defaultdict
from datetime import datetime, timezone

# --- Config ---
BASE_URL = "https://socawkndr.eventcube.io/api/v1"
API_KEY = "b2c12817-45f5-459a-85d6-18258df74387"
HEADERS = {"Authorization": f"Bearer {API_KEY}"}

st.set_page_config(page_title="Event Dashboard", layout="wide")
st.title("📊 Ticket Sales Dashboard")

# --- Refresh Button ---
if st.button("🔄 Refresh All Data"):
    st.cache_data.clear()
    st.experimental_rerun()

# --- Tabs ---
tab1, tab2 = st.tabs(["Soca Wkndr (Eventcube)", "Events Int (Wix)"])

# =========================
# TAB 1: Eventcube Tickets
# =========================
with tab1:
    st.header("🎟️ Soca Wkndr - Eventcube Tickets")

    # --- Fetch Eventcube Data ---
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

    events = fetch_events()
    orders = fetch_all_orders_paginated()

    st.info(f"📦 Total Eventcube Orders: {len(orders)}")
    st.divider()

    # --- Build and Show Table (Future Events Only) ---
    event_ticket_data = defaultdict(lambda: defaultdict(int))
    event_dates = {}

    for order in orders:
        for item in order.get("items", []):
            ticket = item.get("ticket", {})
            event = ticket.get("event", {})
            event_title = event.get("title", "Unknown Event")
            ticket_title = ticket.get("title", "Unnamed Ticket")
            quantity = item.get("quantity", 1)
            start_time = event.get("start_time")

            if not start_time:
                continue

            # Convert ISO datetime to aware datetime object
            try:
                start_dt = datetime.fromisoformat(start_time.replace("Z", "+00:00"))
            except ValueError:
                continue

            # Only include events in the future
            if start_dt > datetime.now(timezone.utc):
                event_ticket_data[event_title][ticket_title] += quantity
                event_dates[event_title] = start_dt

    # --- Aggregate Totals per Event ---
    event_totals = {
        event: sum(ticket_counts.values())
        for event, ticket_counts in event_ticket_data.items()
    }

    # --- Sort Events by Date ---
    sorted_events = sorted(event_totals.items(), key=lambda x: event_dates.get(x[0], datetime.max))

    # --- Show Summary Table ---
    df_summary = pd.DataFrame([
        {"Event Name": event, "Tickets Sold": total}
        for event, total in sorted_events
    ])

    st.table(df_summary)

# =========================
# TAB 2: Wix Events
# =========================
with tab2:
    st.header("🌍 Events Int - Wix Events")
    st.warning("🔧 This tab is under construction. API integration coming soon!")
