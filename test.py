import struct

def encode_obj(obj):
    """
    serialize py objs
    """
    if isinstance(obj, int):
        # define int as type 0x00 + 8-byte signed integer
        return b'\x00' + struct.pack('!q', obj)

    elif isinstance(obj, str):
        # define str as type 0x01 + 4-byte length + UTF-8 byte array
        data = obj.encode('utf-8')
        length = len(data)
        return b'\x01' + struct.pack('!I', length) + data

    elif isinstance(obj, list):
        # define list as type 0x02 + 4-byte size + encode_obj(elements)
        encoded_items = []
        for item in obj:
            encoded_items.append(encode_obj(item))
        total = b''.join(encoded_items)
        return b'\x02' + struct.pack('!I', len(obj)) + total

    elif isinstance(obj, dict):
        # define dict as type 0x03 + 4-byte size + encode_obj(key) + encode_obj(value)
        # we define key should be str
        encoded_items = []
        for k, v in obj.items():
            encoded_key = encode_obj(str(k))
            encoded_value = encode_obj(v)
            encoded_items.append(encoded_key + encoded_value)
        total = b''.join(encoded_items)
        return b'\x03' + struct.pack('!I', len(obj)) + total

    else:
        raise TypeError(f"Unsupported type: {type(obj)}")


def decode_obj(data, offset=0):
    type_code = data[offset]
    offset += 1

    if type_code == 0x00:
        # int64
        (val,) = struct.unpack_from('!q', data, offset)
        offset += 8
        return val, offset

    elif type_code == 0x01:
        # string
        (str_len,) = struct.unpack_from('!I', data, offset)
        offset += 4
        s = data[offset:offset+str_len].decode('utf-8')
        offset += str_len
        return s, offset

    elif type_code == 0x02:
        # list
        (list_size,) = struct.unpack_from('!I', data, offset)
        offset += 4
        arr = []
        for _ in range(list_size):
            item, offset = decode_obj(data, offset)
            arr.append(item)
        return arr, offset

    elif type_code == 0x03:
        # dict
        (dict_size,) = struct.unpack_from('!I', data, offset)
        offset += 4
        d = {}
        for _ in range(dict_size):
            # key
            key, offset = decode_obj(data, offset)
            # value
            value, offset = decode_obj(data, offset)
            d[key] = value
        return d, offset

    else:
        raise ValueError(f"Unknown type code: {type_code}")

a = "hello"
a_bytes = encode_obj(a)
print(len(a_bytes))
print(decode_obj(a_bytes))


b = 12345
b_bytes = encode_obj(b)
print(len(b_bytes))
print(decode_obj(b_bytes))

c = ['test', 347]
c_bytes = encode_obj(c)
print(len(c_bytes))
print(decode_obj(c_bytes))

d = {'apple': 5, 'banana': 6}
d_bytes = encode_obj(d)
print(len(d_bytes))
print(decode_obj(d_bytes))