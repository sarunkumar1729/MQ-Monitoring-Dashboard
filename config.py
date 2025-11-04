# RabbitMQ Config
RABBITMQ_HOST = "localhost"
RABBITMQ_URL = "amqps://kwvizzuf:fyF1bexQjw7vJi7vTwl8ONm_Gg3XRGFj@armadillo.rmq.cloudamqp.com/kwvizzuf"
# Define queues to monitor (vhost, queue_name, max_length, threshold%)
QUEUES = [
    ("kwvizzuf", "Finance_invoices", 1000, 80),
    ("kwvizzuf", "Finance_payments", 500, 70),
    ("kwvizzuf", "Orders_failed_orders", 2000, 85),
    ("kwvizzuf", "Orders_new_orders", 300, 60)
]

# Email Config (for alerts)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "santosenderbits@gmail.com"
EMAIL_PASSWORD = "oocq tfix lwqw kwpk" 
EMAIL_RECEIVER = "santobits22@gmail.com"


