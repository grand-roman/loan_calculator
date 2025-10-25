import requests

API_URL = 'https://www.cbr-xml-daily.ru/daily_json.js'

def fetch_rates() -> dict:
    try:
        resp = requests.get(API_URL)
        resp.raise_for_status()
        data = resp.json()
        if data.get("success", True):
            return data['Valute']
        else:
            raise ValueError("API returned an error")
    except Exception as e:
        raise RuntimeError(f"Failed to fetch rates: {e}")