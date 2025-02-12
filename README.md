# COMPSCI-2620-Wire-Protocols

# GUI Design Guide

## 1. Login

### Phase 1: Username Entry
- The user enters their username.
- The system sends a request to the server using `send_data` with the following parameters:
  - `sock`: `self.socket`
  - `msg_type`: `REQ_LOGIN_1`
  - `data`: `username` (string)
- The system then calls `resp_type, resp = recv_data(self.socket)` to receive the response type and object.
- There are two possible response types, all need user to input password:
  - `RESP_USER_EXISTING`: The user exists, prompting them to enter a password.
  - `RESP_USER_NOT_EXISTING`: The user does not exist, prompting them to register.
- The response object `resp` is `None` and does not need to be considered.

### Phase 2: Password Entry
- The user enters their password.
- The system sends a request to the server using `send_data` with the following parameters:
  - `sock`: `self.socket`
  - `msg_type`: `REQ_LOGIN_2`
  - `data`: `password` (string)
- The system then calls `resp_type, resp = recv_data(self.socket)` to receive the response type and object.
- There are two possible response types:
  - `RESP_LOGIN_SUCCESS`: Login successful, redirect to the user interface.
  - `RESP_LOGIN_FAILED`: Login failed, prompt the user to retry.
- The response object `resp` is `None` and does not need to be considered.

## 2. User List
- After a successful login, the system sends a request to retrieve the user list using `send_data`:
  - `sock`: `self.socket`
  - `msg_type`: `REQ_LIST_USERS`
  - `data`: `None` (no additional data needed)
- The system then calls `resp_type, resp = recv_data(self.socket)` to receive the response type and object.
- The response type is `RESP_LIST_USERS`, and `resp` is a dictionary where:
  - The key is the `username`.
  - The value is the number of unread messages, e.g., `{"eric": 0, "test_user": 0}`.
- Use this data to build the corresponding GUI.

## 3. Message List
- Clicking on a user displays the chat history between the logged-in user and the selected user.
- The system sends a request to retrieve the message list using `send_data`:
  - `sock`: `self.socket`
  - `msg_type`: `REQ_LIST_MESSAGES`
  - `data`: The target username (string).
- The system then calls `resp_type, resp = recv_data(self.socket)` to receive the response type and object.
- The response type is `RESP_LIST_MESSAGES`, and `resp` is a list of message objects (instances of `Chatmsg`).
- Each message object contains attributes such as `sender`, `recipient`, and `content`.
- Use these attributes to build the GUI for displaying messages.

## 4. Send Message
- Sending a message requires communicating with the server using `send_data`:
  - `sock`: `self.socket`
  - `msg_type`: `REQ_SEND_MSG`
  - `data`: A list where:
    - The first element is the recipient's username.
    - The second element is the message content, e.g., `["bob", "hey"]`.
- **Do not call `recv_data` immediately after sending the message**, as it may cause a block.
- After sending the message, **refresh the message list** to update the chat interface.

## 5. Delete Message
- A new delete message API has been added. Please pull the latest updates from the main branch.
- Deleting a message requires sending a request to the server using `send_data`:
  - `sock`: `self.socket`
  - `msg_type`: `REQ_DELETE_MESSAGE`
  - `data`: The ID of the message to be deleted (string).
- The message ID is an attribute of the `Chatmsg` class and can be retrieved from the message object.
- **Do not call `recv_data` immediately after sending the request**, as it may cause a block.
- After deletion, **refresh the message list** to update the chat interface.

## 6. Delete Account
- A new delete account API has been added. Please pull the latest updates from the main branch.
- Deleting an account requires sending a request to the server using `send_data`:
  - `sock`: `self.socket`
  - `msg_type`: `REQ_DELETE_ACCOUNT`
  - `data`: `None` (no additional data needed)
- **Do not call `recv_data` immediately after sending the request**, as it may cause a block.
- After deletion, **refresh the message list** to update the chat interface.
