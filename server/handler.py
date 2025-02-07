import struct
import threading
from common.protocol import Protocol

connected_clients = []

def handle_new_connection(client_socket, address):
    print(f"[INFO] Client connected from {address}")
    connected_clients.append(client_socket)
    

def handle_disconnect(client_socket):
    if client_socket in connected_clients:
        connected_clients.remove(client_socket)
    client_socket.close()
    print(f"[INFO] Client disconnected.")

def handle_message(msg_type, parsed_obj):
    match msg_type:
        case 1:
            pass
        case 2:
            pass
        case _:
            pass

def recv_message(sock):
    # receive 12 bytes header
    header = sock.recv(12)
    if len(header) < 12:
        return None, None

    # parse header
    msg_type, data_len = struct.unpack("!QI", header)

    # read payload
    payload = b""
    while len(payload) < data_len:
        chunk = sock.recv(data_len - len(payload))
        if not chunk:
            return None, None 
        payload += chunk

    obj = Protocol.decode_obj(payload)
    return msg_type, obj


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
            handle_message(msg_type, parsed_obj)
    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        handle_disconnect(client_socket)
