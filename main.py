# main.py
import time
from intersection.simulator.intersection_node import IntersectionNode

NUM_NODES = 10
TELEMETRY_INTERVAL = 1.0

def run_node(node_id):
  
    node = IntersectionNode(
        intersection_id=node_id,
        block_brain_url=" https://casteless-unpatronizable-ephraim.ngrok-free.dev", 
        telemetry_interval=TELEMETRY_INTERVAL
    )
    node.run()

if __name__ == "__main__":
   

    try:
        node_id = "junction-1"
        print(f"Started node {node_id}\n")
        run_node(node_id)

    except KeyboardInterrupt:
        print("Interrupted by user")

    finally:
        print("Stopping node...")
