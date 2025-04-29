import os
import streamlit as st
import requests
import pandas as pd
import altair as alt
from datetime import datetime


API_BASE = os.getenv("API_URL", "http://127.0.0.1:8000")
API_URL  = f"{API_BASE}/failed-trades"


def main():
    st.set_page_config(page_title="Failed Trades Dashboard", layout="wide")
    st.title("📉 Monorail MCP Failed Trades Dashboard")
    st.write("🔍 Fetching from:", repr(API_URL))


    try:
        resp = requests.get(API_URL)
        resp.raise_for_status()
        data = resp.json().get("failed_trades", [])
    except requests.exceptions.RequestException as e:
        st.error(f"Error fetching data: {e}")
        return

    if not data:
        st.info("No failed trades recorded yet.")
        return

    # Convert to DataFrame for chart
    df = pd.DataFrame(data)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

    # Bar chart: failures per token pair
    st.subheader("Failures by Token Pair")
    chart = (
        alt.Chart(df)
           .mark_bar()
           .encode(
               x=alt.X("pair:N", title="Token Pair"),
               y=alt.Y("count():Q", title="Number of Failures"),
               tooltip=["pair", "count()"]
           )
           .properties(width=700)
    )
    st.altair_chart(chart, use_container_width=True)

    # Detailed list
    st.subheader("Detailed Failed Trades")
    for trade in data:
        ts_raw = trade.get('timestamp', '')
        try:
            ts = datetime.fromisoformat(ts_raw.replace('Z',''))
            formatted_ts = ts.strftime("%Y-%m-%d %H:%M:%S")
        except:
            formatted_ts = ts_raw

        st.markdown(f"""
**Trade ID:** {trade.get('id', 'N/A')}  
**Pair:** {trade.get('pair', 'N/A')}  
**Error:** {trade.get('error', 'No error message')}  
**Time:** {formatted_ts}
""")
        st.json(trade.get('payload', {}))
        st.markdown("---")

if __name__ == "__main__":
    main()