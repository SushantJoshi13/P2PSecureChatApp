import socket
import threading

connected_clients = {}

# Function to handle the client requests and its connections
def handle_client(client_socket, ip, username):
    try:
        while True:
            request = client_socket.recv(1024).decode().strip()

            if request.startswith("LISTEN_PORT:"):
                listen_port = int(request.split(":")[1])
                connected_clients[username] = (ip, listen_port)
                client_socket.send("Listening port registered.".encode())

            elif request == "Get Users":
                user_list = ""
                for u, data in connected_clients.items():
                    if u != username:
                        user_list += f"{u} {data[0]} {data[1]}\n"

                # List of users is sent to the client requesting it if more users exist
                if user_list:
                    client_socket.send(user_list.encode())
                else:
                    client_socket.send("No users available.".encode())

                client_socket.send(user_list.encode() if user_list else "No users available.".encode())

            elif request == "EXIT":
                print(f"[INFO] {username} disconnected.")
                # If client gets disconnected then remove it from the list of active clients
                del connected_clients[username]
                break

            else:
                client_socket.send("Invalid request".encode())

    except Exception as e:
        print(f"[ERROR] Connection error with {username}: {e}")
    finally:
        client_socket.close()

def start_server():
    # Create and configure the server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 10000))
    server_socket.listen(5)

    print("[SERVER] Listening on port 10000...")

    while True:
        # Accept incoming client connection
        client_socket, (ip, _) = server_socket.accept()

        # Ask for username from the client
        client_socket.send("Enter your username:".encode())
        username = client_socket.recv(1024).decode().strip()

        if username in connected_clients:
            # If username is already taken, inform the client and close connection
            client_socket.send("Username already in use. Try again.".encode())
            client_socket.close()
        else:
            print(f"[NEW USER] {username} connected from {ip}")
            # Request user to enter port number on which it wants to connect
            client_socket.send("Welcome! Please send your listening port.".encode())
            # New thread is created for every client
            threading.Thread(target=handle_client, args=(client_socket, ip, username)).start()

start_server()
