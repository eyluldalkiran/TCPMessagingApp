import socket
import threading
import json

# Kullanıcı verilerini saklamak için


class UserData:
    def __init__(self, username):
        self.username = username
        self.data = {"messages": [], "contacts": {}}
        self.load_data()

    def load_data(self):
        try:
            with open(f"{self.username}.json", "r") as file:
                self.data = json.load(file)
        except FileNotFoundError:
            self.save_data()

    def save_data(self):
        with open(f"{self.username}.json", "w") as file:
            json.dump(self.data, file, indent=4)

    def add_message(self, message):
        self.data["messages"].append(message)
        self.save_data()

    def add_contact(self, group, contact):
        if group not in self.data["contacts"]:
            self.data["contacts"][group] = []
        self.data["contacts"][group].append(contact)
        self.save_data()

    def add_group(self, group):
        if group not in self.data["contacts"]:
            self.data["contacts"][group] = []
            self.save_data()

    def get_group_members(self, group):
        """Belirli bir grubun üyelerini döndürür."""
        return self.data["contacts"].get(group, [])

    def search_messages(self, keyword):
        return [msg for msg in self.data["messages"] if keyword in msg]

# Mesajlaşma istemcisi


class ChatClient:
    def __init__(self, host='localhost', port=1234):
        self.server_host = host
        self.server_port = port
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.username = input("Kullanıcı adınız: ")
        self.user_data = UserData(self.username)

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024).decode()
                if message:
                    print(message)
                    self.user_data.add_message(message)
            except:
                print("Sunucuyla bağlantı kesildi")
                self.client_socket.close()
                break

    def show_menu(self):
        print("\nMenü:")
        print("1. Mesaj Gönder")
        print("2. Grup Ekle")
        print("3. Gruba Kişi Ekle")
        print("4. Mesajlarda Arama Yap")
        print("5. Grup Üyelerini Görüntüle")
        print("6. Çıkış")
        return input("Seçiminizi yapın: ")

    def send_message(self):
        message = input("Mesajınızı yazın: ")
        self.client_socket.send(message.encode())
        self.user_data.add_message(f"{self.username}: {message}")

    def add_group(self):
        group = input("Eklemek istediğiniz grubun adını yazın: ")
        self.user_data.add_group(group)
        print(f"{group} grubu eklendi.")

    def add_contact(self):
        group = input("Kişiyi eklemek istediğiniz grup: ")
        contact = input("Eklemek istediğiniz kişinin adı: ")
        self.user_data.add_contact(group, contact)
        print(f"{contact} kişisi {group} grubuna eklendi.")

    def search_messages(self):
        keyword = input("Aramak istediğiniz anahtar kelimeyi yazın: ")
        results = self.user_data.search_messages(keyword)
        print("Arama Sonuçları:")
        for msg in results:
            print(msg)

    def show_group_members(self):
        group = input("Üyelerini görmek istediğiniz grubun adını girin: ")
        members = self.user_data.get_group_members(group)
        if members:
            print(f"{group} grubunun üyeleri:")
            for member in members:
                print(member)
        else:
            print(f"{group} grubu mevcut değil veya üye yok.")

    def run(self):
        self.client_socket.connect((self.server_host, self.server_port))
        self.client_socket.send(self.username.encode())
        threading.Thread(target=self.receive_messages).start()

        while True:
            choice = self.show_menu()
            if choice == "1":
                self.send_message()
            elif choice == "2":
                self.add_group()
            elif choice == "3":
                self.add_contact()
            elif choice == "4":
                self.search_messages()
            elif choice == "5":
                self.show_group_members()
            elif choice == "6":
                print("Çıkış yapılıyor...")
                self.client_socket.close()
                break
            else:
                print("Geçersiz seçim, lütfen tekrar deneyin.")


if __name__ == "__main__":
    client = ChatClient()
    client.run()
