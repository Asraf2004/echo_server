import socket
import threading
import logging
import os
from colorama import Fore, init
from datetime import datetime

init(autoreset=True)

# Logging configuration
logging.basicConfig(filename='chat.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

clients = {}  # nickname -> conn
addresses = {}  # conn -> nickname
join_info = {}  # nickname -> (ip, join_time)
colors = [Fore.BLUE, Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.RED, Fore.WHITE]

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

def show_user_info(requester, target_nick):
    if target_nick in join_info:
        ip, join_time = join_info[target_nick]
        info_msg = f"🧠 Info for '{target_nick}': IP = {ip}, Joined at = {join_time}"
        try:
            clients[requester].sendall((info_msg + '\n').encode())
        except:
            pass
    else:
        clients[requester].sendall(f"❌ No info found for '{target_nick}'\n".encode())

def handle_client(conn, addr):
    try:
        conn.sendall("Enter your nickname: ".encode())
        nickname = conn.recv(1024).decode().strip()
        if not nickname:
            nickname = f"Guest{addr[1]}"

        clients[nickname] = conn
        addresses[conn] = nickname
        join_info[nickname] = (addr[0], timestamp())

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

            elif msg.lower() == "/who":
                user_list = ", ".join(clients.keys())
                conn.sendall((f"👥 Online: {user_list}\n").encode())

            elif msg.startswith("/info"):
                parts = msg.split(" ")
                if len(parts) != 2:
                    conn.sendall("Usage: /info <nickname>\n".encode())
                else:
                    show_user_info(nickname, parts[1])

            elif msg.startswith("/pm"):
                parts = msg.split(" ", 2)
                if len(parts) < 3:
                    conn.sendall("Usage: /pm <user> <message>\n".encode())
                else:
                    _, target_nick, pm_msg = parts
                    private_message(nickname, target_nick, pm_msg)

            else:
                formatted = f"[{timestamp()}] {nickname} ➤ {msg}"
                logging.info(f"{nickname}: {msg}")
                print(get_color(nickname) + formatted)
                broadcast(get_color(nickname) + formatted, exclude=conn)

    except Exception as e:
        logging.error(f"Error with {addr}: {e}")

    finally:
        if conn in addresses:
            nickname = addresses[conn]
            del addresses[conn]
            if nickname in clients:
                del clients[nickname]
            if nickname in join_info:
                del join_info[nickname]
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
    os.system("chcp 65001 >nul")  # Windows-only UTF-8

    HOST = '0.0.0.0'
    PORT = 12345

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()

    print(Fore.CYAN + f"🚀 Server started on {HOST}:{PORT}. Type 'exit' to stop.")
    logging.info("Server started.")

    threading.Thread(target=accept_connections, args=(server,), daemon=True).start()

    while True:
        cmd = input("🛠️ Server> ").strip()
        if cmd.lower() == 'exit':
            break

        elif cmd.lower() == 'who':
            print(Fore.LIGHTYELLOW_EX + "👥 Online Users:")
            for nick in clients:
                ip, join_time = join_info.get(nick, ("Unknown", "Unknown"))
                print(f" - {nick} (IP: {ip}, Joined: {join_time})")

        elif cmd.lower().startswith('kick '):
            parts = cmd.split(" ", 1)
            if len(parts) == 2:
                target = parts[1].strip()
                conn = clients.get(target)
                if conn:
                    try:
                        conn.sendall("🚫 You were kicked from the server.\n".encode())
                        conn.close()
                        print(Fore.RED + f"✅ Kicked {target}")
                        logging.info(f"Admin kicked {target}")
                    except:
                        print(Fore.RED + f"❌ Failed to kick {target}")
                else:
                    print(Fore.RED + f"❌ User '{target}' not found.")

        elif cmd.lower().startswith("msg "):
            msg = cmd[4:]
            server_msg = f"📢 [Server @ {timestamp()}] {msg}"
            print(Fore.LIGHTMAGENTA_EX + server_msg)
            broadcast(Fore.LIGHTMAGENTA_EX + server_msg)

        else:
            print(Fore.RED + "❓ Unknown command. Use: who | kick <user> | msg <text> | exit")

    print(Fore.RED + "🛑 Shutting down server...")
    logging.info("Server shutting down.")
    for conn in list(addresses):
        try:
            conn.sendall("Server is shutting down. Bye!\n".encode())
            conn.close()
        except:
            pass
    server.close()
