from core.queue_manager import get_queue
from data.outgoing_data import save_outgoing

def push_to_front(data: dict):
    save_outgoing(data)
    get_queue().put(data)
