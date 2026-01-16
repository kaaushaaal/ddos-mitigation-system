import time
from collections import defaultdict

class TokenBucket:
    def __init__(self, rate, capacity):
        self.rate = rate          # tokens per second
        self.capacity = capacity
        self.tokens = capacity
        self.last_refill = time.time()

    def allow(self):
        now = time.time()
        elapsed = now - self.last_refill
        self.tokens = min(self.capacity, self.tokens + elapsed * self.rate)
        self.last_refill = now

        if self.tokens >= 1:
            self.tokens -= 1
            return True
        return False


# Per-IP buckets
buckets = defaultdict(lambda: TokenBucket(rate=5, capacity=10))

def is_allowed(ip, system_state):
    # Adjust limits based on system state
    if system_state == "ATTACK":
        buckets[ip].rate = 1
        buckets[ip].capacity = 3
    elif system_state == "SUSPICIOUS":
        buckets[ip].rate = 3
        buckets[ip].capacity = 6
    else:  # NORMAL
        buckets[ip].rate = 5
        buckets[ip].capacity = 10

    return buckets[ip].allow()
