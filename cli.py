import socket
import threading
from colorama import Fore, Style, init

init(autoreset=True)

SERVER = '127.0.0.1'
PORT = 5050

def receive_messages(client):
    while True:
        try:
            msg = client.recv(1024).decode()
            if msg:
                print(msg)
            else:
                break
        except Exception as ex:
            print(f"Error recieving message: {ex}")
            break

def main():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect((SERVER, PORT))
        print(Fore.GREEN + "Connected to the chat server")
    except Exception as ex:
        print(Fore.RED + f"Failed to connect to server with error: {ex}")
        return
    # Thread to handle incoming messages
    thread = threading.Thread(target=receive_messages, args=(client,))
    thread.start()

    while True:
        try:
            message = input("> ")
            if message.lower() == "/quit":
                client.send(message.encode())
                print(Fore.YELLOW + "Disconnected from the server.")
                client.close()
                break
            elif message.startswith("/report "):
                client.send(message.encode())
            else:
                client.send(message.encode())
        except Exception as e:
            print(Fore.RED + f"Error: {e}")
            client.close()
            break

if __name__ == "__main__":
    main()
