import pika
from alert import send_email_alert

# ---------------------------
# CONFIGURATION
# ---------------------------
QUEUE_NAME = "test_queue"
THRESHOLD = 50  # set your alert threshold

# ---------------------------
# FUNCTION TO CHECK DEPTH
# ---------------------------
def get_queue_depth(queue_name=QUEUE_NAME):
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # passive=True → check queue without creating new one
    queue = channel.queue_declare(queue=queue_name, passive=True)
    depth = queue.method.message_count

    connection.close()
    return depth

# ---------------------------
# MAIN LOGIC
# ---------------------------
if __name__ == "__main__":
    depth = get_queue_depth()
    print(f"Queue depth for '{QUEUE_NAME}': {depth}")

    if depth > THRESHOLD:
        print(f"[ALERT] Queue depth {depth} exceeded threshold {THRESHOLD}")
        send_email_alert(QUEUE_NAME, depth, THRESHOLD)
    else:
        print(f"[OK] Queue depth {depth} is within safe limits (threshold {THRESHOLD})")
