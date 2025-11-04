import streamlit as st
import pandas as pd
import plotly.express as px
from db_utils import get_metrics
from utils import get_queue_depth, check_threshold
from config import QUEUES

# ---- Page Config ----
st.set_page_config(page_title="MQ Monitoring Dashboard", layout="wide")
st.title("RabbitMQ Queue Monitoring Dashboard")

# Refresh interval in milliseconds
REFRESH_INTERVAL = 2000  # 2 seconds

# --- Auto-refresh setup ---
st_autorefresh_fn = None
try:
    # Newer Streamlit versions expose this
    st_autorefresh_fn = st.experimental_autorefresh
except Exception:
    try:
        # Install with: python -m pip install streamlit-autorefresh
        from streamlit_autorefresh import st_autorefresh as _sa
        st_autorefresh_fn = _sa
    except Exception:
        st.warning(
            "Auto-refresh not available. To enable it, either upgrade Streamlit or install streamlit-autorefresh:\n"
            "python -m pip install --upgrade streamlit OR python -m pip install streamlit-autorefresh"
        )

if st_autorefresh_fn:
    # st_autorefresh returns an integer that increments on each refresh (unused here)
    st_autorefresh_fn(interval=REFRESH_INTERVAL, key="mq_refresh")

# ---- Tabs ----
tabs = st.tabs(["Current Queue Status", "Historical Trends"])

# --- Current Status Tab ---
with tabs[0]:
    metrics = []
    for vhost, queue_name, max_length, threshold in QUEUES:
        depth = get_queue_depth(vhost, queue_name)
        percent, alert = check_threshold(depth, max_length, threshold)
        metrics.append({
            "Vhost": vhost,
            "Queue": queue_name,
            "Depth": depth,
            "Max Length": max_length,
            "Threshold": threshold,
            "Percent": percent,
            "Alert": alert
        })

    df = pd.DataFrame(metrics)

    # Highlight alerts in table using Styler (safe for newer Streamlit)
    def highlight_alert(row):
        return ['background-color: red; color: white' if row["Alert"] else '' for _ in row]

    try:
        styled = df.style.apply(highlight_alert, axis=1)
        st.dataframe(styled, use_container_width=True)
    except Exception:
        # fallback: plain table if styling not supported
        st.dataframe(df, use_container_width=True)

    # Show progress bars with labels
    st.subheader("Queue Utilization")
    for _, row in df.iterrows():
        name = f"{row['Vhost']}/{row['Queue']}"
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write(name)
        with col2:
            pct = max(0, min(int(row["Percent"]), 100))
            st.progress(pct)
            st.write(f"Usage: {row['Percent']:.2f}% | Threshold: {row['Threshold']}")

# --- Historical Trends Tab ---
with tabs[1]:
    st.subheader("Queue Depth Trends (Last 24 Hours)")
    for vhost, queue_name, _, _ in QUEUES:
        data = get_metrics(vhost, queue_name, limit=288)  # 24h at 5-min interval
        if data:
            trend_df = pd.DataFrame(data, columns=["Timestamp", "Depth"])
            trend_df["Timestamp"] = pd.to_datetime(trend_df["Timestamp"])
            trend_df.set_index("Timestamp", inplace=True)

            # Build Plotly figure
            fig = px.line(
                trend_df,
                y="Depth",
                title=f"Queue Depth Trend: {vhost}/{queue_name}",
                labels={"Depth": "Queue Depth", "Timestamp": "Time"},
            )

            # Create safe unique key (replace non-alnum)
            raw_key = f"chart_{vhost}_{queue_name}"
            safe_key = "".join(c if c.isalnum() else "_" for c in raw_key)
            st.plotly_chart(fig, use_container_width=True, key=safe_key)
        else:
            st.write(f"No historical data for {vhost}/{queue_name}")
