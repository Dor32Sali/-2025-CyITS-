from flask import Flask, request, jsonify, Response
from flask_cors import CORS

from config import HOST, PORT
from streams.sse_stream import generate_sse
from services.intersection_service import process_intersection_data

server = Flask(__name__)
CORS(server)

@server.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

@server.route("/api/intersection", methods=["POST"])
def intersection():
    data = request.get_json(force=True)
    result = process_intersection_data(data)
    return jsonify(result)

@server.route("/events")
def events():
    return Response(generate_sse(), mimetype="text/event-stream")

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000, debug=False, threaded=True)
