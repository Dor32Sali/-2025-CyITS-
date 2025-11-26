import json
from flask import stream_with_context
from core.queue_manager import get_queue

def generate_sse():
    q = get_queue()
    while True:
        event = q.get()
        yield f"data: {json.dumps(event)}\n\n"
