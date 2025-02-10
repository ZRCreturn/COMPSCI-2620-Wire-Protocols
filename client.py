import socket
import threading
import time

from common.protocol import Protocol
from common.utils import send_data, recv_data


class ChatClient:
    def __init__(self, host="127.0.0.1", port=12345):
        self.host = host
        self.port = port
        self.client_socket = None
        self.is_running = False
        self.username = None

        # local cache 
        self.messages_map = {}

    def connect(self):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.host, self.port))
            self.is_running = True
            print(f"Connected to server at {self.host}:{self.port}")
        except Exception as e:
            print(f"Failed to connect: {e}")
            self.is_running = False

    def login(self, username, password):
        """
        Login procedure example:
        1. Send REQ_LOGIN_1 (username)
        2. Wait for server response (user existing or not)
        3. Send REQ_LOGIN_2 (password)
        4. Wait for server response (login success or failed)
        """
        if not self.is_running:
            print("Client is not connected.")
            return False

        # 1. Send REQ_LOGIN_1 with the username
        send_data(self.client_socket, Protocol.REQ_LOGIN_1, username)
        resp_type, resp = recv_data(self.client_socket)
        if resp_type is None:
            print("No response for REQ_LOGIN_1, check the server or connection.")
            return False

        if resp_type == Protocol.RESP_USER_EXISTING:
            print(f"User {username} exists, proceeding with password submission.")
        elif resp_type == Protocol.RESP_USER_NOT_EXISTING:
            print(f"User {username} does not exist; it will be created upon password submission.")
        else:
            print(f"Unexpected response after REQ_LOGIN_1: resp_type={resp_type}, resp={resp}")
            return False

        # 2. Send REQ_LOGIN_2 with the password
        send_data(self.client_socket, Protocol.REQ_LOGIN_2, password)
        resp_type, resp = recv_data(self.client_socket)
        if resp_type is None:
            print("No response for REQ_LOGIN_2, check the server or connection.")
            return False

        if resp_type == Protocol.RESP_LOGIN_SUCCESS:
            print(f"Login success for user: {username}")
            self.username = username
            return True
        elif resp_type == Protocol.RESP_LOGIN_FAILED:
            print("Login failed. Please check your password.")
            return False
        else:
            print(f"Unexpected response after REQ_LOGIN_2: resp_type={resp_type}, resp={resp}")
            return False

    def send_message(self, recipient, content):
        """
        Send a message to a specific recipient.
        - Protocol.REQ_SEND_MSG
        - Data = [recipient, content]

        After sending, the server does not return a response. 
        Then immediately send REQ_LIST_MESSAGES to retrieve the latest messages with that recipient.
        """
        if not self.is_running or not self.username:
            print("Cannot send message. Either not connected or not logged in.")
            return

        print(f"[send_message] Sending message to {recipient} -> {content}")
        # 1. Send REQ_SEND_MSG
        send_data(self.client_socket, Protocol.REQ_SEND_MSG, [recipient, content])

        # 2. Send REQ_LIST_MESSAGES to get the updated message list with the recipient
        self.list_messages(recipient)

    def read_message(self, sender):
        """
        Mark messages from a specific sender as read.
        - Protocol.REQ_READ_MSG
        - Data = sender

        After sending, the server does not return a response.
        Then send REQ_LIST_MESSAGES to get the updated message list with that sender.
        """
        if not self.is_running or not self.username:
            print("Cannot read messages. Either not connected or not logged in.")
            return

        print(f"[read_message] Marking messages from {sender} as read.")
        # 1. Send REQ_READ_MSG
        send_data(self.client_socket, Protocol.REQ_READ_MSG, sender)

        # 2. Send REQ_LIST_MESSAGES to get updated conversation with that sender
        self.list_messages(sender)

    def list_messages(self, friend):
        """
        Retrieve all messages between the current user and a friend.
        - Protocol.REQ_LIST_MESSAGES
        - Data = friend's username
        - return: a list of messages concerning both the current user and that friend
        """
        if not self.is_running or not self.username:
            print("Cannot list messages. Either not connected or not logged in.")
            return

        # Send REQ_LIST_MESSAGES
        send_data(self.client_socket, Protocol.REQ_LIST_MESSAGES, friend)

        # Receive and process the message list
        resp_type, resp = recv_data(self.client_socket)
        if resp_type is None:
            print("No response for REQ_LIST_MESSAGES.")
            return

        if resp_type == Protocol.RESP_LIST_MESSAGES:
            # resp is assumed to be a list of dictionaries representing Chatmsg objects
            return resp
            
            
    def start_gui(self):
        """
        Launch a separate thread to handle GUI logic.
        Actual rendering is not implemented here.
        """
        gui_thread = threading.Thread(target=self.gui_loop, daemon=True)
        gui_thread.start()

    def gui_loop(self):
        """
        Placeholder GUI loop for demonstration.
        Replace with your actual GUI framework logic (Tkinter, PyQt, etc.).
        """
        while self.is_running:
            time.sleep(1)
            # Implement GUI refresh or event callbacks here

    def close(self):
        """
        Close the client connection and stop the running loop.
        """
        self.is_running = False
        if self.client_socket:
            self.client_socket.close()
            self.client_socket = None
        print("Client closed.")


def main():
    client = ChatClient(host="127.0.0.1", port=5000)
    client.connect()


    # Close the client
    client.close()


if __name__ == "__main__":
    main()
