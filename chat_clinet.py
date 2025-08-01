import socket
import threading
from colorama import init, Fore
from datetime import datetime

init(autoreset=True)

nickname = input("Enter your nickname 👤: ") or "Client 🔓"

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode().strip()
            if msg.lower() == 'quit':
                print(Fore.RED + f"[{timestamp()}] Server disconnected ❌")
                break
            print(Fore.GREEN + f"[{timestamp()}] Server 📨: " + Fore.RESET + msg)
        except:
            break

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5000))
    print(Fore.YELLOW + f"[{timestamp()}] Connected to server ✅")

    thread = threading.Thread(target=receive_messages, args=(sock,))
    thread.start()

    try:
        while True:
            msg = input(Fore.BLUE + f"[{nickname}] You 🗣️: " + Fore.RESET)
            sock.sendall((msg + '\n').encode())
            if msg.lower() == 'quit':
                break
    finally:
        sock.close()

if __name__ == "__main__":
    start_client()
