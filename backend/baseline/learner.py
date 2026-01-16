import time
import statistics
from storage.db import get_connection

WINDOW = 60  # seconds

def save_window(request_count):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT INTO baseline (timestamp, request_count) VALUES (?, ?)",
        (int(time.time()), request_count)
    )

    conn.commit()
    conn.close()

def load_history():
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT request_count FROM baseline")
    rows = cur.fetchall()
    conn.close()

    return [r[0] for r in rows]

def compute_baseline():
    history = load_history()

    if len(history) < 1:
        return None  # not enough data yet

    mean = statistics.mean(history)
    std = statistics.stdev(history)

    return {
        "mean": mean,
        "std": std,
        "samples": len(history)
    }
