import streamlit as st
import pika
import time

QUEUE_NAME = "test_queue"
RABBITMQ_HOST = "localhost"   # Change if using remote RabbitMQ
THRESHOLD = 50                # Alert threshold

# Function to get queue depth
def get_queue_depth(queue_name=QUEUE_NAME):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(RABBITMQ_HOST))
        channel = connection.channel()
        queue = channel.queue_declare(queue=queue_name, passive=True)
        depth = queue.method.message_count
        connection.close()
        return depth
    except Exception as e:
        return f"Error: {e}"

# Streamlit UI
st.set_page_config(page_title="MQ Queue Monitor", layout="wide")

st.title("MQ Queue Depth Monitoring")
st.write("Monitoring RabbitMQ queue in real-time with alerts.")

# Auto-refresh every few seconds
refresh_rate = st.sidebar.slider("Refresh interval (seconds)", 2, 30, 5)

placeholder = st.empty()

while True:
    depth = get_queue_depth()
    with placeholder.container():
        if isinstance(depth, int):
            st.metric(label="Queue Depth", value=depth)

            # Show alert if threshold crossed
            if depth > THRESHOLD:
                st.error(f"ALERT: Queue depth exceeded threshold ({depth} > {THRESHOLD})!")
            else:
                st.success(f"Queue depth is healthy ({depth} ≤ {THRESHOLD})")
        else:
            st.error(depth)

    time.sleep(refresh_rate)
    st.rerun()
