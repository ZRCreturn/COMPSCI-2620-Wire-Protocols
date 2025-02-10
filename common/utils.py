import struct
import bcrypt
from common.protocol import Protocol

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
