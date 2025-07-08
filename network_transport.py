import socket
import threading
import time
import json


class MessageTransport:
    def __init__(self, node_id, my_port):
        self.node_id = node_id
        self.my_port = my_port
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('127.0.0.1', my_port))
        self.acks = set()
        self.msg_count = 0
        self.handler = None
        self.running = False
        self.broadcast_responses = {}
    
    def set_handler(self, handler):
        self.handler = handler
    
    def start(self):
        if not self.running:
            self.running = True
            threading.Thread(target=self.listen, daemon=True).start()
    
    def listen(self):
        while self.running:
            try:
                data, addr = self.socket.recvfrom(4096)
                packet = json.loads(data.decode('utf-8'))
                if packet['type'] == 'MESSAGE':
                    if self.handler:
                        self.handler(packet, addr)
                    self.send_ack(addr, packet['id'])
                elif packet['type'] == 'ACK':
                    msg_id = packet['ack_id']
                    self.acks.add(msg_id)
                    
                    if msg_id in self.broadcast_responses:
                        self.broadcast_responses[msg_id]['received'] += 1
            except:
                continue
    
    def send_ack(self, addr, msg_id):
        ack_packet = {
            'type': 'ACK',
            'ack_id': msg_id
        }
        encoded = json.dumps(ack_packet).encode('utf-8')
        self.socket.sendto(encoded, addr)
    
    def send_message(self, packet, recipients):
        encoded = json.dumps(packet).encode('utf-8')
        msg_id = packet['id']
        is_broadcast = packet['mode'] == 'broadcast'
        
        if is_broadcast:
            self.broadcast_responses[msg_id] = {
                'expected': len(recipients),
                'received': 0,
                'nodes': [r[1] for r in recipients]
            }
        
        for recipient in recipients:
            try:
                self.socket.sendto(encoded, recipient)
                threading.Thread(target=self.wait_for_ack, args=(msg_id, encoded, recipient, is_broadcast), daemon=True).start()
            except Exception as e:
                print(f"Error sending to {recipient}: {e}")
        
        if is_broadcast:
            threading.Thread(target=self.report_broadcast_status, args=(msg_id,), daemon=True).start()
    
    def report_broadcast_status(self, msg_id):
        time.sleep(3)
        if msg_id in self.broadcast_responses:
            info = self.broadcast_responses[msg_id]
            print(f"Broadcast delivered to {info['received']}/{info['expected']+1} nodes.\n")
            del self.broadcast_responses[msg_id]
    
    def wait_for_ack(self, msg_id, encoded, node, is_broadcast=False):
        max_retries = 2 if is_broadcast else 5
        sleep_time = 1 if is_broadcast else 2
        
        retries = 0
        while retries < max_retries:
            time.sleep(sleep_time)
            if msg_id in self.acks:
                return
            try:
                self.socket.sendto(encoded, node)
            except Exception as e:
                print(f"Error sending to {node}: {e}")
                return
            retries += 1
        
        if is_broadcast:
            print(f"Node {node[1]} did not respond to broadcast (may be offline)")
        else:
            print(f"Private message {msg_id} not acknowledged after {max_retries} retries.")
    
    def create_packet(self, content, mode, target_id=None, clock=None):
        msg_id = f"{self.node_id}-{self.msg_count}"
        self.msg_count += 1
        
        packet = {
            'type': 'MESSAGE',
            'mode': mode,
            'id': msg_id,
            'sender_id': self.node_id,
            'target_id': target_id,
            'clock': clock,
            'content': content
        }
        
        if mode == 'private':
            packet['seq_num'] = self.msg_count - 1
        
        return packet
    
    def stop(self):
        self.running = False
        self.socket.close()
