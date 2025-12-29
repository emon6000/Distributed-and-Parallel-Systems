import socket, json
from collections import Counter

# --- CONFIGURATION ---
HOST = "0.0.0.0"
PORT = 9999
NUM_CLIENTS = 5 # Change this number to add more clients!

# --- HELPER FUNCTION ---
def split_text(text, n):
    """Splits a list of words into n roughly equal chunks"""
    k, m = divmod(len(text), n)
    return [text[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n)]

# --- MAIN SERVER LOGIC ---
# 1. Prepare Data
file_path = input("File path: ")
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

words = text.lower().split()
word_chunks = split_text(words, NUM_CLIENTS)

# Convert list of words back to strings for sending
chunk_strings = [" ".join(chunk) for chunk in word_chunks]

# 2. Start Network
s = socket.socket()
s.bind((HOST, PORT))
s.listen(NUM_CLIENTS)
print(f"Server waiting for {NUM_CLIENTS} clients...")

clients = []

# 3. Accept Connections Loop
for i in range(NUM_CLIENTS):
    c, addr = s.accept()
    print(f"Connected {i+1}/{NUM_CLIENTS}: {addr}")
    clients.append(c)

# 4. Send Data Loop
print("Distributing tasks...")
for i in range(NUM_CLIENTS):
    # Send the specific chunk to client i
    clients[i].send(chunk_strings[i].encode())

# 5. Receive & Aggregate Loop
final_total = Counter()

print("Receiving results...")
for i in range(NUM_CLIENTS):
    # Receive data (buffer size increased to ensure we get it all)
    data = clients[i].recv(10000000).decode()
    
    # Convert JSON back to Counter
    partial_result = json.loads(data)
    
    # Add to the total
    final_total += Counter(partial_result)
    print(f"Received result from Client {i+1}")

# 6. Final Output
print("\nFINAL WORD COUNT (Top 5 words):")
print(final_total.most_common(5))

# Cleanup
for c in clients:
    c.close()
s.close()