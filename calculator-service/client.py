# import socket library
import socket


def start_client():
    # Create Client socket with IPv4 and TCP
    client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    
    # Connect the client and server socket with the help of IP and Port
    # Here we are using static port 10001
    client_socket.connect(("127.0.0.1", 11000))
    
    # Receive connection confirmation message from server
    confirm_connection_msg = client_socket.recv(1024)
    print(confirm_connection_msg.decode("utf-8"))
        
    while True:
        # Get the input from the client and send it to the server to get the result
        expression = input("[INPUT]  " )
        client_socket.send(expression.encode("utf-8"))
        if expression.upper().strip() == "END":
            break
        
        # Get result and print
        result = client_socket.recv(1024).decode("utf-8")
        print(f"[OUTPUT] {result}")
        
    client_socket.close()


# Start the client when new user connects
start_client()