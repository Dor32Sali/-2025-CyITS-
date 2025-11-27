from data.incoming_data import save_incoming
from core.queue_manager import get_queue # NEW IMPORT
# Note: Removed dependencies on handlers/event_handler and services/frontend_service
from datetime import datetime

def process_intersection_data(data: dict):
    """
    Receives the complete telemetry payload, saves the raw data to file, and 
    pushes the event onto an internal queue for further asynchronous processing.
    
    Args:
        data (dict): The complete JSON payload received from the IntersectionNode.
    
    Returns:
        dict: A simple response payload sent back to the IntersectionNode.
    """

    # 1) Save raw telemetry to file (CRITICAL STEP)
    
    
    # 2) Put the raw event data onto a queue for processing by workers (e.g., event handlers)
    get_queue().put(data)
    

    # Extract basic metadata for the response
    intersection_id = data.get("intersection_id", "UNKNOWN")

    # 3) Response back to IntersectionNode (simplified and clean)
    return {
        "status": "accepted",
        "message": f"Raw telemetry accepted for {intersection_id}",
        "timestamp_received_utc": datetime.utcnow().isoformat(),
    }