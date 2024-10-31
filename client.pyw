import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
import re
import os

# Function to read configuration from a file
def read_config(file_path):
    config = {}
    with open(file_path, 'r') as f:
        for line in f:
            if line.strip() and not line.startswith('#'):  # Ignore empty lines and comments
                key, value = line.strip().split('=')
                config[key] = value
    return config

# Function to get local IP address based on user input
def get_local_ip(last_digit):
    base_ip = "10.100.172."  # Adjust as necessary for your local network
    return base_ip + str(last_digit)

# Load configuration
config_path = os.path.join(os.path.dirname(__file__), 'config.txt')
config = read_config(config_path)

# Color definitions for dark mode from config
BACKGROUND_COLOR = config.get('BACKGROUND_COLOR', '#2e2e2e')
ENTRY_BACKGROUND_COLOR = config.get('ENTRY_BACKGROUND_COLOR', '#3e3e3e')
TEXT_COLOR = config.get('TEXT_COLOR', 'white')
USERNAME_COLOR = config.get('USERNAME_COLOR', 'cyan')
DARK_TEXT_AREA_COLOR = config.get('DARK_TEXT_AREA_COLOR', '#1e1e1e')
FONT_FAMILY = config.get('FONT_FAMILY', 'Consolas')
FONT_SIZE = int(config.get('FONT_SIZE', '12'))

# ANSI color codes mapping
ANSI_COLOR_CODES = {
    '30': 'black',
    '31': 'red',
    '32': 'green',
    '33': 'yellow',
    '34': 'blue',
    '35': 'magenta',
    '36': 'cyan',
    '37': 'white',
    '0': 'reset',
}

class ChatClient:
    def __init__(self, master):
        self.master = master
        self.master.title("NINJA Messenger")
        self.master.configure(bg=BACKGROUND_COLOR)

        # Set the application icon using a relative path
        icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
        self.master.iconbitmap(icon_path)

        # Prompt user for the last digit of the local IP address
        last_digit = simpledialog.askinteger("Input", "Enter server local IP address (e.g., 2 for 192.168.1.2):", parent=self.master)
        if last_digit is None:
            self.master.destroy()
            return
        elif last_digit == 69420:  # Example condition for localhost
            self.HOST = '127.0.0.1'
        else:
            self.HOST = get_local_ip(last_digit)

        self.PORT = 12345
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((self.HOST, self.PORT))
        except Exception as e:
            messagebox.showerror("Connection Error", f"Could not connect to server: {e}")
            self.master.destroy()
            return

        # Configure grid for a resizable UI
        master.grid_rowconfigure(0, weight=0)
        master.grid_rowconfigure(1, weight=1)
        master.grid_columnconfigure(0, weight=1)

        # Username label
        self.username_label = tk.Label(master, text="Username: ", bg=BACKGROUND_COLOR, fg=USERNAME_COLOR, font=(FONT_FAMILY, FONT_SIZE))
        self.username_label.grid(row=0, column=0, padx=(10, 0), pady=(10, 0), sticky='w')

        label = tk.Label(master, text="Message:", bg=BACKGROUND_COLOR, fg=TEXT_COLOR)
        label.grid(row=2, column=0, padx=(0, 10), pady=(0, 10), sticky='w')

        self.entry = tk.Entry(master, bg=ENTRY_BACKGROUND_COLOR, fg=TEXT_COLOR, insertbackground=TEXT_COLOR)
        self.entry.grid(row=2, column=0, padx=(60), pady=(0, 10), sticky='ew')

        # Create a frame for the text area
        text_frame = tk.Frame(master, bg=BACKGROUND_COLOR)
        text_frame.grid(row=1, column=0, columnspan=2, padx=10, pady=10, sticky='nsew')

        self.text_area = scrolledtext.ScrolledText(text_frame, state='disabled', wrap=tk.WORD, bg=DARK_TEXT_AREA_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE))
        self.text_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.entry.bind("<Return>", self.send_message)

        self.username = simpledialog.askstring("Username", "Enter your username:", parent=self.master)
        if self.username:
            self.username_label.config(text="Username: " + self.username)
            self.client_socket.send(self.username.encode('utf-8'))

        threading.Thread(target=self.receive_messages, daemon=True).start()
        self.create_tags()

    def create_tags(self):
        for color in ANSI_COLOR_CODES.values():
            if color != 'reset':
                self.text_area.tag_config(color, foreground=color)

    def send_message(self, event=None):
        message = self.entry.get()
        self.entry.delete(0, tk.END)
        if message:
            self.client_socket.send(message.encode('utf-8'))
            self.display_message(f"You: {message}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024)
                if message:
                    self.display_message(message.decode('utf-8'))
            except Exception as e:
                print(f"An error occurred: {e}")
                self.client_socket.close()
                break

    def display_message(self, message):
        self.text_area.config(state='normal')
        self.insert_colored_message(message)
        self.text_area.insert(tk.END, "\n")
        self.text_area.config(state='disabled')
        self.text_area.see(tk.END)

    def insert_colored_message(self, message):
        segments = re.split(r'(\x1b\[\d+m)', message)
        current_color = 'reset'
        for segment in segments:
            if segment.startswith('\x1b['):
                code = segment[2:-1]
                current_color = ANSI_COLOR_CODES.get(code, 'reset')
            else:
                if current_color == 'reset':
                    self.text_area.insert(tk.END, segment)
                else:
                    self.text_area.insert(tk.END, segment, current_color)

if __name__ == "__main__":
    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()
