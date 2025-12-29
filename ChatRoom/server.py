import socket
import threading

HOST = "0.0.0.0"
PORT = 9999

# Global list to keep track of everyone connected
clients = []

def broadcast(message, sender_conn):
    """
    Sends a message to everyone EXCEPT the person who sent it.
    """
    for client in clients:
        if client != sender_conn:
            try:
                client.send(message.encode())
            except:
                # If sending fails, assume client disconnected and remove them
                clients.remove(client)

def handle_client(conn, addr):
    """
    Runs in a separate thread for EACH user. 
    Constantly listens for messages from that specific user.
    """
    print(f"[+] New connection from {addr}")
    
    # 1. Ask for a nickname
    conn.send("Enter your nickname: ".encode())
    nickname = conn.recv(1024).decode()
    
    welcome_msg = f"--- {nickname} has joined the chat! ---"
    broadcast(welcome_msg, conn) # Tell everyone else
    
    # 2. Main Chat Loop
    while True:
        try:
            # Wait for message
            msg = conn.recv(1024).decode()
            if not msg: break # Connection closed
            
            # Format: "Bob: Hello everyone!"
            final_msg = f"{nickname}: {msg}"
            print(final_msg) # Log on server
            
            # Send to everyone else
            broadcast(final_msg, conn)
            
        except:
            break

    # 3. Cleanup when they leave
    clients.remove(conn)
    broadcast(f"--- {nickname} left the chat ---", None)
    conn.close()

def start_server():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((HOST, PORT))
    s.listen()
    print(f"[*] Chat Server running on {PORT}...")

    while True:
        conn, addr = s.accept()
        clients.append(conn)
        
        # Start a thread for this user so we can go back to accepting new ones
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    start_server()