import socket
import threading
import time
from server.handler import client_thread_entry

HOST = '127.0.0.1'
PORT = 5000

def start_server():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((HOST, PORT))
    server_socket.listen(5)
    print(f"Server listening on {HOST}:{PORT}")

    while True:
        client_socket, addr = server_socket.accept()
        t = threading.Thread(target=client_thread_entry, args=(client_socket, addr))
        t.start()

if __name__ == "__main__":
    start_server()
