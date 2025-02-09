import pytest
from common.protocol import Protocol
from common.message import Chatmsg


@pytest.fixture
def protocol():
    return Protocol()

def test_int(protocol):
    data = 3
    encoded_data = protocol.encode_obj(data)
    assert type(encoded_data) == bytes
    decoded_data, _ = protocol.decode_obj(encoded_data)
    assert decoded_data == 3

def test_float(protocol):
    data = 3.14
    encoded_data = protocol.encode_obj(data)
    assert type(encoded_data) == bytes
    decoded_data, _ = protocol.decode_obj(encoded_data)
    assert decoded_data == 3.14

def test_str(protocol):
    data = "test str"
    encoded_data = protocol.encode_obj(data)
    assert type(encoded_data) == bytes
    decoded_data, _ = protocol.decode_obj(encoded_data)
    assert decoded_data == "test str"

def test_list(protocol):
    data = ["apple", "banana"]
    encoded_data = protocol.encode_obj(data)
    assert type(encoded_data) == bytes
    decoded_data, _ = protocol.decode_obj(encoded_data)
    assert decoded_data == ["apple", "banana"]

def test_dict(protocol):
    data = {"apple":1, "banana": 2}
    encoded_data = protocol.encode_obj(data)
    assert type(encoded_data) == bytes
    decoded_data, _  = protocol.decode_obj(encoded_data)
    assert decoded_data == {"apple":1, "banana": 2}

def test_chat_msg(protocol):
    data = Chatmsg("eric", "bob", "test")
    encoded_data = protocol.encode_obj(data)
    assert type(encoded_data) == bytes
    decoded_data, _ = protocol.decode_obj(encoded_data)
    assert decoded_data.sender == "eric"
    assert decoded_data.recipient == "bob"
    assert decoded_data.content == "test"

