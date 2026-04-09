import requests
from config import OTX_API_KEY

def fetch_otx_iocs():
    url = "https://otx.alienvault.com/api/v1/indicators/export"
    headers = {"X-OTX-API-KEY": OTX_API_KEY}

    try:
        res = requests.get(url, headers=headers, timeout=10)
        data = res.json()
        return data
    except Exception as e:
        print("OTX Fetch Failed:", e)
        return None