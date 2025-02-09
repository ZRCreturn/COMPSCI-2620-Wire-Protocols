import time
import uuid


class Chatmsg:
    def __init__(self, sender, recipient, content, msg_id=None, timestamp=None, status="unread"):
        self.id = msg_id if msg_id else str(uuid.uuid4()) 
        self.timestamp = timestamp if timestamp else time.time()  # float timestamp
        self.sender = sender
        self.recipient = recipient
        self.content = content
        self.status = status  

    def to_dict(self):
        """Convert the Chatmsg object to a dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "recipient": self.recipient,
            "content": self.content,
            "status": self.status,
        }

    @staticmethod
    def from_dict(data):
        """Convert a dictionary to a Chatmsg object"""
        return Chatmsg(
            sender=data["sender"],
            recipient=data["recipient"],
            content=data["content"],
            msg_id=data["id"],
            timestamp=data["timestamp"],
            status=data["status"]
        )
