import json
from core.queue_manager import get_queue

_q = get_queue()

def push_event(event: dict):
    # Safety guard
    if isinstance(event, set):
        raise TypeError("push_event received a set instead of a dict")
    _q.put(event)

def generate_sse():
    while True:
        event = _q.get()
        # Debug if needed:
        # print("SSE event:", event, type(event), flush=True)
        yield f"data: {json.dumps(event)}\n\n"