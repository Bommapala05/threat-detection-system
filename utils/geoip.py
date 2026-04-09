import requests

def get_geo(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5)
        data = res.json()

        return {
            "lat": data.get("lat"),
            "lon": data.get("lon"),
            "country": data.get("country")
        }
    except:
        return None