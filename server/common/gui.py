import tkinter as tk
from tkinter import messagebox
import socket
import threading
import pickle
from utils import hash_pwd, check_pwd, send_data, recv_data  # Assuming these utilities are available

class ClientApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Client App")
        
        # Initialize the connection-related variables
        self.server_ip = "127.0.0.1"  # The server's IP address
        self.server_port = 5000  # The server's port number
        self.socket = None
        self.logged_in_user = None
        self.contacts = {}
        
        # Username and password fields for login
        self.username_label = tk.Label(self.master, text="Username:")
        self.username_label.pack()
        self.username_entry = tk.Entry(self.master)
        self.username_entry.pack()

        self.password_label = tk.Label(self.master, text="Password:")
        self.password_label.pack()
        self.password_entry = tk.Entry(self.master, show="*")
        self.password_entry.pack()

        # Buttons for login and account creation
        self.login_button = tk.Button(self.master, text="Login", command=self.login)
        self.login_button.pack()

        self.create_account_button = tk.Button(self.master, text="Create Account", command=self.create_account)
        self.create_account_button.pack()

        # Error label (for showing errors)
        self.error_label = tk.Label(self.master, text="", fg="red")
        self.error_label.pack()

        # Frame for contacts and messages
        self.contacts_frame = tk.Frame(self.master)
        self.contacts_frame.pack()

        # Frame for message display and sending
        self.message_frame = tk.Frame(self.master)
        self.message_frame.pack()

        # Initialize connection to the server
        self.connect_to_server()

    def connect_to_server(self):
        """Connect to the server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.server_ip, self.server_port))
            print("Connected to server.")
        except Exception as e:
            print(f"Failed to connect to server: {e}")
            self.error_label.config(text="Failed to connect to server.")

    def send_data_to_server(self, msg_type, data):
        """Send data to the server."""
        try:
            message = {'msg_type': msg_type, 'data': data}
            serialized_data = pickle.dumps(message)  # Serialize the data using pickle
            self.socket.sendall(serialized_data)

            # Wait for server response
            response = self.socket.recv(1024)
            if response:
                response_data = pickle.loads(response)
                return response_data
            else:
                self.error_label.config(text="No response from server.")
        except Exception as e:
            print(f"Error: {e}")
            self.error_label.config(text="Failed to communicate with server.")

    def login(self):
        """Handle login functionality."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            data = {"action": "login", "username": username, "password": password}
            response = self.send_data_to_server(2, data)  # Assuming 2 is login msg_type
            if response and response.get("status") == "success":
                self.logged_in_user = username
                self.error_label.config(text="")
                self.load_contacts()
                self.show_message_interface()
            else:
                self.error_label.config(text="Invalid credentials. Please try again.")
        else:
            self.error_label.config(text="Please enter both username and password.")

    def create_account(self):
        """Handle account creation functionality."""
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password:
            hashed_password = hash_pwd(password)
            data = {"action": "create_account", "username": username, "password": hashed_password}
            response = self.send_data_to_server(1, data)  # Assuming 1 is create account msg_type
            if response and response.get("status") == "success":
                messagebox.showinfo("Account Created", "Account created successfully!")
            else:
                self.error_label.config(text="Failed to create account.")
        else:
            self.error_label.config(text="Please enter both username and password.")

    def load_contacts(self):
        """Load contacts who have sent messages to the logged-in user."""
        data = {"action": "get_contacts", "username": self.logged_in_user}
        response = self.send_data_to_server(3, data)  # Assuming 3 is get contacts msg_type
        if response and response.get("status") == "success":
            self.contacts = response["contacts"]
            self.populate_contacts()

    def populate_contacts(self):
        """Populate the contacts list on the left."""
        for widget in self.contacts_frame.winfo_children():
            widget.destroy()

        self.contacts_listbox = tk.Listbox(self.contacts_frame)
        self.contacts_listbox.pack()

        for contact in self.contacts:
            self.contacts_listbox.insert(tk.END, contact)
        
        self.contacts_listbox.bind("<<ListboxSelect>>", self.show_chat_history)

    def show_message_interface(self):
        """Show the message sending interface once logged in."""
        for widget in self.message_frame.winfo_children():
            widget.destroy()

        self.contact_label = tk.Label(self.message_frame, text="Select a contact to chat with:")
        self.contact_label.pack()

        self.message_entry = tk.Entry(self.message_frame)
        self.message_entry.pack()

        self.send_button = tk.Button(self.message_frame, text="Send Message", command=self.send_message)
        self.send_button.pack()

        self.chat_history_text = tk.Text(self.message_frame, height=10, width=50)
        self.chat_history_text.pack()

    def show_chat_history(self, event):
        """Show chat history for the selected contact."""
        contact = self.contacts_listbox.get(self.contacts_listbox.curselection())
        data = {"action": "get_chat_history", "username": self.logged_in_user, "contact": contact}
        response = self.send_data_to_server(4, data)  # Assuming 4 is get chat history msg_type
        if response and response.get("status") == "success":
            chat_history = response.get("chat_history", [])
            self.chat_history_text.delete(1.0, tk.END)
            for message in chat_history:
                self.chat_history_text.insert(tk.END, f"{message['sender']}: {message['content']}\n")

    def send_message(self):
        """Send a message to the selected contact."""
        contact = self.contacts_listbox.get(self.contacts_listbox.curselection())
        message_content = self.message_entry.get()
        if message_content:
            data = {"action": "send_message", "username": self.logged_in_user, "contact": contact, "message": message_content}
            response = self.send_data_to_server(5, data)  # Assuming 5 is send message msg_type
            if response and response.get("status") == "success":
                self.message_entry.delete(0, tk.END)
                self.show_chat_history(None)  # Refresh chat history

if __name__ == "__main__":
    root = tk.Tk()
    app = ClientApp(root)
    root.mainloop()
