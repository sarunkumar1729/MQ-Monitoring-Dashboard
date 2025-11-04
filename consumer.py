import pika
import sys
from config import RABBITMQ_URL

def consume_messages(vhost, queue_name):
    params = pika.URLParameters(RABBITMQ_URL)
    connection = pika.BlockingConnection(params)
    channel = connection.channel()

    # Ensure queue exists
    channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        print(f"📥 Received: {body.decode()}")
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print(f"🎧 Listening to '{queue_name}' in vhost '{vhost}' (Ctrl+C to stop)...")
    channel.start_consuming()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python consumer.py <vhost> <queue_name>")
        sys.exit(1)

    vhost = sys.argv[1]
    queue_name = sys.argv[2]

    consume_messages(vhost, queue_name)
