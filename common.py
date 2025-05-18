import json
import socket

def send_message(sock, data):
    toSend = data.encode('utf-8')

    data_len = len(toSend)
    sock.sendall(data_len.to_bytes(4, 'big'))
    sock.sendall(toSend)

def receive_message(sock):
    """Принимает JSON-данные из сокета, используя заголовок с размером."""
    header = sock.recv(4)
    if len(header) != 4:
        raise ValueError("Invalid header received")
    data_len = int.from_bytes(header, 'big')
    chunks = []
    bytes_received = 0
    while bytes_received < data_len:
        chunk = sock.recv(min(4096, data_len - bytes_received))
        if not chunk:
            raise ConnectionError("Connection closed prematurely")
        chunks.append(chunk)
        bytes_received += len(chunk)
    raw_data = b''.join(chunks).decode('utf-8')

    return raw_data