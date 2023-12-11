import tkinter as tk
from tkinter import ttk
import subprocess
import platform
import json
import os
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor

class Device:
    def __init__(self, name, ip):
        self.name = name
        self.ip = ip
        self.item = None
        self.tree = None
        self.status = "Unknown"

def ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

class DeviceMonitorApp(tk.Tk):
    def __init__(self, resolution='1200x700', text_size=10):
        super().__init__()
        self.title("Device Monitor")
        self.geometry(resolution)
        self.devices = {}
        self.device_cycle = cycle([])
        self.data_file = "device_data.json"
        self.thread_pool = ThreadPoolExecutor(max_workers=10)
        self.setup_ui()
        self.load_devices()
        self.reset_device_cycle()


    def setup_ui(self):
        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(pady=10)

        self.name_entry = tk.Entry(self.entry_frame, width=20)
        self.name_entry.grid(row=0, column=0, padx=5)

        self.ip_entry = tk.Entry(self.entry_frame, width=20)
        self.ip_entry.grid(row=0, column=1, padx=5)

        add_button = tk.Button(self.entry_frame, text="Add Device", command=self.add_device)
        add_button.grid(row=0, column=2, padx=5)

        remove_button = tk.Button(self.entry_frame, text="Remove Device", command=self.remove_selected)
        remove_button.grid(row=0, column=3, padx=5)

        # Setting up two treeviews side by side
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(expand=True, fill="both", padx=10)

        self.tree1 = self.create_treeview(self.tree_frame)
        self.tree2 = self.create_treeview(self.tree_frame)

        self.tree1.pack(side="left", fill="both", expand=True)
        self.tree2.pack(side="right", fill="both", expand=True)

    def create_treeview(self, parent):
        tree = ttk.Treeview(parent, columns=("Serial", "Name", "IP", "Status"), show='headings')
        tree.heading("Serial", text="Serial No")
        tree.heading("Name", text="Name")
        tree.heading("IP", text="IP")
        tree.heading("Status", text="Status")
        for col in tree["columns"]:
            tree.column(col, width=200)
        return tree

    def add_device(self):
        name = self.name_entry.get()
        ip = self.ip_entry.get()
        if name and ip:
            device = Device(name, ip)
            tree = self.tree1 if len(self.devices) < 23 else self.tree2
            device.item = tree.insert("", tk.END, values=(len(self.devices) + 1, name, ip, "Unknown"))
            device.tree = tree
            self.devices[name] = device
            self.name_entry.delete(0, tk.END)
            self.ip_entry.delete(0, tk.END)
            self.save_devices()
            self.reset_device_cycle()  # Reset device cycle after removing a device

    def remove_selected(self):
        for tree in [self.tree1, self.tree2]:
            selected_item = tree.selection()
            if selected_item:
                for name, device in self.devices.items():
                    if device.item == selected_item[0]:
                        del self.devices[name]
                        break
                tree.delete(selected_item[0])
                self.save_devices()
                break

    def reset_device_cycle(self):
        # Reset the device cycle with the current devices
        self.device_cycle = cycle(self.devices.values())

    def update_device_status(self, device, status):
        color = 'green' if status else 'red'
        device.status = "Online" if status else "Offline"
        device.tree.item(device.item, values=(device.tree.index(device.item) + 1, device.name, device.ip, device.status), tags=(color,))
        device.tree.tag_configure('green', foreground='green')
        device.tree.tag_configure('red', foreground='red')

    def monitor_devices(self):
        try:
            device = next(self.device_cycle)
        except StopIteration:
            self.device_cycle = cycle(self.devices.values())
            device = next(self.device_cycle)

        self.set_to_grey(device)
        # Schedule the ping and update after 1 second
        self.after(1000, lambda: self.thread_pool.submit(self.ping_and_update, device))
        self.after(1000, self.monitor_devices)  # 5 seconds plus 1 second grey time

    def set_to_grey(self, device):
        device.tree.item(device.item, tags=('grey',))
        device.tree.tag_configure('grey', foreground='grey')

    def ping_and_update(self, device):
        status = ping(device.ip)
        self.after(0, lambda: self.update_device_status(device, status))

    def save_devices(self):
        with open(self.data_file, 'w') as file:
            json.dump({name: device.ip for name, device in self.devices.items()}, file, indent=4)

    def load_devices(self):
        if not os.path.exists(self.data_file):
            return

        with open(self.data_file, 'r') as file:
            loaded_devices = json.load(file)
            for name, ip in loaded_devices.items():
                self.name_entry.insert(0, name)
                self.ip_entry.insert(0, ip)
                self.add_device()

if __name__ == "__main__":
    app = DeviceMonitorApp(resolution='1920x1080', text_size=12)
    app.after(1000, app.monitor_devices)
    app.mainloop()
