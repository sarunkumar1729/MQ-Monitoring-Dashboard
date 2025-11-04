import pika
import sys
import time
from config import RABBITMQ_URL

def send_messages(vhost, queue_name, num_messages=100):
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Declare queue if not already present (CloudAMQP auto-creates if needed)
    channel.queue_declare(queue=queue_name, durable=True)

    for i in range(num_messages):
        message = f"Message {i+1} for {queue_name}"
        channel.basic_publish(exchange="", routing_key=queue_name, body=message)
        print(f"Sent: {message}")
        time.sleep(0.1)

    connection.close()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python producer.py <vhost> <queue_name> [num_messages]")
        sys.exit(1)

    vhost = sys.argv[1]
    queue_name = sys.argv[2]
    num_messages = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    send_messages(vhost, queue_name, num_messages)
