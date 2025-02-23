import grpc
from concurrent import futures
import time

from generated import chat_pb2
from generated import chat_pb2_grpc
from server.handler import send_message, read_messages, list_messages, list_users, delete_message, delete_account, login_stage1, login_stage2

class ChatServiceServicer(chat_pb2_grpc.ChatServiceServicer):
    def LoginStage1(self, request, context):
        username = request.username
        if login_stage1(username):
            return chat_pb2.LoginResponse1(
                user_existing = True,
            )
        else:
            return chat_pb2.LoginResponse1(
                user_existing = False,
            )
        
    def LoginStage2(self, request, context):
        pwd = request.password
        username = request.username
        
        flag, user_list = login_stage2(username, pwd)
        if flag:
            return chat_pb2.LoginResponse2(
                success = True,
                user_list = user_list, 
            )
        else:
            return chat_pb2.LoginResponse2(
                success = False,
                user_list = None,
            )      
        
    def SendMessage(self, request, context):
        recipient = request.recipient
        sender = request.sender
        content = request.content
        send_message(sender, recipient, content)
        return chat_pb2.SendMessageResponse(
            success = True,
        )       

    def ReadMessage(self, request, context):
        sender = request.sender
        reader = request.reader
        read_messages(sender, reader)
        return chat_pb2.ReadMessageResponse(
            success = True,
        )  

    def ListMessages(self, request, context):
        friend = request.friend
        user = request.user
        resp_list = list_messages(user, friend)
        chat_messages = []
        for msg in resp_list:
            chat_messages.append(
                chat_pb2.ChatMessage(
                    id=msg.id,
                    timestamp=msg.timestamp,
                    sender=msg.sender,
                    recipient=msg.recipient,
                    content=msg.content,
                    status=msg.status
                )
            )
        return chat_pb2.ListMessagesResponse(
            messages = chat_messages,
        )  
    
    def ListUsers(self, request, context):
        user = request.user
        resp_list = list_users(user)
        return chat_pb2.ListUserResponse(
            user_list = resp_list,
        )  
    
    def DeleteMessage(self, request, context):
        msg_id = request.message_id
        user = request.user
        delete_message(user, msg_id)
        return chat_pb2.DeleteMessagesResponse(
            success = True
        )    
    
    def DeleteAccount(self, request, context):
        user = request.user
        delete_account(user)
        return chat_pb2.DeleteAccountResponse(
            success = True
        )    

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    chat_pb2_grpc.add_GreeterServicer_to_server(ChatServiceServicer(), server)
    server.add_insecure_port("[::]:50051")
    server.start()
    print("Server started at port 50051...")
    try:
        while True:
            time.sleep(86400)
    except KeyboardInterrupt:
        server.stop(0)

if __name__ == "__main__":
    serve()
