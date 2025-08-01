import socket
import threading
from colorama import init, Fore
from datetime import datetime
import argparse

init(autoreset=True)

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def receive_messages(sock):
    reader = sock.makefile('r', encoding='utf-8', errors='replace')
    while True:
        try:
            msg = reader.readline().strip()
            if not msg:
                break
            if msg.lower() == 'quit':
                print(Fore.RED + f"🛑 [{timestamp()}] Server ended the chat.")
                break
            print(Fore.YELLOW + f"{msg}")
        except Exception as e:
            print(Fore.RED + f"💥 Error: {e}")
            break

def start_client(host, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    print(Fore.GREEN + f"✅ [{timestamp()}] Connected to server at {host}:{port}")

    nickname = input(Fore.BLUE + "✨ Enter your nickname: " + Fore.RESET).strip() or "Guest"
    sock.sendall(f"NICK:{nickname}\n".encode('utf-8'))

    thread = threading.Thread(target=receive_messages, args=(sock,))
    thread.start()

    try:
        while True:
            msg = input(Fore.MAGENTA + f"👤 You ({nickname}) ➤ " + Fore.RESET)
            if msg.strip().lower() == 'quit':
                sock.sendall('quit\n'.encode('utf-8'))
                break
            sock.sendall((msg + '\n').encode('utf-8'))
    except KeyboardInterrupt:
        print(Fore.RED + "\n🛑 Interrupted by user")
    finally:
        sock.close()
        print(Fore.RED + f"🔴 [{timestamp()}] Disconnected from server")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    start_client(args.host, args.port)
