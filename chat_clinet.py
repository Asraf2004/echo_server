import socket
import threading
from datetime import datetime
from colorama import init, Fore

init(autoreset=True)

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def receive(sock):
    while True:
        try:
            msg = sock.recv(1024).decode().strip()
            if not msg:
                break
            print(Fore.YELLOW + msg)
        except:
            break

def start_client():
    nickname = input("✨ Enter your nickname: ").strip() or "Guest"
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 5000))
    sock.sendall((nickname + '\n').encode())

    threading.Thread(target=receive, args=(sock,), daemon=True).start()

    while True:
        msg = input(Fore.CYAN + f"{nickname} ➤ " + Fore.RESET)
        if msg.lower() == "quit":
            sock.sendall(b'quit\n')
            break
        sock.sendall((msg + '\n').encode())

    sock.close()
    print(Fore.RED + "🚪 Disconnected from server")

if __name__ == "__main__":
    import os
    os.system("")  # Enables ANSI on Windows without chcp
    start_client()
