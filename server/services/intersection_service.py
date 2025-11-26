# services/intersection_service.py
from data.incoming_data import save_incoming
from handlers.event_handler import handle_event
from services.frontend_service import push_to_front


def process_intersection_data(data: dict):
    """
    Telemetry example from IntersectionNode:

    {
      "intersection_id": "junction-1",
      "timestamp": 1732639091,
      "phase": {"N": "GREEN", "S": "GREEN", "E": "RED", "W": "RED"},
      "cars": {"north": 3, "south": 1, "east": 0, "west": 5},
      "pedestrians_waiting": false,
      "emergency_vehicle": false
    }
    """

    # 1) Save raw telemetry to file
    save_incoming(data)

    intersection_id = data.get("intersection_id")
    timestamp = data.get("timestamp")
    phase = data.get("phase", {}) or {}
    cars = data.get("cars", {}) or {}
    pedestrians_waiting = bool(data.get("pedestrians_waiting"))
    emergency_vehicle = bool(data.get("emergency_vehicle"))

    # total car count
    if isinstance(cars, dict):
        total_cars = sum(cars.values())
    else:
        total_cars = 0

    # 2) Derive event_type based on telemetry
    if emergency_vehicle:
        event_type = "emergency_vehicle"
    elif total_cars > 40:
        event_type = "traffic_spike"
    elif pedestrians_waiting:
        event_type = "pedestrian_waiting"
    else:
        event_type = "normal"

    # Context for handlers + frontend
    ctx = {
        "intersection_id": intersection_id,
        "timestamp": timestamp,
        "phase": phase,
        "cars": cars,
        "total_cars": total_cars,
        "pedestrians_waiting": pedestrians_waiting,
        "emergency_vehicle": emergency_vehicle,
        "raw": data,
    }

    # 3) Special backend events (alerts, logs, etc.)
    special_payload = handle_event(event_type, ctx)
    if special_payload is not None:
        push_to_front(special_payload)

    # 4) Normal event message for frontend via SSE
    normal_payload = {
        "type": "normal_event",
        "event_type": event_type,
        **ctx,
    }
    push_to_front(normal_payload)

    # 5) Response back to IntersectionNode
    return {
        "status": "accepted",
        "intersection_id": intersection_id,
        "event_type": event_type,
        "total_cars": total_cars,
    }
