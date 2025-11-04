import streamlit as st
import plotly.express as px
from datetime import datetime
from db_utils import get_metrics
from utils import get_queue_depth, check_threshold
from config import QUEUES

# ---- Page Config ----
st.set_page_config(page_title="MQ Monitoring Dashboard", layout="wide")
st.title("RabbitMQ Queue Monitoring Dashboard")

# refresh interval in milliseconds
REFRESH_INTERVAL = 2000  # 2 seconds

# --- autorefresh ---
st_autorefresh_fn = None
try:
    st_autorefresh_fn = st.experimental_autorefresh
except Exception:
    try:
        from streamlit_autorefresh import st_autorefresh as _sa
        st_autorefresh_fn = _sa
    except Exception:
        st.warning(
            "Auto-refresh not available. Upgrade Streamlit or install `streamlit-autorefresh`."
        )

if st_autorefresh_fn:
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

    # Display table
    def format_metrics_table(metrics):
        headers = list(metrics[0].keys())
        table_data = [headers] + [[m[h] for h in headers] for m in metrics]
        return table_data

    table_data = format_metrics_table(metrics)
    st.subheader("Queue Metrics")
    st.table(table_data)

    # Progress bars
    st.subheader("Queue Utilization")
    for m in metrics:
        name = f"{m['Vhost']}/{m['Queue']}"
        col1, col2 = st.columns([1, 4])
        with col1:
            st.write(name)
        with col2:
            pct = max(0, min(int(m["Percent"]), 100))
            st.progress(pct)
            st.write(f"Usage: {m['Percent']:.2f}% | Threshold: {m['Threshold']}")

# --- Historical Trends Tab ---
with tabs[1]:
    st.subheader("Queue Depth Trends (Last 24 Hours)")
    for vhost, queue_name, _, _ in QUEUES:
        data = get_metrics(vhost, queue_name, limit=288)  # 24h at 5-min interval
        if data:
            # Convert timestamps to datetime objects
            timestamps = [datetime.fromisoformat(d[0]) if isinstance(d[0], str) else d[0] for d in data]
            depths = [d[1] for d in data]

            # Build Plotly figure
            fig = px.line(
                x=timestamps,
                y=depths,
                title=f"Queue Depth Trend: {vhost}/{queue_name}",
                labels={"x": "Time", "y": "Queue Depth"},
            )

            # Safe key for Streamlit
            raw_key = f"chart_{vhost}_{queue_name}"
            safe_key = "".join(c if c.isalnum() else "_" for c in raw_key)

            st.plotly_chart(fig, use_container_width=True, key=safe_key)
        else:
            st.write(f"No historical data for {vhost}/{queue_name}")
