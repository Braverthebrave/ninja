import socket
import threading
import tkinter as tk
from tkinter import simpledialog, scrolledtext, messagebox
from PIL import Image, ImageTk  # Import Pillow for image handling
import re
import os
import sys
import subprocess
import time
import requests
from io import BytesIO


import pkg_resources

ipoverride = False
overrideip = "127.0.0.1" # change this to required ip and ipoverride to True go to line 122 to set up a cleaner way of connecting to static ip  

# This should fix the issues on mac with Tkinter
def check_and_install_tkmacosx():
    try:
        # Check if tkmacosx is installed
        pkg_resources.require("tkmacosx")
        print("tkmacosx is already installed.")
    except pkg_resources.DistributionNotFound:
        print("tkmacosx is not installed. Installing now...")
        # Install tkmacosx using pip3
        subprocess.check_call([ "pip3", "install", "tkmacosx"])

# Run the function
check_and_install_tkmacosx()

# Check if required libraries are installed
def check_libraries():
    try:
        import requests
    except ImportError:
        print("The 'requests' library is not installed. Please install it using 'pip install requests'.")
        sys.exit(1)  # Exit the program if the library is missing
    
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("The 'Pillow' library is not installed. Please install it using 'pip install pillow'.")
        sys.exit(1)  # Exit the program if the library is missing

# Function to read configuration from a file
def read_config(file_path):
    config = {}
    try:
        with open(file_path, 'r') as f:
            for line in f:
                if line.strip() and not line.startswith('#'):  # Ignore empty lines and comments
                    key, value = line.strip().split('=')
                    config[key] = value
    except:
        config = "{'BACKGROUND_COLOR': '#2e2e2e', 'ENTRY_BACKGROUND_COLOR': '#3e3e3e', 'TEXT_COLOR': 'white', 'USERNAME_COLOR': 'cyan', 'DARK_TEXT_AREA_COLOR': '#1e1e1e', 'FONT_FAMILY': 'Consolas', 'FONT_SIZE': '12'}" # default config when can't find config.txt
        print(f"can't find config.txt at {file_path}")
    print(config)
    return config

# Function to get local IP address based on user input
def get_local_ip(last_digit):
    # Get the local IP address
    local_ip = socket.gethostbyname(socket.gethostname())
    
    # Strip the last segment of the IP address
    base_ip = ".".join(local_ip.split('.')[:-1]) + "."
    
    # Return the base IP concatenated with the given last digit
    if ipoverride == False:
        return base_ip + str(last_digit)
    else:
        return(overrideip)

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
    '34': 'cyan',
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

        # Set the application icon using a relative path and check if the icon exists
        try:
            icon_path = os.path.join(os.path.dirname(__file__), 'icon.ico')
            self.master.iconbitmap(icon_path)
        except:
            print(f"debug: cannot find icon.ico at {icon_path}")

        # Prompt user for the last digit of the local IP address
        last_digit = simpledialog.askinteger("Input", "Enter server local IP address (e.g., 2 for 192.168.1.2):", parent=self.master)
        if last_digit is None:
            self.master.destroy()
            return
        elif last_digit == 69420:  # Example condition for localhost (if you want to connect to a server over the internet, change the ip below and type 69420 to connect to it)
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

        # Use a Text widget for message display
        self.text_area = tk.Text(text_frame, state='disabled', wrap=tk.WORD, bg=DARK_TEXT_AREA_COLOR, fg=TEXT_COLOR, font=(FONT_FAMILY, FONT_SIZE))
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

            if message.startswith("//"):# local command handling
                if message == "//restart" or message == "//r":
                    self.display_message(f"RESTARTING CLIENT IN 3 seconds")
                    self.master.after(3000, self.restart_program)
                    self.master.destroy()
                    subprocess.run([sys.executable] + sys.argv)

                elif message == "//restart i" or message == "//r i":
                    self.master.destroy()
                    subprocess.run([sys.executable] + sys.argv)
                    
                elif message.startswith("//restart t") or message.startswith("//r t"):
                    if message.startswith("//re"):
                        timetorestart = message[12:].strip()
                    else:
                        timetorestart = message[6:].strip()
                    try:
                        numbertime = (float(timetorestart)) * 1000
                        self.display_message(f"RESTARTING CLIENT IN {timetorestart} seconds")
                        self.master.after(int(numbertime), self.restart_program)
                        self.display_message(f"RESTARTING CLIENT")
                        self.master.destroy()
                        subprocess.run([sys.executable] + sys.argv)
                    except:
                        self.display_message(f"{timetorestart} is not an integer")

                    
                elif message == '//shutdown' or message == "//s":
                    os._exit(0)
                elif message.startswith('//echo'):
                    echo = message[7:].strip()
                    self.display_message(f"{echo}")
                else:
                    self.display_message(f"INVALID COMMAND!")

            else:
                self.client_socket.send(message.encode('utf-8'))
                self.display_message(f"You: {message}")

    def receive_messages(self):
        while True:
            try:
                message = self.client_socket.recv(1024)
                if message:
                    message = message.decode('utf-8')
                    if message.startswith(":img: "):
                        self.display_image_from_url(message[6:])  # Process the image URL
                    else:
                        self.display_message(message)
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

    def display_image_from_url(self, url):
        try:
            # Get the image from the URL for some reason it don't always work 
            response = requests.get(url)
            image_data = BytesIO(response.content)
            image = Image.open(image_data)
            image.thumbnail((300, 300))  # Resize the image to fit in the window ill add smart resizing latererr

            # Create a Tkinter-compatible image becasuefsd f u  thats why
            image_tk = ImageTk.PhotoImage(image)

            # Insert the image into the Text widget
            self.text_area.config(state='normal')
            self.text_area.insert(tk.END, "\n")  # To ensure image isn't on the same line as the last message
            self.text_area.image_create(tk.END, image=image_tk)  # Add image at the end
            self.text_area.insert(tk.END, "\n")  # Insert a newline after the image

            # Keep a reference to the image object
            self.text_area.image = image_tk
            self.text_area.config(state='disabled')
            self.text_area.see(tk.END)

        except Exception as e:
            self.display_message(f"Failed to load image: {e}")

if __name__ == "__main__":
    check_libraries()

    root = tk.Tk()
    client = ChatClient(root)
    root.mainloop()

# made by braverthebrave 2024 