import socket
import json

SERVER_IP = "127.0.0.1"
PORT = 9999

def start_worker():
    s = socket.socket()
    try:
        s.connect((SERVER_IP, PORT))
        print("Connected to Search Server.")
    except:
        print("Server not found!")
        return

    # 1. Receive the Task Packet (Big buffer for large text)
    # We loop to ensure we get the whole message if it's large
    raw_data = b""
    while True:
        packet = s.recv(4096)
        if not packet: break
        raw_data += packet
        # A simple way to know we are done is checking for a specific end marker
        # But for this simple lab, we'll assume one big send/recv or use a timeout
        if len(packet) < 4096: break 
    
    if not raw_data:
        print("No data received.")
        return

    # 2. Unpack the Data
    data = json.loads(raw_data.decode())
    chunk_text = data['text']
    keyword = data['keyword']
    start_line = data['offset']

    print(f"Searching for '{keyword}' starting at line {start_line}...")

    # 3. Perform Local Search
    found_lines = []
    lines = chunk_text.split('\n')
    
    for i, line in enumerate(lines):
        if keyword in line:
            # Calculate the ACTUAL global line number
            global_index = start_line + i + 1 
            found_lines.append(global_index)

    # 4. Send Results Back
    print(f"Found {len(found_lines)} matches.")
    s.send(json.dumps(found_lines).encode())
    s.close()

if __name__ == "__main__":
    start_worker()