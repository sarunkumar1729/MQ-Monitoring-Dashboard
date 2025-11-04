import pika
import sys
import time

def send_messages(vhost, queue_name, num_messages=100):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="localhost",
            virtual_host=vhost,
            credentials=pika.PlainCredentials("guest", "guest")  # add credentials
        )
    )
    channel = connection.channel()

    # Remove queue_declare if queue already exists
    # channel.queue_declare(queue=queue_name, durable=True, arguments={"x-queue-type": "classic"})

    for i in range(num_messages):
        message = f"Message {i+1} for {queue_name}"
        channel.basic_publish(exchange="", routing_key=queue_name, body=message)
        print(f"Sent: {message}")
        time.sleep(0.1)  # slow down so you can watch queue depth grow

    connection.close()

if __name__ == "__main__":
    # Usage: python producer.py vhost queue_name 50
    if len(sys.argv) < 3:
        print("Usage: python producer.py <vhost> <queue_name> [num_messages]")
        sys.exit(1)

    vhost = sys.argv[1]
    queue_name = sys.argv[2]
    num_messages = int(sys.argv[3]) if len(sys.argv) > 3 else 100

    send_messages(vhost, queue_name, num_messages)

# sample : python produer.py Finance payments 80