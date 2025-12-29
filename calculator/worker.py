import socket
import sys

# Configuration: Map operations to specific Ports
# This mimics "Service Discovery" - knowing where each service lives
PORT_MAP = {
    "add": 9001,
    "sub": 9002,
    "mul": 9003,
    "div": 9004,
    "mod": 9005
}

def start_worker(op_type):
    host = "127.0.0.1"
    
    if op_type not in PORT_MAP:
        print(f"Unknown operation: {op_type}. Choose from: add, sub, mul, div, mod")
        return

    port = PORT_MAP[op_type]
    
    s = socket.socket()
    try:
        s.connect((host, port))
        print(f"[*] I am the '{op_type.upper()}' worker. Connected to port {port}.")
    except ConnectionRefusedError:
        print(f"[!] Could not connect. Is the server running?")
        return

    while True:
        try:
            # 1. Wait for task (e.g., "10,5")
            data = s.recv(1024).decode()
            if not data: break
            
            print(f"Received task: {data}")
            a, b = map(float, data.split(","))
            
            # 2. Perform the logic
            result = 0
            if op_type == "add": result = a + b
            elif op_type == "sub": result = a - b
            elif op_type == "mul": result = a * b
            elif op_type == "div": result = a / b if b != 0 else "Error"
            elif op_type == "mod": result = a % b
            
            # 3. Send back result
            s.send(str(result).encode())
            print(f"Sent result: {result}")
            
        except Exception as e:
            print(f"Error processing: {e}")
            break

    s.close()

if __name__ == "__main__":
    # You can run this file like: python worker.py add
    if len(sys.argv) > 1:
        op = sys.argv[1].lower()
        start_worker(op)
    else:
        op = input("Enter my role (add, sub, mul, div, mod): ").strip().lower()
        start_worker(op)