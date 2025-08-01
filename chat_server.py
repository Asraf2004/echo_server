import socket
import threading
from datetime import datetime
from colorama import init, Fore

init(autoreset=True)

clients = {}  # nickname -> connection

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def broadcast(msg, exclude_conn=None):
    for conn in clients.values():
        if conn != exclude_conn:
            try:
                conn.sendall(msg.encode())
            except:
                pass  # Ignore broken pipes

def handle_client(conn, addr):
    try:
        nickname = conn.recv(1024).decode().strip()
        clients[nickname] = conn
        welcome = f"✅ [{timestamp()}] {nickname} joined the chat.\n"
        print(Fore.GREEN + welcome.strip())
        broadcast(welcome, exclude_conn=conn)

        # Send list of online users
        user_list = "📋 Online Users: " + ", ".join(clients.keys()) + "\n"
        conn.sendall(user_list.encode())

        while True:
            msg = conn.recv(1024).decode().strip()
            if not msg:
                break
            if msg.lower() == "quit":
                break
            if msg.startswith("/pm "):
                parts = msg.split(' ', 2)
                if len(parts) == 3:
                    target, message = parts[1], parts[2]
                    if target in clients:
                        try:
                            clients[target].sendall(
                                f"🔒 [Private from {nickname}] {message}\n".encode()
                            )
                            conn.sendall(f"🔒 [Private to {target}] {message}\n".encode())
                        except:
                            conn.sendall(f"❌ Failed to send to {target}\n".encode())
                    else:
                        conn.sendall(f"❌ User {target} not found\n".encode())
                else:
                    conn.sendall("⚠️ Usage: /pm <nickname> <message>\n".encode())
            else:
                formatted = f"[{timestamp()}] {nickname} ➤ {msg}\n"
                print(Fore.CYAN + formatted.strip())
                broadcast(formatted, exclude_conn=conn)
    except:
        pass
    finally:
        conn.close()
        if nickname in clients:
            del clients[nickname]
            goodbye = f"🔴 [{timestamp()}] {nickname} left the chat.\n"
            broadcast(goodbye)
            print(Fore.RED + goodbye.strip())

def start_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 5000))
    sock.listen()
    print(Fore.YELLOW + f"🟢 [{timestamp()}] Server started on port 5000")

    threading.Thread(target=admin_console, daemon=True).start()

    while True:
        conn, addr = sock.accept()
        threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()

def admin_console():
    while True:
        cmd = input(Fore.MAGENTA + "🛠️ Server CMD ➤ " + Fore.RESET).strip()
        if cmd == "quit":
            print(Fore.RED + "🔻 Shutting down server...")
            broadcast("🔻 Server is shutting down.\n")
            for conn in clients.values():
                try:
                    conn.close()
                except:
                    pass
            break
        elif cmd == "users":
            print("👥 Online Users:", ', '.join(clients.keys()))
        else:
            print("❓ Unknown command. Use: quit | users")

if __name__ == "__main__":
    import os
    os.system("")  # Enables ANSI on Windows without chcp
    start_server()

