# import the socket library
import socket
from collections import deque

def calculate_result(expression: str) -> str:
    all_operands = deque()   # Stores numbers
    all_operators = deque()  # Stores operators
    
    i = 0
    input_flag = True  # True = Operand, False = Operator
    
    while i < len(expression):
        if input_flag:
            number = ""
            while i < len(expression) and expression[i] != ' ':
                number += expression[i]
                i += 1
            current_operand = float(number)

            # Handle *, /, %
            if all_operators and all_operators[-1] in {'*', '/', '%'}:
                op = all_operators.pop()
                left_operand = all_operands.pop()

                if op == '*':
                    all_operands.append(left_operand * current_operand)
                elif op == '/':
                    all_operands.append(left_operand / current_operand)
                elif op == '%':
                    all_operands.append(int(left_operand) % int(current_operand))
            else:
                all_operands.append(current_operand)
        else:
            all_operators.append(expression[i])
            i += 1

        input_flag = not input_flag
        i += 1  # Skip space
    
    # Reverse stacks to evaluate + and - from left to right
    all_operands = deque(reversed(all_operands))
    all_operators = deque(reversed(all_operators))

    answer = all_operands.pop()

    while all_operands and all_operators:
        curr = all_operands.pop()
        op = all_operators.pop()

        if op == '+':
            answer += curr
        elif op == '-':
            answer -= curr

    return f"{answer}"


def start_server():
    # Create server socket
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    # Set the IP and Port of the Server
    server_ip = "0.0.0.0"
    server_port = 11000
    
    # Bind the socket to the specified IP and Port
    server_socket.bind((server_ip, server_port))
    
    # Listen for incoming connection connection requests
    server_socket.listen(5)
    print(f"Listening on {server_ip}: {server_port}")
    
    # Accept the incoming connection request
    client_socket, client_address = server_socket.accept()
    print(f"Client with IP: {client_address[0]} and Port: {client_address[1]}")
    client_socket.send("Connection Established. Enter an expression or type 'END' to quit.".encode("utf-8"))
    
    print("")
    
    # Receive the expression from the client
    while True:
        expression = client_socket.recv(1024).decode("utf-8")
        print(f"Expression: {expression}")
        
        if expression.upper().strip() == "END":
            break
        # Evaluate the expression
        result = calculate_result(expression)
        client_socket.send(result.encode())
        
    client_socket.close()
    server_socket.close()

start_server()