import random
import sqlite3
from datetime import datetime, timedelta
from config import QUEUES
from db_utils import DB_FILE

NUM_RECORDS = 288  # 24 hours * 12 records per hour (every 5 minutes)
TIME_INTERVAL = 5  # minutes between records

# Connect to DB
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()
 
# Clear existing records
c.execute('DELETE FROM queue_metrics')
conn.commit()

print("🗑 Cleared existing records.")

# Generate historical records for last 24 hours
for vhost, queue_name, max_length, threshold in QUEUES:
    current_time = datetime.now() - timedelta(hours=24)  # start 24 hours ago
    for _ in range(NUM_RECORDS):
        depth = random.randint(0, max_length)  # random depth
        c.execute('INSERT INTO queue_metrics (timestamp, vhost, queue, depth) VALUES (?, ?, ?, ?)',
                  (current_time.strftime("%Y-%m-%d %H:%M:%S"), vhost, queue_name, depth))
        current_time += timedelta(minutes=TIME_INTERVAL)

conn.commit()
conn.close()
print("✅ Historical records for last 24 hours inserted.")
