import pika
import sys

def consume_messages(vhost, queue_name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
            virtual_host=vhost,
            credentials=pika.PlainCredentials("guest", "guest")
        )
    )
    channel = connection.channel()

    # Just make sure queue exists
    # channel.queue_declare(queue=queue_name, durable=True)

    def callback(ch, method, properties, body):
        print(f"Received: {body.decode()}")
        # Acknowledge the message
        ch.basic_ack(delivery_tag=method.delivery_tag)

    channel.basic_consume(queue=queue_name, on_message_callback=callback)
    print(f"Consuming messages from queue '{queue_name}' in vhost '{vhost}'... Press Ctrl+C to stop.")
    channel.start_consuming()

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python consumer.py <vhost> <queue_name>")
        sys.exit(1)

    vhost = sys.argv[1]
    queue_name = sys.argv[2]

    consume_messages(vhost, queue_name)

# python consumer.py Finance payments