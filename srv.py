import socket
import threading
import json
from usr_mngt import add_or_upd_usr, validate_token, revoke_token, ban_usr, unban_user, is_mod
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

HOST='127.0.0.1'
PORT= 5050

clients = []
username = {}
message_log = {}

EULA_FILE = "eula.txt"

def get_eula():
    try:
        with open(EULA_FILE, "r") as f:
            return f.read()
    except FileNotFoundError:
        return "No EULA found. Please contact the chat master !"
    
def broadcast(msg, sender=None, color=Style.RESET_ALL):
    formatted_msg = f"{color}{msg}{Style.RESET_ALL}"
    for client in clients:
        if client != sender:
            client.send(formatted_msg.encode())

def log_report(reporter, sender, msg_id, msg_content):
    report_data = {
        "reporter": reporter,
        "sender": sender,
        "message_id": msg_id,
        "message_content": msg_content,
        "reported_at": datetime.now().isoformat()
    }

    try:
        with open("complain.json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        data = {"reports": []}

    data["reports"].append(report_data)

    with open("complain.json", "w") as f:
        json.dump(data, f, indent=4)

    print(f"Report logged: {report_data}")

def handle_client(client, addr):
    try:
        client.send("Enter your username: ".encode())
        username = client.recv(1024).decode().strip()

        client.send("Enter your private token (or 'new' to generate new one): ".encode())
        token = client.recv(1024).decode().strip()

        if token == "new":
            eula_text = get_eula()
            client.send(f"\n{eula_text}\n".encode())

            client.send("Do you accept the EULA ? (Yy/Nn): ".encode())
            eula_accepted = client.recv(1024).decode().strip().lower()

            if eula_accepted != 'y':
                client.send("You must accept the EULA to register. Connection to server has been terminated !\n".encode())
                add_or_upd_usr(username, eula_acc=False)
                client.close()
                return
            
            token = add_or_upd_usr(username, eula_acc=True)
            client.send(f"Your token is: {Fore.GREEN}{Style.BRIGHT}{token}{Style.RESET_ALL}".encode())

        is_valid, msg = validate_token(username, token)
        if not is_valid:
            client.send(f"Authentication failed: {msg}\n".encode())
            client.close()
            return
        
        username[client] = username
        clients.append(client)
        role = "moderator" if is_mod(username) else "user"
        broadcast(f"{username} ({role}) has joined the chat room !", sender=None, color=Fore.GREEN)
        client.send(f"Authentication successful! Welkom, {username} ({role}). \n".encode())

        while True:
            msg = client.recv(1024).decode().strip()

            if msg.lower() == "/quit":
                broadcast(f"{username} has left the chat room !", sender=None, color=Fore.YELLOW)
                clients.remove(client)
                client.close()
                break
            elif msg.startwith("/ban ") and is_mod(username):
                target = msg.split(" ", 1)[1]
                ban_usr(target)
                broadcast(f"{target} has been banned by {username}.", sender=None, color=Fore.RED)
            elif msg.startwith("/unban ") and is_mod(username):
                target = msg.split(" ", 1)[1]
                ban_usr(target)
                broadcast(f"{target} has been banned by {username}.", sender=None, color=Fore.RED)
            elif msg.startwith("/revoke ") and is_mod(username):
                target = msg.split(" ", 1)[1]
                revoke_token(target)
                broadcast(f"{target} has been exiled to void realm by {username}.", sender=None, color=Fore.YELLOW)
            elif msg.startwith("/report "):
                msg_id = msg.split(" ", 1)[1]
                if msg_id in message_log:
                    sender_username, msg_content = message_log[msg_id]
                    log_report(username, sender_username, msg_id, msg_content)
                    client.send("Message has been reported to the Moderator.\n".encode())
                else:
                    client.send("Invalid message ID. Please recheck reported message ID\n".encode())
            else:
                msg_id = hash(msg) & 0xFFFFFF
                message_log[msg_id] = (username, msg)
                broadcast(f"{Fore.GREEN}{username}{Fore.WHITE} | {Fore.CYAN}{msg_id}{Style.RESET_ALL}: {msg}", sender=client, color=None)

    except Exception as ex:
        print(f"Error: {ex}")
        if client in clients:
            clients.remove(client)
        client.close()


def main():
    srv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    srv.bind((HOST, PORT))
    srv.listen(10)
    print(f"Server running on {HOST}:{PORT}")

    while True:
        client, addr = srv.accept()
        print(f"Connection established with {addr}")
        threading.Thread(target=handle_client, args=(client, addr)).start()

if __name__ == "__main__":
    main()