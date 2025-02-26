import tkinter as tk
from tkinter import messagebox
import grpc
import chat_pb2
import chat_pb2_grpc

class ChatClientApp:
    def __init__(self, root, host='localhost', port=50051):
        self.root = root
        self.host = host
        self.port = port
        self.username = None
        
        # Create a gRPC channel and stub
        self.channel = grpc.insecure_channel(f"{self.host}:{self.port}")
        self.stub = chat_pb2_grpc.ChatServiceStub(self.channel)
        
        self.current_screen = None
        self.login_screen()
    
    def login_screen(self):
        self.clear_screen()
        self.current_screen = None
        
        tk.Label(self.root, text="Username:").pack()
        self.username_entry = tk.Entry(self.root)
        self.username_entry.pack()
        tk.Button(self.root, text="Login", command=self.handle_username).pack()
    
    def handle_username(self):
        username = self.username_entry.get()
        if not username:
            messagebox.showwarning("Input Error", "Username cannot be empty!")
            return
        
        self.username = username
        response = self.stub.LoginStage1(chat_pb2.LoginRequest1(username=username))
        
        if response.user_existing:
            self.handle_password_screen()
        else:
            self.handle_password_screen()
    
    def handle_password_screen(self):
        self.clear_screen()
        self.current_screen = "password"
        
        tk.Label(self.root, text="Password:").pack()
        self.password_entry = tk.Entry(self.root, show="*")
        self.password_entry.pack()
        tk.Button(self.root, text="Submit", command=self.handle_password).pack()
    
    def handle_password(self):
        password = self.password_entry.get()
        if not password:
            messagebox.showwarning("Input Error", "Password cannot be empty!")
            return
        
        response = self.stub.LoginStage2(chat_pb2.LoginRequest2(username=self.username, password=password))
        if response.success:
            self.user_list = response.user_list
            self.show_user_list_screen()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")
    
    def show_user_list_screen(self):
        self.clear_screen()
        self.current_screen = "user_list"
        
        tk.Label(self.root, text="User List:").pack()
        for user in self.user_list:
            tk.Button(self.root, text=user, command=lambda u=user: self.show_message_list(u)).pack()
    
    def show_message_list(self, friend):
        self.clear_screen()
        self.current_screen = f"chat_{friend}"
        
        response = self.stub.ListMessages(chat_pb2.ListMessagesRequest(user=self.username, friend=friend))
        tk.Label(self.root, text=f"Chat with {friend}:").pack()
        
        self.message_listbox = tk.Listbox(self.root)
        self.message_listbox.pack()
        for msg in response.messages:
            self.message_listbox.insert(tk.END, f"{msg.sender}: {msg.content}")
        
        self.message_entry = tk.Entry(self.root)
        self.message_entry.pack()
        tk.Button(self.root, text="Send", command=lambda: self.send_message(friend)).pack()
        tk.Button(self.root, text="Back", command=self.show_user_list_screen).pack()
    
    def send_message(self, recipient):
        message = self.message_entry.get()
        if not message:
            messagebox.showwarning("Input Error", "Message cannot be empty!")
            return
        
        self.stub.SendMessage(chat_pb2.SendMessageRequest(sender=self.username, recipient=recipient, content=message))
        self.show_message_list(recipient)
    
    def clear_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def delete_message(self, msg_id, recipient):
    response = self.stub.DeleteMessage(chat_pb2.DeleteMessagesRequest(user=self.username, message_id=msg_id))

    if response.success:
        self.show_message_list(recipient)
    else:
        messagebox.showerror("Error", "Failed to delete message.")

    def delete_account(self):
    response = self.stub.DeleteAccount(chat_pb2.DeleteAccountRequest(user=self.username))

    if response.success:
        messagebox.showinfo("Account Deleted", "Your account has been deleted.")
        self.root.quit()
    else:
        messagebox.showerror("Error", "Failed to delete account.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ChatClientApp(root)
    root.mainloop()
