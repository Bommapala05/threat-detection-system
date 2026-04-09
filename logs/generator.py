import random
import time

# 🔥 Mix of normal + suspicious IPs
IPS = [
    "185.23.11.9",   # suspicious
    "103.21.244.1",
    "8.8.8.8",
    "142.250.183.14",
    "45.33.32.156",
    "192.168.1.5",
    "172.16.0.2",
    "91.121.90.1",
    "66.249.66.1"
]

EVENTS = ["LOGIN_FAILED", "LOGIN_SUCCESS", "DOWNLOAD"]

def generate_logs():
    while True:
        ip = random.choice(IPS)

        # 🔥 Simulate attack behavior (more failures for bad IP)
        if ip == "185.23.11.9":
            event = random.choices(
                ["LOGIN_FAILED", "DOWNLOAD"],
                weights=[0.7, 0.3]
            )[0]
        else:
            event = random.choice(EVENTS)

        log = {
            "ip": ip,
            "event": event
        }

        yield log
        time.sleep(1)  # faster for demos