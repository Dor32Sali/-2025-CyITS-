from data.incoming_data import save_incoming
from handlers.event_handler import handle_event
from services.frontend_service import push_to_front

def process_intersection_data(data: dict):
    save_incoming(data)

    event_type = data.get("event_type")
    special = handle_event(event_type, data)

    if special:
        push_to_front(special)

    normal = {
        "type": "normal_event",
        "id": data.get("id"),
        "features": data.get("features", []),
    }

    push_to_front(normal)

    return {"status": "accepted"}
