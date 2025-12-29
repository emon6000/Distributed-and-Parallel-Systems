import socket
import json
import threading

HOST = "0.0.0.0"
PORT = 9999
NUM_WORKERS = 2  # We will use 2 workers for this example

def handle_worker(conn, chunk_lines, start_offset, keyword, results):
    """
    Sends a chunk of lines to a worker and waits for line numbers back.
    """
    try:
        # 1. Prepare the Data Packet
        payload = {
            "text": "\n".join(chunk_lines), # Join lines back into a string
            "keyword": keyword,
            "offset": start_offset
        }
        
        # 2. Send Data
        conn.send(json.dumps(payload).encode())
        
        # 3. Receive Results (List of line numbers)
        data = conn.recv(1024).decode()
        found_indices = json.loads(data)
        
        # Add to global results
        results.extend(found_indices)
        
    except Exception as e:
        print(f"Worker failed: {e}")
    finally:
        conn.close()

def start_server():
    # --- SETUP ---
    filename = "log.txt" 
    keyword = input("Enter keyword to search (e.g., 'error'): ")
    
    # Read all lines
    try:
        with open(filename, "r") as f:
            all_lines = f.readlines()
    except FileNotFoundError:
        print("Please create 'log.txt' first!")
        return

    total_lines = len(all_lines)
    mid = total_lines // NUM_WORKERS

    # Split lines: Worker 1 gets first half, Worker 2 gets second half
    # chunk_info stores: (lines_list, starting_index)
    chunks_info = [
        (all_lines[:mid], 0),           # Start at line 0
        (all_lines[mid:], mid)          # Start at line mid
    ]

    # --- NETWORKING ---
    s = socket.socket()
    s.bind((HOST, PORT))
    s.listen(NUM_WORKERS)
    print(f"Server looking for '{keyword}' in {total_lines} lines.")
    print(f"Waiting for {NUM_WORKERS} workers...")

    workers = []
    for i in range(NUM_WORKERS):
        conn, addr = s.accept()
        print(f"Worker {i+1} connected from {addr}")
        workers.append(conn)

    # --- DISTRIBUTED EXECUTION ---
    print("Dispatching search tasks...")
    global_results = []
    threads = []

    for i in range(NUM_WORKERS):
        lines, offset = chunks_info[i]
        
        # We use threads so both workers search at the exact same time
        t = threading.Thread(target=handle_worker, args=(workers[i], lines, offset, keyword, global_results))
        t.start()
        threads.append(t)

    # Wait for both to finish
    for t in threads:
        t.join()

    # --- AGGREGATION ---
    print("\n--- SEARCH RESULTS ---")
    if global_results:
        print(f"Keyword '{keyword}' found on lines: {sorted(global_results)}")
    else:
        print("Keyword not found.")

    s.close()

if __name__ == "__main__":
    start_server()