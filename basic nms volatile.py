import tkinter as tk
from tkinter import ttk
import subprocess
import platform

# Function to ping and check device status
def ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

# Define GUI class
class DeviceMonitorApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Device Monitor")
        self.geometry("1000x700")
        self.devices = {}  # Store devices as {name: [IP, treeview_item]}
        self.setup_ui()

    def setup_ui(self):
        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(pady=10)

        self.name_entry = tk.Entry(self.entry_frame, width=20)
        self.name_entry.grid(row=0, column=0, padx=5)

        self.ip_entry = tk.Entry(self.entry_frame, width=20)
        self.ip_entry.grid(row=0, column=1, padx=5)

        add_button = tk.Button(self.entry_frame, text="Add Device", command=self.add_device)
        add_button.grid(row=0, column=2, padx=5)

        # Treeview setup
        self.tree = ttk.Treeview(self, columns=("Name", "IP", "Status"), show='headings')
        self.tree.heading("Name", text="Name")
        self.tree.heading("IP", text="IP")
        self.tree.heading("Status", text="Status")
        self.tree.column("Name", width=200)
        self.tree.column("IP", width=200)
        self.tree.column("Status", width=200)
        self.tree.pack(pady=20)

    def add_device(self):
        name = self.name_entry.get()
        ip = self.ip_entry.get()
        if name and ip:
            item = self.tree.insert("", tk.END, values=(name, ip, "Checking..."))
            self.devices[name] = [ip, item]
            self.name_entry.delete(0, tk.END)
            self.ip_entry.delete(0, tk.END)

    def update_device_status(self, name, status):
        item = self.devices[name][1]
        self.tree.item(item, values=(name, self.devices[name][0], "Online" if status else "Offline"))

    def monitor_devices(self):
        for name, [ip, _] in self.devices.items():
            status = ping(ip)
            self.update_device_status(name, status)
        self.after(5000, self.monitor_devices)  # Schedule next check in 5 seconds

if __name__ == "__main__":
    app = DeviceMonitorApp()
    app.after(5000, app.monitor_devices)  # Start monitoring
    app.mainloop()
