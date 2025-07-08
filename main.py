import sys
import time
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from chat_node import ChatNode
from config import NODES


def main():    
    try:
        node_id = int(sys.argv[1])
        if node_id < 0 or node_id >= len(NODES):
            print(f"Invalid node ID. Must be between 0 and {len(NODES)-1}")
            sys.exit(1)
    except ValueError:
        print("Node ID must be a number")
        sys.exit(1)
    
    my_node = ChatNode(node_id, NODES[node_id][1], NODES)
    my_node.start()
    
    print(f"Chat node {node_id} started on port {NODES[node_id][1]}")
    
    try:
        while True:
            mode = input("\nType 'b' for broadcast or enter ID for private message: ")
            
            if mode == 'b':
                content = input("Broadcast message: ")
                my_node.send_message(content, mode='broadcast')
            elif mode.isdigit():
                target_id = int(mode)
                if 0 <= target_id < len(NODES):
                    content = input(f"Private message to Node {target_id}: ")
                    my_node.send_message(content, mode='private', target_id=target_id)
                else:
                    print("Invalid node ID.")
            else:
                print("Invalid input.")
            
            time.sleep(5)
    except KeyboardInterrupt:
        my_node.stop()


if __name__ == "__main__":
    main()
