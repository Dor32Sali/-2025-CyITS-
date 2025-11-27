from flask import Flask, request, jsonify, Response
from flask_cors import CORS

# Local imports
from data.incoming_data import save_incoming
from analisys.validator import validate_snapshot, classify_status
from streams.sse_stream import generate_sse, push_event

server = Flask(__name__)
CORS(server)


# ------------------------
# Health check
# ------------------------
@server.route("/health", methods=["GET"])
def health():
    return {"status": "ok"}


# ------------------------
# Main telemetry ingress
# ------------------------
@server.route("/api/intersection", methods=["POST"])
def intersection():
    try:
        data = request.get_json(force=True)

        if not data:
            return jsonify({"error": "No JSON received"}), 400

        print("▶ Received telemetry:", data, flush=True)

        save_incoming(data)

        anomalies = validate_snapshot(data, prev_snapshot=None)
        status = classify_status(anomalies)

        event_payload = {
            "intersection_id": data.get("intersection_id"),
            "block_id": data.get("block_id"),
            "status": status,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
        }

        push_event(event_payload)

        return jsonify({
            "intersection_id": data.get("intersection_id"),
            "block_id": data.get("block_id"),
            "status": status,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "data": data,
        }), 200

    except Exception as e:
        import traceback
        print("💥 Error in /api/intersection:", e, flush=True)
        traceback.print_exc()
        # ⬇️ VERY IMPORTANT: dict, not set
        return jsonify({"error": str(e)}), 500


# ------------------------
# Optional snapshot endpoint (supports prev_snapshot)
# ------------------------
@server.route("/api/intersection-snapshot", methods=["POST"])
def handle_snapshot():
    """
    Alternate endpoint if you want to POST:
    {
      "snapshot": { ... },
      "prev_snapshot": { ... }   # optional
    }
    instead of sending the raw snapshot only.
    """
    try:
        body = request.get_json(force=True)
        if not body:
            return jsonify({"error": "No JSON received"}), 400

        snapshot = body.get("snapshot", body)   # support both wrapped & raw
        prev = body.get("prev_snapshot")

        # Save current snapshot
        save_incoming(snapshot)

        anomalies = validate_snapshot(snapshot, prev_snapshot=prev)
        status = classify_status(anomalies)

        event_payload = {
            "intersection_id": snapshot.get("intersection_id"),
            "block_id": snapshot.get("block_id"),
            "status": status,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
        }
        push_event(event_payload)

        return jsonify({
            "intersection_id": snapshot.get("intersection_id"),
            "block_id": snapshot.get("block_id"),
            "status": status,
            "anomaly_count": len(anomalies),
            "anomalies": anomalies,
            "data": snapshot,
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ------------------------
# SSE stream for frontend
# ------------------------
@server.route("/events")
def events():
    """
    Server-Sent Events endpoint.

    Frontend example:
      const es = new EventSource('https://<your-ngrok>.ngrok-free.app/events');
      es.onmessage = (event) => console.log(JSON.parse(event.data));
    """
    return Response(generate_sse(), mimetype="text/event-stream")


# ------------------------
# Run server (ngrok exposes this)
# ------------------------
if __name__ == "__main__":
    # Run on 0.0.0.0:5000 so ngrok can forward to it:
    #   ngrok http 5000
    server.run(host="0.0.0.0", port=5000, debug=True, threaded=True)
