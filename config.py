# RabbitMQ Config
RABBITMQ_HOST = "localhost"

# Define queues to monitor (vhost, queue_name, max_length, threshold%)
QUEUES = [
    ("Finance", "payments", 1000, 80),
    ("Finance", "invoices", 500, 70),
    ("Orders", "new_orders", 2000, 85),
    ("Orders", "failed_orders", 300, 60)
]

# Email Config (for alerts)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "santosenderbits@gmail.com"
EMAIL_PASSWORD = "oocq tfix lwqw kwpk" 
EMAIL_RECEIVER = "santobits22@gmail.com"


