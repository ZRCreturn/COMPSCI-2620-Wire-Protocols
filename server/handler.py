from collections import deque, defaultdict
from common.utils import recv_data, send_data, check_pwd, hash_pwd
from common.protocol import Protocol
from common.message import Chatmsg

# dict mapping client addr to username
connected_clients = {}

# dict mapping username to password
user_accounts = {}

# global message store 
message_store = {}  # {msg_id: Message}
messages = defaultdict(lambda: defaultdict(deque))  # {sender: {recipient: deque([msg_id1, msg_id2, ...])}}


def handle_new_connection(address):
    print(f"[INFO] Client connected from {address}")
    connected_clients[address] = None
    

def handle_disconnect(client_socket, address):
    if address in connected_clients:
        del connected_clients[address]
    client_socket.close()
    print(f"[INFO] Client disconnected.")


def send_message(sender, recipient, content):
    """ send message:
    - online user:directly send messages
    - offline user: store into undelivered_messages
    """
    msg = Chatmsg(sender, recipient, content)
    message_store[msg.id] = msg  # global storage for messages

    messages[recipient][sender].append(msg.id)
    
    if recipient in connected_clients.values():  # if recipient is online
        print(f"✅ Message delivered to {recipient}")
        msg.status = 'read'
    else:  # recipient is offline
        print(f"📩 {recipient} is offline. Message stored for later delivery.")


def read_messages(sender, recipient):

    if recipient not in messages or sender not in messages[recipient]:
        print(f"🚫 No messages from {sender} to {recipient}.")

    message_ids = list(messages[recipient][sender])

    for msg_id in message_ids:
        if msg_id in message_store:
            message_store[msg_id].status = "read"

def list_messages(sender, recipient):
    pass


def handle_request(sock, address, msg_type, parsed_obj):
    match msg_type:
        case Protocol.REQ_LOGIN_1:
            username = parsed_obj
            connected_clients[address] = username
            # user exists
            if username in user_accounts:
                send_data(sock, Protocol.RESP_USER_EXISTING, None)
            # user not exists, prompt to create account
            else:
                user_accounts[username] = None
                send_data(sock, Protocol.RESP_USER_NOT_EXISTING, None)
            return
            
        case Protocol.REQ_LOGIN_2:
            pwd = parsed_obj
            username = connected_clients[address]
            # the behavior is creating account 
            if user_accounts[username] is None:
                user_accounts[username] = hash_pwd(pwd)
                # a successful login should response the list of accounts
                send_data(sock, Protocol.RESP_LOGIN_SUCCESS, list(user_accounts.keys()))
            # the behavior is validating account
            else:
                if check_pwd(pwd, user_accounts[username]):
                    send_data(sock, Protocol.RESP_LOGIN_SUCCESS, list(user_accounts.keys()))
                else:
                    send_data(sock, Protocol.RESP_LOGIN_FAILED, None)
            return
                
        case Protocol.REQ_SEND_MSG:
            recipient, content = parsed_obj
            username = connected_clients[address]
            send_message(sender=username, recipient=recipient, content=content)
            return 
        
        case Protocol.REQ_READ_MSG:
            sender = parsed_obj
            username = connected_clients[address]
            read_messages(sender=sender, recipient=username)
            return 
        
        case Protocol.LIST_MESSAGES:


            return

        case _:
            pass



def client_thread_entry(client_socket, address):
    """
    entry for each thread listening to a client
    """
    handle_new_connection(client_socket, address)

    try:
        while True:
            msg_type, parsed_obj = recv_data(client_socket)
            if msg_type is None:
                break
            handle_request(client_socket, address, msg_type, parsed_obj)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        handle_disconnect(client_socket, address)
