from collections import deque, defaultdict
import threading
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

lock = threading.Lock()

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
    with lock:
        msg = Chatmsg(sender, recipient, content)
        message_store[msg.id] = msg  # global storage for messages

        messages[recipient][sender].append(msg.id)
        
        if recipient in connected_clients.values():  # if recipient is online
            print(f"✅ Message delivered to {recipient}")
            msg.status = 'read'
        else:  # recipient is offline
            print(f"📩 {recipient} is offline. Message stored for later delivery.")


def read_messages(sender, recipient):
    with lock:
        if recipient not in messages or sender not in messages[recipient]:
            print(f"🚫 No messages from {sender} to {recipient}.")
            return

        message_ids = list(messages[recipient][sender])

        for msg_id in message_ids:
            if msg_id in message_store:
                message_store[msg_id].status = "read"

def list_messages(username, friend):
    ret = []
    for msg in message_store.values():
        # my message to this friend 
        if msg.sender == username and msg.recipient == friend:
            ret.append(msg)
        # this frind's message to me
        if msg.sender == friend and msg.recipient == username:
            ret.append(msg)
    
    # sort mseeage by time
    sorted(ret, key= lambda msg : msg.timestamp)
    return ret

def list_users(username):
    unread_msg_cnt = {}
    for sender in user_accounts.keys():
        msg_queue = messages[username][sender]
        count = 0
        for msg_id in msg_queue:
            msg = message_store[msg_id]
            if msg.status == "unread":
                count += 1
        unread_msg_cnt[sender] = count
    
    return unread_msg_cnt

def delete_message(username, msg_id):
    with lock:
        if msg_id in message_store:
            recipient = message_store[msg_id].recipient
            del message_store[msg_id]

            messages[recipient][username].remove(msg_id)
            print(f"🗑️ Deleted message {msg_id} from {username} to {recipient}")

def delete_account(username):
    with lock:
        if username in user_accounts:
            del user_accounts[username]
        if username in messages:
            for sender in list(messages[username].keys()):  # iterate message this user received
                for msg_id in messages[username][sender]: 
                    if msg_id in message_store:
                        del message_store[msg_id]   
            del messages[username] 

        for recipient in list(messages.keys()):  # iterate message this user sended
            if username in messages[recipient]:  # if user is sender
                for msg_id in messages[recipient][username]: 
                    if msg_id in message_store:
                        del message_store[msg_id]
                del messages[recipient][username]  # 删除 user 作为 sender 的消息

                if not messages[recipient]:  # 如果 recipient 的消息都删光了，删除 recipient 记录
                    del messages[recipient]

        print(f"❌ {username} has been deleted.")


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
        
        case Protocol.REQ_LIST_MESSAGES:
            friend = parsed_obj
            username = connected_clients[address]
            resp_list = list_messages(username, friend)
            send_data(sock, Protocol.RESP_LIST_MESSAGES, resp_list)
            return

        case Protocol.REQ_LIST_USERS:
            username = connected_clients[address]
            resp_list = list_users(username)
            send_data(sock, Protocol.RESP_LIST_USERS, resp_list)
            return
        
        case Protocol.REQ_DELETE_MESSAGE:
            msg_id = parsed_obj
            username = connected_clients[address]
            delete_message(username, msg_id)
            return
        
        case Protocol.REQ_DELETE_ACCOUNT:
            username = connected_clients[address]
            delete_account(username)
            return

        case _:
            pass



def client_thread_entry(client_socket, address):
    """
    entry for each thread listening to a client
    """
    handle_new_connection(address)

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
