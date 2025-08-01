import socket
import threading
import logging
import os
from colorama import Fore, init, Style
from datetime import datetime

init(autoreset=True)

# Logging config
logging.basicConfig(filename='chat.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Global server data
clients = {}  # nickname -> conn
addresses = {}  # conn -> nickname
colors = [Fore.BLUE, Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.RED]

def get_color(nick):
    return colors[hash(nick) % len(colors)]

def timestamp():
    return datetime.now().strftime('%H:%M:%S')

def broadcast(msg, exclude=None):
    for nick, conn in clients.items():
        if conn != exclude:
            try:
                conn.sendall((msg + '\n').encode())
            except:
                pass

def send_user_list():
    user_list = ", ".join(clients.keys())
    msg = f"👥 Users Online: {user_list}"
    logging.info(msg)
    print(Fore.LIGHTBLACK_EX + msg)
    broadcast(Fore.LIGHTBLACK_EX + msg)

def private_message(sender, target_nick, message):
    if target_nick in clients:
        try:
            formatted = f"🔒 [Private] {sender} ➤ {message}"
            clients[target_nick].sendall((formatted + '\n').encode())
            clients[sender].sendall((formatted + '\n').encode())
            logging.info(f"[PM] {sender} ➤ {target_nick}: {message}")
        except:
            pass
    else:
        clients[sender].sendall(f"❌ User '{target_nick}' not found.\n".encode())
        print(Fore.RED + f"❌ Private message failed: '{target_nick}' not found.")

def handle_client(conn, addr):
    try:
        conn.sendall("Enter your nickname: ".encode())
        nickname = conn.recv(1024).decode().strip()
        if not nickname:
            nickname = f"Guest{addr[1]}"

        clients[nickname] = conn
        addresses[conn] = nickname

        logging.info(f"{nickname} connected from {addr}")
        welcome_msg = f"🎉 [{timestamp()}] {nickname} joined the chat!"
        print(get_color(nickname) + welcome_msg)
        broadcast(get_color(nickname) + welcome_msg, exclude=conn)
        send_user_list()

        while True:
            data = conn.recv(1024)
            if not data:
                break
            msg = data.decode().strip()

            if msg.lower() == "/quit":
                break

            if msg.startswith("/pm"):
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    conn.sendall("Usage: /pm <user> <message>\n".encode())
                else:
                    _, target_nick, pm_msg = parts
                    private_message(nickname, target_nick, pm_msg)
            else:
                formatted = f"[{timestamp()}] {nickname} ➤ {msg}"
                color_msg = get_color(nickname) + formatted
                logging.info(f"{nickname}: {msg}")
                print(color_msg)
                broadcast(color_msg, exclude=conn)

    except Exception as e:
        logging.error(f"Error with {addr}: {e}")

    finally:
        if conn in addresses:
            nickname = addresses[conn]
            del addresses[conn]
            if nickname in clients:
                del clients[nickname]
                leave_msg = f"❌ {nickname} has left the chat."
                print(Fore.RED + leave_msg)
                broadcast(Fore.RED + leave_msg)
                send_user_list()
        conn.close()
        logging.info(f"Connection with {addr} closed.")

def accept_connections(server):
    while True:
        try:
            conn, addr = server.accept()
            print(Fore.YELLOW + f"🔌 Connection from {addr}")
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except OSError:
            break

if __name__ == "__main__":
    os.system("chcp 65001 >nul")  # Windows-only: set UTF-8

    HOST = '0.0.0.0'
    PORT = 12345

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(Fore.CYAN + f"🚀 Server started on {HOST}:{PORT}. Type 'exit' to stop.")
    logging.info("Server started.")

    threading.Thread(target=accept_connections, args=(server,), daemon=True).start()

    while True:
        cmd = input()
        if cmd.strip().lower() == 'exit':
            break

    print(Fore.RED + "🛑 Shutting down server...")
    logging.info("Server shutting down.")
    for conn in list(addresses):
        try:
            conn.sendall("Server is shutting down. Bye!\n".encode())
            conn.close()
        except:
            pass
    server.close()
