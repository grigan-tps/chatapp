import time

from network_transport import MessageTransport
from message_ordering import FIFOHandler, CausalHandler


class ChatNode:
    def __init__(self, node_id, my_port, all_nodes):
        self.node_id = node_id
        self.my_port = my_port
        self.all_nodes = all_nodes

        self.transport = MessageTransport(node_id, my_port)
        self.fifo = FIFOHandler()
        self.causal = CausalHandler(node_id, len(all_nodes))
        
        self.transport.set_handler(self.handle_message)
    
    def start(self):
        self.transport.start()
    
    def handle_message(self, packet, addr):
        msg_id = packet['id']
        sender_id = packet['sender_id']
        received_clock = packet['clock']
        content = packet['content']
        mode = packet['mode']

        if mode == 'private':
            delivered = self.fifo.handle_message(msg_id, sender_id, content, packet.get('seq_num', 0))
            for sender, msg_content in delivered:
                print(f"\n[MP from Node {sender}]: {msg_content}\n")
        else:
            delivered = self.causal.handle_message(msg_id, sender_id, received_clock, content)
            for sender, msg_content in delivered:
                print(f"\n[BROADCAST from Node {sender}]: {msg_content}\n")

    def send_message(self, content, mode='broadcast', target_id=None):
        if mode == 'broadcast':
            self.causal.increment_clock()
            clock = self.causal.get_clock()
        else:
            clock = None
        
        packet = self.transport.create_packet(content, mode, target_id, clock)

        
        if mode == 'broadcast':
            recipients = [node for i, node in enumerate(self.all_nodes) if i != self.node_id]
            self.transport.send_message(packet, recipients,)
        elif mode == 'private' and target_id is not None:
            if target_id != self.node_id:
                recipient = self.all_nodes[target_id]
                self.transport.send_message(packet, [recipient])
        else:
            print("Error: Invalid message mode or target")
    
    def stop(self):
        self.transport.stop()
