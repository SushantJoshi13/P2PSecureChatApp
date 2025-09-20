import socket
import threading

connected_clients = {}  # Stores username -> (IP, listening port)

def handle_client(client_socket, ip, username):
    """Handles communication with a connected client."""
    try:
        while True:
            request = client_socket.recv(1024).decode().strip()

            if request.startswith("LISTEN_PORT:"):
                # Store the listening port of the user
                listen_port = int(request.split(":")[1])
                connected_clients[username] = (ip, listen_port)
                client_socket.send("Listening port registered.".encode())

            elif request == "Get Users":
                user_list = ""
                for u, data in connected_clients.items():
                    if u != username:
                        user_list += f"{u} {data[0]} {data[1]}\n"

                # Send user list or message if no users are available
                if user_list:
                    client_socket.send(user_list.encode())
                else:
                    client_socket.send("No users available.".encode())

                # Send user list or message if no users are available
                client_socket.send(user_list.encode() if user_list else "No users available.".encode())

            elif request == "EXIT":
                print(f"[INFO] {username} disconnected.")
                # Remove the user from the connected clients list
                del connected_clients[username]
                break

            else:
                # Handle invalid requests
                client_socket.send("Invalid request".encode())

    except Exception as e:
        print(f"[ERROR] Connection error with {username}: {e}")
    finally:
        # Close the client socket
        client_socket.close()

def run_server():
    """Runs the central server for client registration."""
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
            # Ask for the listening port and inform the client
            client_socket.send("Welcome! Please send your listening port.".encode())
            # Start a new thread to handle this client
            threading.Thread(target=handle_client, args=(client_socket, ip, username)).start()

run_server()
