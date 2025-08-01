import socket
import threading
from datetime import datetime
from colorama import init, Fore
import winsound

init(autoreset=True)

# Message colors
colors = [Fore.BLUE, Fore.GREEN, Fore.CYAN, Fore.MAGENTA, Fore.YELLOW, Fore.WHITE]

nickname = input("Enter your nickname: ").strip()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('localhost', 12345))

# Send nickname immediately
def send_nickname():
    client.recv(1024)  # Prompt
    client.sendall((nickname + '\n').encode())

# Assign consistent color based on nickname hash
def get_color(nick):
    return colors[hash(nick) % len(colors)]

# Sound for incoming messages
def play_beep():
    winsound.Beep(1000, 150)

# Listen for messages from server
def receive():
    while True:
        try:
            msg = client.recv(1024).decode().strip()
            if not msg:
                break

            if not msg.startswith(f"[{nickname}") and nickname not in msg:
                play_beep()

            print(msg)
        except:
            print("❌ Connection closed.")
            break

# Send messages to server
def write():
    while True:
        msg = input(f"{Fore.LIGHTBLACK_EX}[{datetime.now().strftime('%H:%M:%S')}] {nickname} ➤ {Fore.RESET}")
        if msg.strip().lower() == "/quit":
            client.sendall("/quit\n".encode())
            break
        client.sendall((msg + '\n').encode())

send_nickname()

recv_thread = threading.Thread(target=receive, daemon=True)
recv_thread.start()

write()
client.close()