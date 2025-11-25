from flask import Flask, jsonify
import os
import socket
import requests

app = Flask(__name__)

BLOCK_ID = os.getenv("BLOCK_ID", "BLOCK_UNKNOWN")
# Comma-separated list of intersection service URLs, e.g. "http://intersection_i1:8000,http://intersection_i2:8000"
INTERSECTION_URLS = os.getenv("INTERSECTION_URLS", "")


def get_intersection_status(url: str):
    try:
        resp = requests.get(f"{url}/status", timeout=1.0)
        resp.raise_for_status()
        return {"url": url, "ok": True, "data": resp.json()}
    except Exception as e:
        return {"url": url, "ok": False, "error": str(e)}


@app.route("/summary", methods=["GET"])
def summary():
    urls = [u.strip() for u in INTERSECTION_URLS.split(",") if u.strip()]
    results = [get_intersection_status(u) for u in urls]

    # TODO: later: add anomaly detection, neighbor consistency, etc.
    data = {
        "block_id": BLOCK_ID,
        "hostname": socket.gethostname(),
        "intersections": results,
    }
    return jsonify(data)


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"msg": "block controller alive", "block_id": BLOCK_ID})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8001)
