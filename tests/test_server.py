import socket
import threading
import time
import pytest
from server.server import start_server, HOST, PORT 
from common.utils import send_data, recv_data
from common.message import Chatmsg
from common.protocol import Protocol


@pytest.fixture
def server():
    """start server thread"""
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()
    time.sleep(1)  
    yield


def test_login(server):  
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    send_data(client_socket, Protocol.REQ_LOGIN_1, "test_user")
    resp_type, resp = recv_data(client_socket)
    assert resp_type == Protocol.RESP_USER_NOT_EXISTING

    send_data(client_socket, Protocol.REQ_LOGIN_2, "password")
    resp_type, resp = recv_data(client_socket)
    assert resp_type == Protocol.RESP_LOGIN_SUCCESS

    client_socket.close()


    
