import json
import struct
import bcrypt
from common.protocol import Protocol
from common.message import Chatmsg

def recv_data(sock):
    # receive 12 bytes header
    header = sock.recv(12)
    if len(header) < 12:
        return None, None

    # parse header
    msg_type, data_len = struct.unpack("!QI", header)

    if data_len == 0:
        return msg_type, None
    
    # read payload
    payload = b""
    while len(payload) < data_len:
        chunk = sock.recv(data_len - len(payload))
        if not chunk:
            return None, None 
        payload += chunk

    obj, _ = Protocol.decode_obj(payload)
    return msg_type, obj

def send_data(sock, msg_type, data):
    if data is None:
        payload = b""
    else:
        payload = Protocol.encode_obj(data)
    data_len = len(payload)
    header = struct.pack('!QI', msg_type, data_len)
    sock.sendall(header + payload)    

def hash_pwd(password):
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode(), salt)
    return hashed.decode()  

def check_pwd(password, hashed_password):
    return bcrypt.checkpw(password.encode(), hashed_password.encode())    

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Chatmsg):
            return obj.__dict__
        return super().default(obj)

def send_data_json(sock, msg_type, data):
    if data is None:
        payload = b""
    else:
        payload = json.dumps(data, cls=CustomJSONEncoder).encode('utf-8')

    data_len = len(payload)
    header = struct.pack('!QI', msg_type, data_len)
    sock.sendall(header + payload)

def decode_json(obj):
    if isinstance(obj, dict) and "sender" in obj and "message" in obj:
        return Chatmsg(**obj)  
    elif isinstance(obj, list):
        return [decode_json(item) for item in obj] 
    return obj  

def recv_data_json(sock):
    header = sock.recv(12)
    if len(header) < 12:
        return None, None

    msg_type, data_len = struct.unpack("!QI", header)

    if data_len == 0:
        return msg_type, None
    
    payload = b""
    while len(payload) < data_len:
        chunk = sock.recv(data_len - len(payload))
        if not chunk:
            return None, None 
        payload += chunk

    try:
        obj = json.loads(payload.decode('utf-8'))
        obj = decode_json(obj)  
    except json.JSONDecodeError:
        return None, None  

    return msg_type, obj