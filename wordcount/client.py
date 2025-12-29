import socket, json
from collections import Counter

SERVER_IP = "127.0.0.1"
PORT = 9999

s = socket.socket()
s.connect((SERVER_IP, PORT))

chunk = s.recv(1000000).decode()
words = chunk.lower().split()

s.send(json.dumps(dict(Counter(words))).encode())
s.close()
print("Client1 done")