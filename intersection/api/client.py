# api/client.py
import requests

class NodeAPIClient:
    def __init__(self, block_brain_url):
        self.base = block_brain_url.rstrip("/")

    def send_telemetry(self, telemetry: dict):
        try:
            url = f"{self.base}/telemetry"
            resp = requests.post(url, json=telemetry, timeout=1.0)

            if resp.status_code == 200:
                return resp.json()
            return None

        except requests.exceptions.RequestException:
            return None
