import socket
import json
from config import NODES

message = {
    "type": "MESSAGE",
    "mode": "broadcast", 
    "id": "0-0",
    "sender_id": 0,
    "target_id": None,
    "clock": [1,0,0,0,0,0,0,0,0,0],
    "content": "Delayed first message simulated"
}

for i, port in enumerate(NODES):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.sendto(json.dumps(message).encode('utf-8'), (port))
sock.close()

print("Message sent !")
