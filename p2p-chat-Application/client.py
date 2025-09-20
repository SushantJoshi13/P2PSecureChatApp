import socket
import threading
import queue

chat_active = False
incoming_connections = queue.Queue()

# Function to receive messages in the p2p mode
def receive_messages(rec_socket):
    try:
        while True:
            msg_received = rec_socket.recv(1024).decode()
            if msg_received == "EOM":
                print("\n[Chat Ended]")
                break
            print(f"\n[Received]: {msg_received}\n[Send]: ", end="", flush=True)
            
    except:
        print("\n[ERROR] Connection lost.")
        
    finally:
        rec_socket.close()

def send_messages(rec_socket):
    try:
        while True:
            msg_to_send = input("[Send]: ").strip()
            rec_socket.send(msg_to_send.encode())
            if msg_to_send == "EOM":
                print("\n[Chat Ended]")
                break
                
    except:
        print("\n[ERROR] Connection lost.")
        
    finally:
        rec_socket.close()

def start_p2p_chat(rec_socket):
    global chat_active
    chat_active = True

    print("\n[INFO] Chat started. Type 'EOM' to end.")
    
    recv_thread = threading.Thread(target=receive_messages, args=(rec_socket,))
    send_thread = threading.Thread(target=send_messages, args=(rec_socket,))
    
    # Threads are created for the client to send and receive the messages    
    recv_thread.start() 
    send_thread.start()
    
    # Client joins the created threads    
    recv_thread.join()
    send_thread.join()
    
    chat_active = False

def listen_p2p(listen_port):    
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.bind(("0.0.0.0", listen_port))
    listen_socket.listen(1)

    print(f"\n[LISTEN] Waiting for incoming P2P chat on port {listen_port}...")

    while True:
        client_socket, addr = listen_socket.accept()
        print(f"\n[INCOMING] P2P chat request from {addr}")
        print(f"\nPress Enter To Accept The Connection Request")
        incoming_connections.put(client_socket)

def start_client():
    global chat_active
    #Start the socket to connect with the server
    
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(("172.21.135.94", 10000))  # Connect to server

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
                    #Print all the connected users if available
                    print("\nConnected Users:\n" + user_list)
                    target_user = input("Enter username to chat with: ").strip()

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
                            start_p2p_chat(rec_socket)
                            
                        except ConnectionRefusedError:
                            print(f"[ERROR] {target_user} is not available.")
                            
                    else:
                        print("[ERROR] User not found.")
                        
            # EXIT from the chat
            elif command == "EXIT":
                client.send(command.encode())
                print("\n[INFO] Disconnecting from server...")
                client.close()
                break

start_client()
