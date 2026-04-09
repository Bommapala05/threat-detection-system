# detection/engine.py

import time
from ml_model import train_model, predict_threat

history = {}

print("[INFO] Training ML Model...")
try:
    ml_model = train_model()
    print("[INFO] ML Model Trained Successfully")
except Exception as e:
    print(f"[ERROR] ML Model failed to train: {e}")
    ml_model = None

def detect(ip, event, ioc_data):
    score = 0
    reasons = []

    current_time = time.time()

    # Initialize history
    if ip not in history:
        history[ip] = {
            "failures": 0,
            "successes": 0,
            "events": [],
            "first_seen": current_time
        }

    # Track behavior
    history[ip]["events"].append((event, current_time))

    if event == "LOGIN_FAILED":
        history[ip]["failures"] += 1
    elif event == "LOGIN_SUCCESS":
        history[ip]["successes"] += 1

    # 🔥 ML Based Threat Detection
    if ml_model:
        ml_prediction = predict_threat(ml_model, history[ip]["failures"], history[ip]["successes"])
        if ml_prediction == "HIGH":
            score += 50
            reasons.append("ML Model flagged behavior as HIGH threat")

    # 🔥 OSINT Matching with confidence decay
    if ip in ioc_data:
        ioc = ioc_data[ip]

        age = current_time - ioc["timestamp"]
        decay_factor = max(0.3, 1 - (age / 86400))  # 1 day decay

        osint_score = 70 * ioc["confidence"] * decay_factor
        score += osint_score
        reasons.append("OSINT match")

    # 🔥 Behavior Rules
    if history[ip]["failures"] > 5:
        score += 20
        reasons.append("Brute force behavior")

    # 🔥 Pattern Detection
    events = [e[0] for e in history[ip]["events"][-3:]]

    if events == ["LOGIN_FAILED", "LOGIN_FAILED", "LOGIN_SUCCESS"]:
        score += 30
        reasons.append("Account takeover pattern")

    # 🔥 Unknown IP but aggressive activity
    if ip not in ioc_data and len(history[ip]["events"]) > 10:
        score += 15
        reasons.append("Anomalous activity")

    # Classification
    if score > 80:
        return "CRITICAL", reasons
    elif score > 50:
        return "HIGH", reasons
    elif score > 20:
        return "MEDIUM", reasons
    else:
        return None, []