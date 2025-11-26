# handlers/event_handler.py

def handle_event(event_type: str, ctx: dict):
    """
    event_type: string like 'emergency_vehicle', 'traffic_spike', 'normal'
    ctx: dict with context (intersection_id, total_cars, etc.)
    """
    iid = ctx.get("intersection_id")

    if event_type == "emergency_vehicle":
        print(f"🚑 Emergency vehicle at {iid}")
        return {
            "type": "special_event",
            "event_type": event_type,
            "intersection_id": iid,
        }

    if event_type == "traffic_spike":
        print(f"🚗 Traffic spike at {iid}, total_cars={ctx.get('total_cars')}")
        return {
            "type": "special_event",
            "event_type": event_type,
            "intersection_id": iid,
            "total_cars": ctx.get("total_cars"),
        }

    # For 'normal', 'pedestrian_phase', etc., you might not need special events
    return None
