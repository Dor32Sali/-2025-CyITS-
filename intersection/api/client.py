# api/client.py
import requests


class NodeAPIClient:
    def __init__(self, block_brain_url: str):
        # base can be "http://localhost:5000" or your ngrok URL
        self.base = block_brain_url.rstrip("/")

    def send_telemetry(self, telemetry: dict):
        """
        Send telemetry from IntersectionNode to the block-brain server.

        Your server has:
        POST /api/intersection
        """
        url = f"{self.base}/api/intersection"
        try:
            resp = requests.post(url, json=telemetry, timeout=2.0)

            if resp.status_code == 200:
                try:
                    data = resp.json()
                except ValueError:
                    # no JSON body
                    return None

                # Optional: debug print – you can remove later
                print(f"[NodeAPIClient] Sent telemetry OK -> {data}")
                return data

            # Non-200 response
            print(f"[NodeAPIClient] Server error {resp.status_code} for {url}")
            return None

        except requests.exceptions.RequestException as e:
            print(f"[NodeAPIClient] Error sending telemetry to {url}: {e}")
            return None