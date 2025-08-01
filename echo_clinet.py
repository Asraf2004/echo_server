import socket

def start_client():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 5000))

    try:
        while True:
            msg = input("You: ")
            client.sendall((msg + '\n').encode())  # newline signals end of message
            if msg.lower() == 'quit':
                break
            response = client.recv(1024).decode().strip()
            print("Server:", response)
    finally:
        client.close()

if __name__ == "__main__":
    start_client()
