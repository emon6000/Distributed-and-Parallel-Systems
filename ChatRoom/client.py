import socket
import threading
import sys

SERVER_IP = "127.0.0.1"
PORT = 9999

def receive_messages(s):
    """
    This function runs in a background thread.
    It sits and waits for messages from the server.
    """
    while True:
        try:
            msg = s.recv(1024).decode()
            if not msg: break
            # \r overwrites the current line (fixing the visual glitch with input)
            sys.stdout.write(f"\r{msg}\nYou: ")
            sys.stdout.flush()
        except:
            print("Disconnected from server.")
            break

def start_chat():
    s = socket.socket()
    try:
        s.connect((SERVER_IP, PORT))
    except:
        print("Server not found!")
        return

    # 1. Handle the nickname login
    # The server sends "Enter nickname", we print it
    prompt = s.recv(1024).decode() 
    nickname = input(prompt)
    s.send(nickname.encode())

    # 2. Start the "Listening Thread"
    # This runs in the background while we type
    thread = threading.Thread(target=receive_messages, args=(s,))
    thread.daemon = True # Ensures thread dies when main program exits
    thread.start()

    print("--- Connected! Type 'exit' to leave ---")

    # 3. Main Loop (Sending Messages)
    while True:
        msg = input("You: ")
        if msg.lower() == 'exit':
            break
        s.send(msg.encode())

    s.close()

if __name__ == "__main__":
    start_chat()