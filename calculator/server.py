import socket

# Map mathematical symbols to the Ports we expect the workers to be on
OP_TO_PORT = {
    "+": 9001,
    "-": 9002,
    "*": 9003,
    "/": 9004,
    "%": 9005
}

def start_server():
    workers = {} # Will store active connections: {'+': socket_obj, '-': socket_obj...}
    
    print("--- SERVER STARTING ---")
    
    # 1. Setup connections for all 5 workers
    # We loop through our config to open 5 ports
    for op, port in OP_TO_PORT.items():
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # This line allows us to restart the server without "Address already in use" errors
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        try:
            s.bind(("0.0.0.0", port))
            s.listen(1)
            print(f"[*] Waiting for '{op}' worker on port {port}...")
            
            conn, addr = s.accept()
            print(f"[+] Worker '{op}' connected from {addr}")
            workers[op] = conn
            
        except Exception as e:
            print(f"[!] Error binding port {port}: {e}")
            return

    print("\n--- SYSTEM FULLY OPERATIONAL ---")
    print("Usage: 10 + 5, 20 % 3, etc. Type 'exit' to quit.")

    # 2. Main Processing Loop
    while True:
        try:
            user_input = input("\nCalculate: ").strip()
            if user_input.lower() == "exit": break
            
            # Parse input (e.g., "10 + 5")
            parts = user_input.split()
            if len(parts) != 3:
                print("Invalid format. Use: NUMBER OP NUMBER (e.g., 5 * 10)")
                continue
                
            num1, op, num2 = parts
            
            # check if we have a worker for this operation
            if op in workers:
                # Send task to the specific worker
                worker_conn = workers[op]
                payload = f"{num1},{num2}"
                worker_conn.send(payload.encode())
                
                # Wait for answer
                result = worker_conn.recv(1024).decode()
                print(f"Result: {result}")
            else:
                print(f"Unknown operator '{op}'. Supported: +, -, *, /, %")

        except Exception as e:
            print(f"Error: {e}")

    # Cleanup
    for conn in workers.values():
        conn.close()

if __name__ == "__main__":
    start_server()