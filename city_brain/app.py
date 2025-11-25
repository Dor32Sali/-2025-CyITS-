from flask import Flask, jsonify
import os
import socket
import requests

app = Flask(__name__)

# Comma-separated list of block controller URLs, e.g. "http://block_a:8001,http://block_b:8001"
BLOCK_URLS = os.getenv("BLOCK_URLS", "")


def get_block_summary(url: str):
    try:
        resp = requests.get(f"{url}/summary", timeout=1.5)
        resp.raise_for_status()
        return {"url": url, "ok": True, "data": resp.json()}
    except Exception as e:
        return {"url": url, "ok": False, "error": str(e)}


@app.route("/city_view", methods=["GET"])
def city_view():
    urls = [u.strip() for u in BLOCK_URLS.split(",") if u.strip()]
    results = [get_block_summary(u) for u in urls]

    # TODO: later: build graph, run GNN, anomaly detection, etc.
    data = {
        "hostname": socket.gethostname(),
        "blocks": results,
    }
    return jsonify(data)


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"msg": "city brain alive"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8002)
