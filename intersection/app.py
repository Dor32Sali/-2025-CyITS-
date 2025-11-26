from flask import Flask, jsonify
import os
import socket

app = Flask(__name__)

INTERSECTION_ID = os.getenv("INTERSECTION_ID", "I_UNKNOWN")
BLOCK_ID = os.getenv("BLOCK_ID", "BLOCK_UNKNOWN")


@app.route("/status", methods=["GET"])
def status():
    # TODO: later: add real simulated cars/people/sensors
    data = {
        "intersection_id": INTERSECTION_ID,
        "block_id": BLOCK_ID,
        "cars": 0,
        "people": 0,
        "sensor_ok": True,
        "power_ok": True,
        "health": "OK",
        "hostname": socket.gethostname(),
    }
    return jsonify(data)


@app.route("/ping", methods=["GET"])
def ping():
    return jsonify({"msg": "intersection alive", "intersection_id": INTERSECTION_ID})


if __name__ == "__main__":
    # For local testing without Docker
    app.run(host="0.0.0.0", port=8000)
