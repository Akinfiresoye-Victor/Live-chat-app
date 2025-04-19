

# importation
from tkinter import *
import socket
import threading
import sys
import errno

# Constant variables
DEST_IP = socket.gethostbyname(socket.gethostname())
DEST_PORT = 1234
BYTESIZE = 10

#Creating a class to guide our app
class ChatClient:
    #a constructor for gettig all the attributes we need 
    def __init__(self, root):
        self.root = root
        root.title('Zen Live Chat')
        root.iconbitmap("C:\\Users\\VICT6OR\\Pictures\\Project_game\\message.ico") #commented out because it caused an error on my system
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client_socket.connect((DEST_IP, DEST_PORT))

        # Homepage view
        self.intro = Label(root, text='  Welcome to Zen Live chat')
        self.intro.grid(row=0, column=0, columnspan=3)
        self.my_username_entry = Entry(root, width=25)
        self.username_label = Label(root, text='Enter your username')
        self.username_label.grid(row=1, column=0)
        self.my_username_entry.grid(row=1, column=1)
        self.button_connect = Button(root, text='Join live chat', command=self.connect)
        self.button_connect.grid(row=1, column=2)

        self.display = None  # Making our display empty

        self.username = None# making our username also empty

    #a method for connecting clients
    def connect(self):
        username = self.my_username_entry.get().encode('utf-8')#getting our username
        username_header = f"{len(username):<{BYTESIZE}}".encode('utf-8')
        self.client_socket.send(username_header + username)
        self.username = username.decode('utf-8')  # Store username
        
        #clearing way for our other widgets
        self.intro.destroy()
        self.my_username_entry.destroy()
        self.username_label.destroy()
        self.button_connect.destroy()

        Label(self.root, text=f"{self.username} joined live chat", fg='green').grid(row=0, column=0)
        #function for creating the chat widget
        self.setup_widgets()
        # Start the receiving thread
        threading.Thread(target=self.receive_messages, daemon=True).start()

    #method for setting up our widgets
    def setup_widgets(self):
        msg_lbl = Label(self.root, text="Message:")
        msg_lbl.grid(row=1, column=0)
        self.my_message_entry = Entry(self.root, width=35)
        self.my_message_entry.grid(row=1, column=1)
        send_button = Button(self.root, text='Send', command=self.send_message)
        send_button.grid(row=1, column=2)
        self.display = Text(self.root, height=4, width=45)
        self.display.grid(row=2, column=0, columnspan=3)
        self.display.config(state='disabled')  # Make it read-only

    #method to send the message
    def send_message(self):
        message = self.my_message_entry.get()
        if message:
            try:
                message = message.encode('utf-8')
                message_header = f"{len(message):<{BYTESIZE}}".encode('utf-8')
                self.client_socket.send(message_header + message)
                self.my_message_entry.delete(0, END)  # Clear the entry field
            except (socket.error, OSError) as e:
                print(f"Error sending message: {e}")
                self.display_message(f"Error sending message: {e}")
                # Consider reconnecting or exiting
                sys.exit()

    #method for receiving message from another client
    def receive_messages(self):
        while True:
            try:
                username_header = self.client_socket.recv(BYTESIZE)
                if not username_header:
                    print("Connection closed by the server")
                    self.display_message("Connection closed by the server")
                    break  # Exit the loop, thread will terminate
                username_length = int(username_header.decode('utf-8').strip())
                username = self.client_socket.recv(username_length).decode('utf-8')

                message_header = self.client_socket.recv(BYTESIZE)
                message_length = int(message_header.decode('utf-8').strip())
                message = self.client_socket.recv(message_length).decode('utf-8')
                self.display_message(f"{username}> {message}")

            except (socket.error, OSError) as e:
                if e.errno == errno.EAGAIN or e.errno == errno.EWOULDBLOCK:
                    continue  # No data available, try again
                else:
                    print(f"Error receiving message: {e}")
                    self.display_message(f"Error receiving message: {e}")
                    break  # Exit loop on other socket errors
            except Exception as e:
                print(f"General error in receive_messages: {e}")
                self.display_message(f"General error: {e}")
                break

    def display_message(self, message):
        self.root.after(0, self._display_message_in_gui, message)  # Use after to update GUI

    def _display_message_in_gui(self, message):
        #making the display widget to be active and in active after receiving a message
        self.display.config(state='normal')
        self.display.insert(END, message + "\n")
        self.display.config(state='disabled')


if __name__ == "__main__":
    root = Tk()
    chat_client = ChatClient(root)
    root.mainloop()
