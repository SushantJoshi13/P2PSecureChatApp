import socket
import threading
import os
import random
import queue #To maintain the queue of the incoming connections

# Libraries to implement AES
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
from hashlib import sha256

chat_active = False #For showing that the P2P Connection is Active or Not
incoming_connections = queue.Queue() #Queue

# Step 1: Read p and g from environment variables
p = int(os.getenv("P", "23"))  # Prime number (default small value for testing)
g = int(os.getenv("Q", "5"))   # Generator (default)

a = random.randint(2, p - 2)  # Private key
A = pow(g, a, p)  # Public key

chat_active = False  # Global flag to prevent command menu during chat

def generate_aes_key(shared_secret):
    return sha256(str(shared_secret).encode()).digest()

def key_exchange(rec_socket):
    """Performs Diffie-Hellman key exchange before chat starts."""
    rec_socket.send(str(A).encode())  # Send public key A
    B = int(rec_socket.recv(1024).decode())  # Receive peer's public key B
    KSC = pow(B, a, p)  # Compute shared secret key
    print(f"Private Key (a): {a}")
    print(f"Public Key (A): {A}")
    print(f"Shared Secret Key Computed: {KSC}")
    print("Secure communication established!")
    
    aes_key = generate_aes_key(KSC)
    print(f"AES key: {aes_key}")
    print("Secure communication established with AES encryption!")
    return aes_key

#Function to receive messages in the p2p mode
def receive_messages(rec_socket):
    try:
        while True:
            msg_received = rec_socket.recv(1024).decode() # Message received
            if msg_received == "EOM": # If End Of Message then End the Chat
                print("\n[Chat Ended]")
                break
            print(f"\n[Received]: {msg_received}\n[Send]: ", end="", flush=True) # Print the received message and enable send function
            #flush = True for the print Send every time it receives the message to show chat more sophisticated.
            
    except:
        print("\n[ERROR] Connection lost.") #Handle Exception
        
    finally:
        rec_socket.close() #Close Socket

def send_messages(rec_socket):
    try:
        while True:
            msg_to_send = input("[Send]: ").strip() #Send the Message
            rec_socket.send(msg_to_send.encode())
            if msg_to_send == "EOM": # If End Of Message then End the Chat
                print("\n[Chat Ended]")
                break
                
    except:
        print("\n[ERROR] Connection lost.") #Handle Exception
        
    finally:
        rec_socket.close() #Close Socket

#Start the p2p chat between 2 parties
def start_p2p_chat(rec_socket):
    global chat_active
    chat_active = True  # Prevent command menu
    
    # Perform key exchange before chat starts
    key_exchange(rec_socket)

    print("\n[INFO] Chat started. Type 'EOM' to end.")
    
    recv_thread = threading.Thread(target=receive_messages, args=(rec_socket,)) #Make receive thread
    send_thread = threading.Thread(target=send_messages, args=(rec_socket,)) #Make Send Thread
    
    #Start the threads
    
    recv_thread.start() 
    send_thread.start()
    
    #Wait until the P2P connection is active
    
    recv_thread.join()
    send_thread.join()
    
    chat_active = False #Make false as we ended the chat

#Start Listening on the port

def listen_p2p(listen_port):
    # Start the Listen Socket
    
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(("0.0.0.0", listen_port))
    listen_socket.listen(1)

    print(f"\n[LISTEN] Waiting for incoming P2P chat on port {listen_port}...")

    #When you get the incoming request from any user then accept it and put into the connections queue
    
    while True:
        client_socket, addr = listen_socket.accept()
        print(f"\n[INCOMING] P2P chat request from {addr}")
        print(f"\nPress Enter To Accept The Connection Request")
        incoming_connections.put(client_socket)

#Main function of Client

def run_client():
    global chat_active
    #Start the socket to connect with the server
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("127.0.0.1", 10000))  # Connect to server

    print(client.recv(1024).decode())  # Server asks for username
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
            start_p2p_chat(rec_socket)
            
        #If no other chat is active then show the Main Commmands to the user
        
        if not chat_active:
            print("\nCommands: [1] Get Users  [2] EXIT")
            command = input("Enter command: ").strip()
            
            #If the user send Get Users send back the user list to the user
            if command == "Get Users":
                client.send(command.encode())
                user_list = client.recv(1024).decode()
                
                #If list is empty
                if "No users available" in user_list:
                    print("\nNo other users available.")
                else:
                    #Print all the connected users
                    print("\nConnected Users:\n" + user_list)
                    target_user = input("Enter username to chat with: ").strip()

                    # Extract IP and port of the  selected user
                    rec_ip, rec_port = None, None
                    for line in user_list.split("\n"):
                        info = line.split()
                        if len(info) == 3 and info[0] == target_user:
                            rec_ip, rec_port = info[1], int(info[2])
                            break

                    if rec_ip and rec_port:
                        print(f"\n[CONNECTING] {target_user} at {rec_ip}:{rec_port}")
                        try:
                            #start p2p chat with the target user and make socket for the p2p chat.
                            rec_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            rec_socket.connect((rec_ip, rec_port))
                            start_p2p_chat(rec_socket)
                            
                        #If anything goes wrong Handle the exception
                        except ConnectionRefusedError:
                            print(f"[ERROR] {target_user} is not available.")
                            
                    #No user found
                    else:
                        print("[ERROR] User not found.")
                        
            #If User want to exit the program
            elif command == "EXIT":
                client.send(command.encode())
                print("\n[INFO] Disconnecting from server...")
                client.close()
                break

run_client()
