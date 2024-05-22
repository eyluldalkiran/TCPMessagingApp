import socket
import threading
import json
import os

# Verilerin saklanacağı dosya
DATA_FILE = "db.json"

# Verilerin yüklenmesi ve kaydedilmesi için yardımcı fonksiyonlar


def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    return {}


def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data, file, indent=4)

# Mesajlaşma sunucusu


class ChatServer:
    def __init__(self, host='localhost', port=1234):
        self.clients = []
        self.host = host
        self.port = port
        self.data = load_data()
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server {self.host}:{self.port} üzerinde çalışıyor")

    def handle_client(self, client_socket, client_address):
        user = client_socket.recv(1024).decode()
        if user not in self.data:
            self.data[user] = {"messages": [], "contacts": {}}
        self.clients.append((client_socket, user))

        while True:
            try:
                message = client_socket.recv(1024).decode()
                if message:
                    print(f"{user}: {message}")
                    self.data[user]["messages"].append(message)
                    save_data(self.data)
                    self.broadcast_message(f"{user}: {message}", client_socket)
            except:
                print(f"{client_address} bağlantısı kesildi")
                self.clients.remove((client_socket, user))
                client_socket.close()
                break

    def broadcast_message(self, message, client_socket):
        for client, user in self.clients:
            if client != client_socket:
                try:
                    client.send(message.encode())
                except:
                    client.close()
                    self.clients.remove((client, user))

    def run(self):
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"{client_address} bağlandı")
            threading.Thread(target=self.handle_client, args=(
                client_socket, client_address)).start()


if __name__ == "__main__":
    server = ChatServer()
    server.run()
