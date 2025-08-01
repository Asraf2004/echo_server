import socket
import threading
from colorama import init, Fore
from datetime import datetime

init(autoreset=True)

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def receive_messages(conn):
    while True:
        try:
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break
            if msg.lower() == 'quit':
                print(Fore.RED + f"🛑 [{timestamp()}] Client disconnected")
                break
            print(Fore.CYAN + f"👤 Client ➤ " + Fore.RESET + msg)
        except ConnectionResetError:
            print(Fore.RED + f"💥 [{timestamp()}] Client disconnected unexpectedly")
            break

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 5000))
    server.listen(1)

    print(Fore.YELLOW + f"🕒 [{timestamp()}] Waiting for connection...")
    conn, addr = server.accept()
    print(Fore.GREEN + f"✅ [{timestamp()}] Connected with {addr}")

    thread = threading.Thread(target=receive_messages, args=(conn,))
    thread.start()

    try:
        while True:
            msg = input(Fore.MAGENTA + "💻 You (Server) ➤ " + Fore.RESET)
            conn.sendall((msg + '\n').encode())
            if msg.lower() == 'quit':
                break
    finally:
        conn.close()
        server.close()
        print(Fore.RED + f"🔴 [{timestamp()}] Server closed")

if __name__ == "__main__":
    start_server()