
from core.queue_manager import get_queue
from data.outgoing_data import save_outgoing

def push_to_front(event: dict):
    save_outgoing(event)
    get_queue().put(event)
