import socket
import threading
from colorama import init, Fore
from datetime import datetime

init(autoreset=True)

nickname = input(Fore.BLUE + "✨ Enter your nickname: " + Fore.RESET) or "Guest"

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode().strip()
            if not msg:
                break
            if msg.lower() == 'quit':
                print(Fore.RED + f"🛑 [{timestamp()}] Server disconnected")
                break
            print(Fore.YELLOW + f"🖥️ Server ➤ " + Fore.RESET + msg)
        except ConnectionResetError:
            print(Fore.RED + f"💥 [{timestamp()}] Server disconnected unexpectedly")
            break

def start_client():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5000))
    print(Fore.GREEN + f"✅ [{timestamp()}] Connected to server")

    thread = threading.Thread(target=receive_messages, args=(sock,))
    thread.start()

    try:
        while True:
            msg = input(Fore.MAGENTA + f"👤 You ({nickname}) ➤ " + Fore.RESET)
            sock.sendall((msg + '\n').encode())
            if msg.lower() == 'quit':
                break
    finally:
        sock.close()
        print(Fore.RED + f"🔴 [{timestamp()}] Disconnected")

if __name__ == "__main__":
    start_client()