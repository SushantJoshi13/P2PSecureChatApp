import socket
import threading
import os
import random
import queue

# Libraries to implement AES
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from hashlib import sha256

chat_active = False
# Maintain the queue of all connections available
incoming_connections = queue.Queue()

# Read p and g from environment variables (take prime numbers)
p = int(os.getenv("P", "23"))
g = int(os.getenv("Q", "5"))

# Generate Public and Private key
a = random.randint(2, p - 2)
A = pow(g, a, p)

chat_active = False 

# AES key from shared secret among 2 users
def generate_aes_key(shared_secret):
    return sha256(str(shared_secret).encode()).digest()

# key exchange function (same as in task 3)
def key_exchange(rec_socket):
    rec_socket.send(str(A).encode())
    
    # Get the public key of the other user and compute the shared secret
    B = int(rec_socket.recv(1024).decode())
    shared_secret = pow(B, a, p)
    
    # Print keys and shared secret of the respective user
    print(f"Private Key (a): {a}")
    print(f"Public Key (A): {A}")
    print(f"Shared Secret Key Computed: {shared_secret}")
    
    # Generate the AES key with the help of Shared Secret
    aes_key = generate_aes_key(shared_secret)
    print("Secure communication established with AES encryption!")
    return aes_key

def encrypt_message(aes_key, message):
    # Generate the Cipher Text
    cipher = AES.new(aes_key, AES.MODE_CBC)
    
    # Padding according to the block
    ct_bytes = cipher.encrypt(pad(message.encode(), AES.block_size))
    return cipher.iv + ct_bytes

def decrypt_message(aes_key, ciphertext):
    iv = ciphertext[:AES.block_size]
    ct = ciphertext[AES.block_size:]
    cipher = AES.new(aes_key, AES.MODE_CBC, iv)
    
    # Decryption of the cipher text received and return the same
    decrypted = unpad(cipher.decrypt(ct), AES.block_size)
    return decrypted.decode()

def receive_messages(rec_socket, aes_key):
    try:
        while True:
            encrypted_message = rec_socket.recv(1024)
            if encrypted_message == b"EOM":
                print("\n[Chat Ended]")
                break
            print(f"\n[Encrypted Ciphertext]: {encrypted_message.hex()}")
            decrypted_message = decrypt_message(aes_key, encrypted_message)
            print(f"\n[Received]: {decrypted_message}\n[Send]: ", end="", flush=True)
            
    # Handle invalid input from the user
    except:
        print("\n[ERROR] Connection lost.")
        
    finally:
        rec_socket.close()

def send_messages(rec_socket, aes_key):
    try:
        while True:
            # decode the msg in utf format and strip to remove leading or trailing spaces
            msg_to_send = input("[Send]: ").strip()
            encrypted_message = encrypt_message(aes_key, msg_to_send)
            rec_socket.send(encrypted_message)
            
            # If user wants to end the chat
            if msg_to_send == "EOM":
                print("\n[Chat Ended]")
                break
                
    except:
        print("\n[ERROR] Connection lost.")
        
    finally:
        rec_socket.close()

def start_chat_among_peers(rec_socket):
    global chat_active
    chat_active = True
    
    # Key exchange before the starting the chat (if both users accepts the chat request)
    aes_key = key_exchange(rec_socket)

    print("\n[INFO] Chat started. Type 'EOM' to end.")
    
    recv_thread = threading.Thread(target=receive_messages, args=(rec_socket, aes_key))
    send_thread = threading.Thread(target=send_messages, args=(rec_socket, aes_key))
    
    # Threads to handle multiple users
    recv_thread.start() 
    send_thread.start()
    
    recv_thread.join()
    send_thread.join()
    
    chat_active = False

def listen_p2p(listen_port):
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(("0.0.0.0", listen_port))
    listen_socket.listen(5)

    print(f"\n[LISTEN] Waiting for incoming P2P chat on port {listen_port}...")

    # When you get the incoming request from any user then accept it and put into the connections queue
    while True:
        client_socket, addr = listen_socket.accept()
        print(f"\n[INCOMING] P2P chat request from {addr}")
        print(f"\nPress Enter To Accept The Connection Request")
        incoming_connections.put(client_socket)  # Add the connection to the queue

def start_client():
    global chat_active
    # Start the socket to connect with the server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 10001))  # Connect to server

    # Get the username to chat with and send request to the mentioned user
    print(client.recv(1024).decode())
    username = input("Enter your username: ").strip()
    client.send(username.encode())

    response = client.recv(1024).decode()
    if response.startswith("Username already in use"):
        print(response)
        client.close()
        return

    print("[CONNECTED] Enter your P2P listening port:")
    listen_port = int(input().strip())

    # Notify server of listening port
    client.send(f"LISTEN_PORT:{listen_port}".encode())
    print(client.recv(1024).decode())

    # Start P2P listener in a background thread to accept other connections
    threading.Thread(target=listen_p2p, args=(listen_port,), daemon=True).start()

    while True:
        # Check if there is an incoming connection
        if not incoming_connections.empty():
            rec_socket = incoming_connections.get()
            start_chat_among_peers(rec_socket)
            
        # If no other chat is active then show the Main Commands to the user
        if not chat_active:
            print("\nCommands: [1] Get Users  [2] EXIT")
            command = input("Enter command: ").strip()
            
            # If the user sends Get Users, send back the user list to the user
            if command == "Get Users":
                client.send(command.encode())
                user_list = client.recv(1024).decode()
                
                # If list is empty
                if "No users available" in user_list:
                    print("\nNo other users available.")
                else:
                    # Print all the connected users
                    print("\nConnected Users:\n" + user_list)
                    target_user = input("Enter username to chat with: ").strip()

                    # Extract IP and port of the selected user
                    rec_ip, rec_port = None, None
                    for line in user_list.split("\n"):
                        info = line.split()
                        if len(info) == 3 and info[0] == target_user:
                            rec_ip, rec_port = info[1], int(info[2])
                            break

                    if rec_ip and rec_port:
                        print(f"\n[CONNECTING] {target_user} at {rec_ip}:{rec_port}")
                        try:
                            rec_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            rec_socket.connect((rec_ip, rec_port))
                            start_chat_among_peers(rec_socket)
                            
                        except ConnectionRefusedError:
                            print(f"[ERROR] {target_user} is not available.")
                            
                    else:
                        print("[ERROR] User not found.")
                        
            elif command == "EXIT":
                client.send(command.encode())
                print("\n[INFO] Disconnecting from server...")
                client.close()
                break

# Run the client
start_client()