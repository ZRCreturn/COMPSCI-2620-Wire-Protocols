import struct
from common.utils import recv_message, send_message, check_pwd, hash_pwd
from common.protocol import Protocol

# dict mapping client addr to username
connected_clients = {}

# dict mapping username to password
user_accounts = {}

def handle_new_connection(address):
    print(f"[INFO] Client connected from {address}")
    connected_clients[address] = None
    

def handle_disconnect(client_socket, address):
    if address in connected_clients:
        del connected_clients[address]
    client_socket.close()
    print(f"[INFO] Client disconnected.")


def handle_message(sock, address, msg_type, parsed_obj):
    match msg_type:
        case Protocol.REQ_LOGIN_1:
            username = parsed_obj
            connected_clients[address] = username
            # user exists
            if username in user_accounts:
                send_message(sock, Protocol.RESP_USER_EXISTING, None)
            # user not exists, prompt to create account
            else:
                user_accounts[username] = None
                send_message(sock, Protocol.RESP_USER_NOT_EXISTING, None)
            return
            
        case Protocol.REQ_LOGIN_2:
            pwd = parsed_obj
            username = connected_clients[address]
            # the behavior is creating account 
            if user_accounts[username] is None:
                user_accounts[username] = hash_pwd(pwd)
                # a successful login should response the list of accounts
                send_message(sock, Protocol.RESP_LOGIN_SUCCESS, list(user_accounts.keys()))
            # the behavior is validating account
            else:
                if check_pwd(pwd, user_accounts[username]):
                    send_message(sock, Protocol.RESP_LOGIN_SUCCESS, list(user_accounts.keys()))
                else:
                    send_message(sock, Protocol.RESP_LOGIN_FAILED, None)
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
            msg_type, parsed_obj = recv_message(client_socket)
            if msg_type is None:
                break
            handle_message(client_socket, address, msg_type, parsed_obj)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        handle_disconnect(client_socket, address)
