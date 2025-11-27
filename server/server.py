from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Local imports
from data.incoming_data import save_incoming
from streams.sse_stream import generate_sse

server = Flask(__name__)
CORS(server)

# ------------------------
# Health check
# ------------------------
@server.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}

# ------------------------
# Receive telemetry JSON
# ------------------------
@server.route("/api/intersection", methods=["POST"])
def intersection():
    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        # Save raw JSON to file
        save_incoming(data)

        return jsonify({"status": "received"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# ------------------------
# SSE stream
# ------------------------
@server.route("/events")
def events():
    return Response(generate_sse(), mimetype="text/event-stream")

# ------------------------
# Run server
# ------------------------
if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000, debug=True, threaded=True)