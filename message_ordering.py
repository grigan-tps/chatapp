class FIFOHandler:
    def __init__(self):
        self.buffers = {}
        self.expected = {}
        self.seen_messages = set()
    
    def handle_message(self, msg_id, sender_id, content, seq_num):
        if msg_id in self.seen_messages:
            print(f"DEBUG: Ignoring duplicate message {msg_id}")
            return []
            
        self.seen_messages.add(msg_id)
        
        if sender_id not in self.buffers:
            self.buffers[sender_id] = {}
            self.expected[sender_id] = 0
        
        self.buffers[sender_id][seq_num] = (msg_id, content)
        delivered = self.deliver_messages(sender_id)
        return delivered
    
    def deliver_messages(self, sender_id):
        expected_seq = self.expected[sender_id]
        delivered = []
        
        while expected_seq in self.buffers[sender_id]:
            msg_id, content = self.buffers[sender_id][expected_seq]
            delivered.append((sender_id, content))
            
            del self.buffers[sender_id][expected_seq]
            self.expected[sender_id] = expected_seq + 1
            expected_seq += 1
        
        return delivered


class CausalHandler:
    def __init__(self, node_id, num_nodes):
        self.node_id = node_id
        self.clock = [0] * num_nodes
        self.buffer = {}
        self.delivered = set()
    
    def handle_message(self, msg_id, sender_id, received_clock, content):
        if msg_id in self.delivered or msg_id in self.buffer:
            print(f"DEBUG: Ignoring duplicated message")
            return []
            
        self.buffer[msg_id] = (sender_id, content, received_clock)
        delivered = self.deliver_messages()
        return delivered
    
    def deliver_messages(self):
        delivered_msgs = []
        delivered_any = True
        
        while delivered_any:
            delivered_any = False
            
            for msg_id, (sender_id, content, msg_clock) in list(self.buffer.items()):
                if self.can_deliver(msg_clock, sender_id):
                    delivered_msgs.append((sender_id, content))
                    
                    for i in range(len(self.clock)):
                        self.clock[i] = max(self.clock[i], msg_clock[i])
                    
                    self.delivered.add(msg_id)
                    del self.buffer[msg_id]
                    delivered_any = True
        
        return delivered_msgs
    
    def can_deliver(self, msg_clock, sender_id):
        for i in range(len(msg_clock)):
            if i == sender_id:
                if msg_clock[i] != self.clock[i] + 1:
                    print(f"DEBUG: Message from {sender_id} with clock {msg_clock} cannot be delivered, BUFFERED")
                    return False
            else:
                if msg_clock[i] > self.clock[i]:
                    print(f"DEBUG: Message received from {sender_id} with clock {msg_clock} cannot be delivered, BUFFERED")
                    return False
        print(f"DEBUG: Message from {sender_id} with clock {msg_clock} can be delivered")
        return True
    
    def increment_clock(self):
        self.clock[self.node_id] += 1
    
    def get_clock(self):
        return self.clock.copy()
