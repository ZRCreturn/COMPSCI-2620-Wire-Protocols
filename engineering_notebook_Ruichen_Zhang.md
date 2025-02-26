# Engineering Notebook

## February 3: Designing the Message Protocol

Before diving into coding, I believe the most crucial step is to clearly define the communication protocol. Since the client and server communicate via TCP sockets by transmitting byte streams, the core challenge lies in determining the message format.

One of the most elegant concepts in computing is **metadata**, or headers. A good design practice here is to structure every message as **metadata + payload**, where the payload contains the actual data in a byte stream. The metadata should include essential information required by the protocol. 

First, since client-server communication relies purely on sockets—unlike modern web apps that leverage structured APIs—the **message type (msg_type)** must be explicitly defined to distinguish different requests and responses. Second, the metadata should include the **payload length**, making it easier to parse messages efficiently.

Based on this, the final message format is as follows:

```
General Message Structure:
    int64       msg_type  = xxx
    uint32      data_len  = length of payload
    # The above metadata occupies 12 bytes
    bytes       payload   = serialized object

Login Requests:
    msg_type = 1
    data_len = length of payload
    payload = user_name (string)

    msg_type = 2
    data_len = length of payload
    payload = user_password (string)

...

# Define msg_type >= 100 as reply messages
Reply Messages:
    msg_type = 100
    data_len = length of payload
    payload = error_message (string)

    msg_type = 101
    data_len = 0
    payload = null
...
```

---

## February 4: Implementing Serialization & Deserialization

Today, I primarily worked on refining the protocol design, with a key challenge being the serialization and deserialization of transmitted messages. Given Python's flexibility in handling core data types, I decided to implement a **universal encoding and decoding method**. This approach ensures that the system remains extensible regardless of future design changes.

The implementation covers fundamental data types: `int`, `str`, `list`, and `dict`. Given the nature of `list` and `dict`, recursion is the most intuitive way to process them.

The implementation proceeded smoothly, as expected, leveraging recursion:

```python
import struct

def encode_obj(obj):
    """
    Serializes Python objects into a byte stream.
    """
    if isinstance(obj, int):
        # Define int as type 0x00 + 8-byte signed integer
        return b'\x00' + struct.pack('!q', obj)

    elif isinstance(obj, str):
        # Define str as type 0x01 + 4-byte length + UTF-8 encoded byte array
        data = obj.encode('utf-8')
        length = len(data)
        return b'\x01' + struct.pack('!I', length) + data

    elif isinstance(obj, list):
        # Define list as type 0x02 + 4-byte size + encode_obj(elements)
        encoded_items = [encode_obj(item) for item in obj]
        total = b''.join(encoded_items)
        return b'\x02' + struct.pack('!I', len(obj)) + total

    elif isinstance(obj, dict):
        # Define dict as type 0x03 + 4-byte size + encode_obj(key) + encode_obj(value)
        # Keys are required to be strings
        encoded_items = []
        for k, v in obj.items():
            encoded_key = encode_obj(str(k))
            encoded_value = encode_obj(v)
            encoded_items.append(encoded_key + encoded_value)
        total = b''.join(encoded_items)
        return b'\x03' + struct.pack('!I', len(obj)) + total

    else:
        raise TypeError(f"Unsupported type: {type(obj)}")
```

---

## February 5: Designing the Framework

Today, I focused on designing the overall project framework and structuring the file directory. The **server-side** was decomposed into modular components, and a `common` directory was introduced to store shared utilities.

### **Project Structure:**
```
project_root/
│── server/
│   ├── main.py          # Entry point for server execution
│   ├── handler.py       # Core logic for handling client requests
│   ├── config.py        # Server configuration parameters
│   ├── __init__.py
│
│── common/
│   ├── protocol.py      # Implementation of message protocol encoding & decoding
│   ├── utils.py         # Helper functions for logging, error handling, etc.
│   ├── __init__.py
│
│── client/
│   ├── main.py          # Client-side entry point
│   ├── __init__.py
│
│── tests/               # Unit tests
│── README.md            # Project documentation
│── requirements.txt     # Dependencies
```

### **Key Components:**
- **`handler.py`**: Handles incoming messages from clients, dispatching them to the appropriate processing functions.
- **`protocol.py`**: Defines the serialization and deserialization logic for message encoding and decoding.
- **`utils.py`**: Contains utility functions for logging, error handling, and debugging.

that's how I design the framework 
```
Class Server:
    Initialize host and port
    Create a TCP socket, bind to (host, port), and listen for connections

    Method start():
        Loop:
            Accept incoming client connection
            Start a new thread to handle client communication


Class ClientHandler:
    Maintain:
        - connected_clients {address: username}
        - user_accounts {username: password}
        - message_store {msg_id: Message}
        - messages {recipient: {sender: deque([msg_id1, msg_id2, ...])}}

    Method handle(client_socket, address):
        Store client connection info
        Loop:
            Receive (msg_type, parsed_obj)
            If no message, break loop
            Process request based on msg_type
        Close connection

    Method process_request(sock, address, msg_type, parsed_obj):
        Case REQ_LOGIN_
            
        Case REQ_SEND_MSG:

        Case REQ_READ_MSG:

        Case REQ_LIST_MESSAGES:

        Case REQ_LIST_USERS:

        Case REQ_DELETE_MESSAGE:

        Case REQ_DELETE_ACCOUNT:


```

### **Next Steps (TODO):**
- Implement the core logic inside `handler.py` to process different message types.
- Finalize the `protocol.py` encoding/decoding implementation.
- Develop the client-side request structure in `request.py`.
- Set up unit tests to validate message transmission.


