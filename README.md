# Distributed Chat Application

A distributed chat system implementing **FIFO ordering** for private messages and **Causal ordering** for broadcast messages using UDP transport with reliable delivery.

## Features

- **Distributed Architecture**: Multiple nodes communicating via UDP
- **FIFO Ordering**: Private messages from the same sender arrive in order using Lamport clocks
- **Causal Ordering**: Broadcast messages respect causal dependencies using vector clocks
- **Reliable Delivery**: Automatic retries and acknowledgments for message delivery
- **Duplicate Detection**: Prevents processing of duplicate messages
- **Fault Tolerance**: Handles offline nodes

## Architecture

### Core Components

- **`ChatNode`**: Main node coordinator handling message routing
- **`MessageTransport`**: UDP network layer with reliability features
- **`FIFOHandler`**: Implements FIFO ordering for private messages
- **`CausalHandler`**: Implements causal broadcast

## Quick Start

### Prerequisites
- Python 3.7+
- Windows/Linux/macOS

### Running Multiple Nodes

Open separate terminals and run:

```bash
# Terminal 1 - Node 0 - Port 8000
python main.py 0

# Terminal 2 - Node 1 - Port 8001
python main.py 1

# Terminal 3 - Node 2 - Port 8002
python main.py 2
```

### Usage

Once a node is running, you can:

- Type `b` + Enter for broadcast message
- Type a node ID (0-9) + Enter for private message
- Type your message content
- Use Ctrl+C to stop a node

### Example Session

```
Chat node 0 started on port 8000
Type 'b' for broadcast or enter ID for private message: b
Broadcast message: Hello everyone!
```
```
Chat node 0 started on port 8000
Type 'b' for broadcast or enter ID for private message:
[BROADCAST from Node 0]: Hello everyone!
```

## Message Ordering Algorithms

### FIFO Ordering (Private Messages)

Ensures messages from the same sender are delivered in the order they were sent:

```python
# Sequence-based delivery
while expected_seq in self.buffers[sender_id]:
    deliver_message()
    expected_seq += 1
```

**Example**: If Node 0 sends `[0, "Hello"]` then `[1, "World"]` to Node 1, Node 1 will always display "Hello" before "World".

### Causal Ordering (Broadcast Messages)

Uses vector clocks to ensure causal dependencies are respected:

```python
# Causal delivery condition
if msg_clock[sender] == my_clock[sender] + 1 and
   all(msg_clock[i] <= my_clock[i] for i != sender):
    deliver_message()
```

**Example**: If Node 0 broadcasts `[(1,0,0), "Meeting at 3pm"]` and Node 1 replies `[(1,1,0), "I'll attend"]`, all nodes will receive the meeting announcement before the reply.

## Configuration

See `config.py` to check node addresses:

```python
NODES = [
    ('127.0.0.1', 8000),  # Node 0
    ('127.0.0.1', 8001),  # Node 1
    ('127.0.0.1', 8002),  # Node 2
    # And so on and so forth...
]
```

## Network Protocol

### Message Format

**Broadcast Message:**
```json
{
    "type": "MESSAGE",
    "mode": "broadcast", 
    "id": "node_id-msg_count",
    "sender_id": 0,
    "target_id": null,
    "clock": [1,0,0,0,0,0,0,0,0,0],
    "content": "Hello everyone!"
}
```

**Private Message:**
```json
{
    "type": "MESSAGE",
    "mode": "private", 
    "id": "0-0",
    "sender_id": 0,
    "target_id": 2,
    "clock": null,
    "content": "Hello Node 2!",
    "seq_num": 0
}
```

### Reliability Features

- **Acknowledgments**: Each message requires an ACK
- **Retries**: Failed messages are retried up to 5 times with a 2-s delay or twice with 1sec delay (respectively broadcast and private)
- **Timeouts**: Different timeouts for broadcast vs private messages
- **Duplicate Detection**: Messages are processed exactly once

## Testing

### Manual Testing

1. Start multiple nodes in separate terminals

### Network Simulation

Use `manual_send.py` to inject messages:

```python
python manual_send.py  # Simulates first broadcat message from Node 0
```

## Project Structure

```
Chat_app/
├── chat_node.py           # Main chat node logic
├── network_transport.py   # UDP transport with reliability
├── message_ordering.py    # FIFO and causal ordering algorithms
├── config.py             # Node configuration
├── main.py               # Application entry point
├── manual_send.py        # Testing utility
└── README.md             # This file
```

## Algorithm Details

### Vector Clocks

Each node maintains a vector clock `[0,0,0,...]` where:
- `clock[i]` = number of messages received from node i
- Before sending: increment own position
- On delivery: update clock using `max()` operation

### FIFO Implementation

- **Per-sender buffers**: Messages buffered by sequence number
- **Per-sender Lamport clocks**: Each receiver tracks next expected sequence per sender
- **Sequential delivery**: Only deliver messages with next expected Lamport timestamp
- **Gap handling**: Buffer out-of-order messages until missing ones arrive

### Reliability Protocol

1. **Send** message via UDP
2. **Wait** for acknowledgment (ACK) with timeout
3. **Retry** if no acknowledgment (ACK) received
4. **Report** delivery status

# Team

- Anthony CAO       `@terreclair`
- Mattéo BONNET     `@0zzone`
- Ylan HEBRON       `@grigan_tps`
