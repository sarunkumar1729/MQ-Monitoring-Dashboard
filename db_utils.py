import sqlite3
from config import QUEUES

DB_FILE = "mq_history.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    # Create table if not exists
    c.execute('''
        CREATE TABLE IF NOT EXISTS queue_metrics (
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            vhost TEXT,
            queue TEXT,
            depth INTEGER
        )
    ''')
    conn.commit()
    conn.close()

def insert_metric(vhost, queue, depth):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('INSERT INTO queue_metrics (vhost, queue, depth) VALUES (?, ?, ?)', (vhost, queue, depth))
    conn.commit()
    conn.close()

def get_metrics(vhost, queue, limit=100):
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''
        SELECT timestamp, depth FROM queue_metrics
        WHERE vhost=? AND queue=?
        ORDER BY timestamp ASC
        LIMIT ?
    ''', (vhost, queue, limit))
    rows = c.fetchall()
    conn.close()
    return rows