## February 7: Thoughts on Designing the Login System

When handling user login, a key consideration is managing connections and usernames. In typical web applications, authentication is often handled using JWT tokens or storing session IDs in cookies. However, since this project relies solely on sockets for communication between the client and server, it requires a custom approach to managing and storing connection and account information.

My initial thought is to use a **global map** to maintain the mapping between **connection addresses** and **usernames**. This mapping would be dynamically updated in the following scenarios:
- **When a client connects**: A new entry is created in the map.
- **Upon login**: The username is associated with the connection.
- **Upon logout**: The mapping is removed.
- **When a connection is lost**: The corresponding entry is cleaned up.

This design ensures that the server can efficiently track active users and manage authentication without relying on an external session store.

Today finish most part of the business logic
### **Next Steps (TODO):**
- finish business logic of handling all kinds of message.
- finish test suits


## February 9: Debugging Import Issues in Python

While running the code, I encountered the following error:

```
from server.handler import client_thread_entry
ModuleNotFoundError: No module named 'server.handler'; 'server' is not a package
```

I wasn't entirely clear on Python's import mechanism. I tried adding `__init__.py` and several other fixes, but they didn’t resolve the issue. Eventually, I discovered that running the script with the `-m` flag as a module resolved the problem:

```
python -m server.server
```

This approach ensures that Python treats the script as a module, searching for it correctly within `sys.path` before executing it. The deeper details of Python’s import mechanism are something I'll explore further in the future.

### **Next Steps (TODO):**
- Organize all the code and ensure a clean structure.
- Write documentation for the project.



## February 10: Adding Locks for Global Variable Modification

To ensure thread safety when modifying global variables related to `send`, `read`, and `delete` message operations, I added locks. In Python, thanks to the **context manager**, using locks becomes very **Pythonic**—simply wrapping critical sections with `with lock` ensures proper locking and unlocking.

This approach makes concurrency management much more convenient and readable.



## February 21: Refactoring the Server Backend with RPC

Today, I researched refactoring the server backend using RPC. Thanks to the well-structured code from previous iterations, the **business logic** was already encapsulated within the `handler` file. Each specific operation was also wrapped within dedicated functions, making the transition to RPC straightforward.

For instance, the existing request handling structure follows this pattern:

```python
def process_request(sock, address, msg_type, parsed_obj):
    match msg_type:
        case REQ_LOGIN_:
            # Extract relevant parameters
            xxx, xxx, ... = parsed_obj
            # Call the corresponding business function
            login(xxx, xxx, ...)

        case REQ_SEND_MSG:
        case REQ_READ_MSG:
        case REQ_LIST_MESSAGES:
        case REQ_LIST_USERS:
        case REQ_DELETE_MESSAGE:
        case REQ_DELETE_ACCOUNT:
```

This structure makes implementing the corresponding RPC interface on the server simple—**just import the original handler functions**:

```python
def Login(self, request, context):
    # Extract relevant parameters
    xxx = request.xxx
    # Call the corresponding business function
    login(xxx, xxx, ...)
```

This should make the implementation process **smooth and efficient**.

---

## February 22: Implementing the Proto File

Today, I worked on implementing the **proto file**, which turned out to be **straightforward**—it was simply a matter of converting the previously defined protocol details into **message types**.

One notable advantage of using RPC over a custom protocol is **clarity and standardization**. Our custom protocol defined a general serialization method for Python's common data types (`int`, `float`, `str`, `list`, `dict`). However, the actual communication **rules** weren't always explicit in the code. 

For example, in our custom protocol, sending a message required transmitting a **list of length 2**, where:
1. The first element was the recipient.
2. The second element was the message content.

This rule had to be **documented separately**, making communication between the frontend and backend **less standardized**.

With **RPC**, we simply define the message in the proto file:

```proto
message SendMessageRequest {
  string sender = 1;     
  string recipient = 2;
  string content = 3;
}
```

This approach is **much more intuitive and structured**, reducing the communication overhead between frontend and backend.

### **Next Steps (TODO):**
- Complete the remaining implementation based on the outlined approach.

---

## February 23: Completing the Refactor

As expected, the refactor was **straightforward**—the entire business logic transition to RPC was completed in just **one hour**.

## Answer to Key Questions

### **Does the use of this tool make the application easier or more difficult?**
It makes the application **easier**. As mentioned earlier, it reduces communication overhead between the frontend and backend. Additionally, we no longer need to implement our own serialization and deserialization mechanisms or manually manage TCP socket connections.

### **What does it do to the size of the data passed?**
The data size **increases** due to the following reasons:
1. **Protobuf Overhead**: gRPC uses **Protobuf** for serialization, which is more structured and complex than our custom protocol. Our previous approach only added two metadata fields (`type` and `length`) when converting objects to byte streams, making it relatively lightweight.
2. **HTTP/2 Overhead**: gRPC operates over **HTTP/2**, which introduces additional overhead, including headers, flow control mechanisms (e.g., **streaming, flow control, and header compression**), and other protocol-level features. This makes gRPC slightly heavier compared to a raw **TCP + custom protocol** approach.

### **How does it change the structure of the client? The server?**
The **client** is handled by my teammate, so further details can be found in his notebook.

For the **server**, this was discussed in detail in the previous engineering notebook entries. In short, gRPC **modularizes** the server structure, making it easier to handle various request types using well-defined APIs.

### **How does this change the testing of the application?**
Testing is **significantly simplified**. Previously, without an API interface, we had to **simulate frontend requests within the code**, manually parse server responses, and verify if they met expectations. With **gRPC**, we can now directly test the API endpoints, making the tests **more independent and standardized**.