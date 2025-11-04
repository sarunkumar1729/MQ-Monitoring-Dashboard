import pika
from config import RABBITMQ_HOST

def get_queue_depth(vhost, queue_name):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBITMQ_HOST,
            port=5672,
            virtual_host=vhost,
            credentials=pika.PlainCredentials("guest", "guest")
        )
    )
    channel = connection.channel()
    queue = channel.queue_declare(queue=queue_name, passive=True)
    depth = queue.method.message_count
    connection.close()
    return depth

def check_threshold(depth, max_length, threshold_percent):
    if max_length == 0:
        return 0, False
    percent = (depth / max_length) * 100
    return percent, percent >= threshold_percent
