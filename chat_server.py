import socket
import threading
from colorama import init, Fore
from datetime import datetime
import argparse

init(autoreset=True)

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def receive_messages(conn, addr, nickname):
    reader = conn.makefile('r')
    while True:
        try:
            msg = reader.readline().strip()
            if not msg:
                break
            if msg.lower() == 'quit':
                print(Fore.RED + f"🛑 [{timestamp()}] {nickname} disconnected")
                break
            print(Fore.CYAN + f"[{timestamp()}] {nickname} ➤ {msg}")
        except Exception as e:
            print(Fore.RED + f"💥 Error: {e}")
            break

def start_server(host, port):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(1)

    print(Fore.YELLOW + f"🕒 [{timestamp()}] Waiting for connection on {host}:{port}...")
    conn, addr = server.accept()
    print(Fore.GREEN + f"✅ [{timestamp()}] Connected with {addr}")

    # Receive nickname
    nickname = conn.recv(1024).decode().strip().replace("NICK:", "") or "Client"

    # Start thread to receive messages
    thread = threading.Thread(target=receive_messages, args=(conn, addr, nickname))
    thread.start()

    try:
        while True:
            msg = input(Fore.MAGENTA + f"💻 You (Server) ➤ " + Fore.RESET)
            if msg.strip().lower() == 'quit':
                conn.sendall('quit\n'.encode())
                break
            conn.sendall((msg + '\n').encode())
    except KeyboardInterrupt:
        print(Fore.RED + "\n🛑 Interrupted by user")
    finally:
        conn.close()
        server.close()
        print(Fore.RED + f"🔴 [{timestamp()}] Server closed")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", default="localhost")
    parser.add_argument("--port", type=int, default=5000)
    args = parser.parse_args()
    start_server(args.host, args.port)
