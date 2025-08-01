import socket

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5000))
    server.listen(1)
    
    print("Waiting for a connection")
    connection, client_address = server.accept()
    print("Connection established:", client_address)
    
    try:
        buffer = ""
        while True:
            data = connection.recv(1024)
            if not data:
                break
            
            buffer += data.decode()
            # Process messages in the buffer
            while '\n' in buffer:
                # Split the buffer by newline characters

                parts = buffer.split('\n')
              
                for part in parts[:-1]:
                    message = part.strip()
                    if message.lower() == 'quit':
                        print("Client requested to quit.")
                        connection.sendall(message.encode())
                        return
                    print("Received:", message)
                    connection.sendall(("echo >"+ message + '\n\r').encode())
                buffer = parts[-1]  # Keep any incomplete message in the buffer
    finally:
        connection.close()
        server.close()

if __name__ == "__main__":
    start_server()
 
