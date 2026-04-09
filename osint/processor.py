import time

def normalize_otx(data):
    normalized = {}

    # Handle different response formats
    if isinstance(data, dict):
        indicators = data.get("results", [])
    else:
        indicators = data

    count = 0

    for item in indicators:
        if count >= 1000:
            break

        # 🔥 Handle BOTH formats
        if isinstance(item, dict):
            ip = item.get("indicator")
        elif isinstance(item, str):
            ip = item
        else:
            continue

        if ip:
            normalized[ip] = {
                "type": "ip",
                "confidence": 0.8,
                "source": "OTX",
                "timestamp": time.time()
            }
            count += 1

    return normalized