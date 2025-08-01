import socket
import threading
from colorama import init, Fore
from datetime import datetime

init(autoreset=True)

nickname = "Server 🔰"

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def receive_messages(conn):
    while True:
        try:
            msg = conn.recv(1024).decode().strip()
            if msg.lower() == 'quit':
                print(Fore.RED + f"[{timestamp()}] [Client] disconnected ❌")
                break
            print(Fore.GREEN + f"[{timestamp()}] Client 📨: " + Fore.RESET + msg)
        except:
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5000))
    server.listen(1)

    print(Fore.CYAN + f"[{timestamp()}] Waiting for connection...")
    conn, addr = server.accept()
    print(Fore.YELLOW + f"[{timestamp()}] Connected with {addr} ✅")

    thread = threading.Thread(target=receive_messages, args=(conn,))
    thread.start()

    try:
        while True:
            msg = input(Fore.BLUE + f"[{nickname}] You 🗣️: " + Fore.RESET)
            conn.sendall((msg + '\n').encode())
            if msg.lower() == 'quit':
                break
    finally:
        conn.close()
        server.close()

if __name__ == "__main__":
    start_server()
