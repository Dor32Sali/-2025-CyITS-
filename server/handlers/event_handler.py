def handle_event(event_type: str, data: dict):
    if event_type == "fire":
        print("🔥 Fire detected")
        return {"type": "special_event", "event_type": "fire"}

    if event_type == "traffic_spike":
        print("🚗 Traffic spike detected")
        return {"type": "special_event", "event_type": "traffic_spike"}

    return None