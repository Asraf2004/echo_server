import socket
import threading
from colorama import init, Fore
from datetime import datetime

init(autoreset=True)

clients = {}  # {conn: nickname}
lock = threading.Lock()

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def broadcast(sender_conn, message):
    with lock:
        for conn in clients:
            if conn != sender_conn:
                try:
                    conn.sendall((message + '\n').encode('utf-8'))
                except:
                    pass

def handle_client(conn, addr):
    try:
        nickname = conn.recv(1024).decode('utf-8', errors='replace').strip().replace("NICK:", "") or f"Client{addr[1]}"
        with lock:
            clients[conn] = nickname
        print(Fore.GREEN + f"✅ [{timestamp()}] {nickname} connected from {addr}")

        welcome = f"👋 {nickname} has joined the chat!"
        broadcast(conn, f"[{timestamp()}] {welcome}")
        conn.sendall(f"[{timestamp()}] ✅ Connected to chat server\n".encode('utf-8'))

        reader = conn.makefile('r', encoding='utf-8', errors='replace')
        while True:
            msg = reader.readline().strip()
            if not msg:
                break
            if msg.lower() == 'quit':
                break
            print(Fore.CYAN + f"[{timestamp()}] {nickname} ➤ {msg}")
            broadcast(conn, f"[{timestamp()}] {nickname} ➤ {msg}")
    except Exception as e:
        print(Fore.RED + f"💥 [{timestamp()}] Error with client {addr}: {e}")
    finally:
        with lock:
            left_nick = clients.pop(conn, "Unknown")
        print(Fore.RED + f"🔌 [{timestamp()}] {left_nick} disconnected")
        broadcast(conn, f"[{timestamp()}] ❌ {left_nick} left the chat.")
        conn.close()

def start_server(host='localhost', port=5000):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen()
    print(Fore.YELLOW + f"🚀 [{timestamp()}] Server started on {host}:{port}. Waiting for clients...")

    try:
        while True:
            conn, addr = server.accept()
            thread = threading.Thread(target=handle_client, args=(conn, addr))
            thread.start()
    except KeyboardInterrupt:
        print(Fore.RED + "\n🛑 Server interrupted by user")
    finally:
        with lock:
            for conn in list(clients.keys()):
                conn.close()
        server.close()
        print(Fore.RED + f"🔒 [{timestamp()}] Server closed")

if __name__ == "__main__":
    start_server()
