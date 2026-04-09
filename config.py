import os

OTX_API_KEY = os.getenv("OTX_API_KEY", "your_otx_key_here")
DB_PATH = os.getenv("DB_PATH", "threats.db")

REFRESH_INTERVAL = 1800  # 30 mins
THREAT_THRESHOLD = {
    "CRITICAL": 80,
    "HIGH": 50,
    "MEDIUM": 20
}