import smtplib
import time
from email.mime.text import MIMEText
from utils import get_queue_depth, check_threshold
from db_utils import insert_metric, init_db
from config import QUEUES, SMTP_SERVER, SMTP_PORT, EMAIL_SENDER, EMAIL_PASSWORD, EMAIL_RECEIVER

# Initialize DB
init_db()

# Track last alert timestamp per queue
last_alert_time = {}
ALERT_THROTTLE = 60  # seconds

def send_email(queue_name, vhost, percent):
    msg = MIMEText(f" Queue '{queue_name}' in vhost '{vhost}' exceeded threshold: {percent:.2f}%")
    msg['Subject'] = f"MQ Queue Alert: {queue_name}"
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECEIVER

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)
        print(f"Alert sent for queue '{queue_name}' ({percent:.2f}%)")

if __name__ == "__main__":
    print("Starting MQ monitoring and alerting...")

    while True:
        for vhost, queue_name, max_length, threshold_percent in QUEUES:
            depth = get_queue_depth(vhost, queue_name)
            insert_metric(vhost, queue_name, depth)  # store historical record

            percent, alert_needed = check_threshold(depth, max_length, threshold_percent)
            if alert_needed:
                now = time.time()
                last_time = last_alert_time.get((vhost, queue_name), 0)
                if now - last_time > ALERT_THROTTLE:
                    send_email(queue_name, vhost, percent)
                    last_alert_time[(vhost, queue_name)] = now
        time.sleep(2)

