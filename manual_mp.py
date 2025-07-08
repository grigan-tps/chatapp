import socket
import json

message = {
    "type": "MESSAGE",
    "mode": "private",
    "id": "0-0",
    "sender_id": 0,
    "target_id": 1,
    "clock": None,
    "content": "Delayed first message simulated",
    "seq_num": 0
}

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.sendto(json.dumps(message).encode('utf-8'), ('127.0.0.1', 8001))
sock.close()

print("Message sent !")
