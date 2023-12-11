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


class SettingsDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("300x200")

        tk.Label(self, text="Resolution (e.g., 1920x1080):").pack(pady=5)
        self.resolution_entry = tk.Entry(self)
        self.resolution_entry.pack(pady=5)
        self.resolution_entry.insert(0, master.geometry())

        tk.Label(self, text="Text Size (e.g., 12):").pack(pady=5)
        self.text_size_entry = tk.Entry(self)
        self.text_size_entry.pack(pady=5)
        self.text_size_entry.insert(0, master.text_size)

        tk.Button(self, text="Apply", command=self.apply_settings).pack(pady=20)

    def apply_settings(self):
        resolution = self.resolution_entry.get()
        text_size = int(self.text_size_entry.get())
        self.master.update_settings(resolution, text_size)
        self.destroy()


class DeviceMonitorApp(tk.Tk):
    def __init__(self, resolution='1200x700', text_size=10):
        super().__init__()
        self.title("Device Monitor")
        self.geometry(resolution)
        self.text_size = text_size
        self.devices = {}
        self.device_cycle = cycle([])
        self.data_file = "device_data.json"
        self.thread_pool = ThreadPoolExecutor(max_workers=10)

        self.selected_tree_var = tk.StringVar(value='tree1')  # Tracks which tree to add devices to
        self.setup_ui()
        self.load_devices()
        self.reset_device_cycle()


    def setup_tree_selection_ui(self):
        self.tree_selection_frame = tk.Frame(self.entry_frame)
        self.tree_selection_frame.grid(row=1, columnspan=5)

        tk.Radiobutton(self.tree_selection_frame, text="Tree 1", variable=self.selected_tree_var, value='tree1').pack(
            side='left')
        tk.Radiobutton(self.tree_selection_frame, text="Tree 2", variable=self.selected_tree_var, value='tree2').pack(
            side='left')

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

        settings_button = tk.Button(self.entry_frame, text="Settings", command=self.open_settings)
        settings_button.grid(row=0, column=4, padx=5)

        tk.Radiobutton(self.entry_frame, text="Table 1", variable=self.selected_tree_var, value='tree1').grid(row=1,
                                                                                                              column=0)
        tk.Radiobutton(self.entry_frame, text="Table 2", variable=self.selected_tree_var, value='tree2').grid(row=1,
                                                                                                              column=1)

        # Setting up two treeviews side by side
        self.tree_frame = tk.Frame(self)
        self.tree_frame.pack(expand=True, fill="both", padx=10)

        self.tree1 = self.create_treeview(self.tree_frame)
        self.tree2 = self.create_treeview(self.tree_frame)

        self.tree1.pack(side="left", fill="both", expand=True)
        self.tree2.pack(side="right", fill="both", expand=True)


    def open_settings(self):
        SettingsDialog(self)

    def update_settings(self, resolution, text_size):
        self.geometry(resolution)
        self.text_size = text_size
        self.apply_text_size()

    def apply_text_size(self):
        # Update text size in Treeview
        style = ttk.Style()
        style.configure('Treeview', font=('Helvetica', self.text_size))

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
            # Choose the table based on the selected option
            selected_tree = self.tree1 if self.selected_tree_var.get() == 'tree1' else self.tree2
            device = Device(name, ip)
            device.item = selected_tree.insert("", tk.END, values=(len(self.devices) + 1, name, ip, "Unknown"))
            device.tree = selected_tree
            self.devices[name] = device
            self.name_entry.delete(0, tk.END)
            self.ip_entry.delete(0, tk.END)
            self.save_devices()
            self.reset_device_cycle()


    def remove_selected(self):
        for tree in [self.tree1, self.tree2]:
            selected_item = tree.selection()
            if selected_item:
                device_to_remove = None
                for name, device in self.devices.items():
                    if device.item == selected_item[0]:
                        tree.delete(selected_item[0])
                        device_to_remove = name
                        break

                if device_to_remove:
                    del self.devices[device_to_remove]
                    self.save_devices()
                    self.reset_device_cycle()  # Reset device cycle after removing a device
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
        # Correctly save device data with table information
        device_data = {
            name: {
                'ip': device.ip,
                'table': 'tree1' if device.tree == self.tree1 else 'tree2'
            } for name, device in self.devices.items()
        }

        with open(self.data_file, 'w') as file:
            json.dump(device_data, file, indent=4)

    def load_devices(self):
        if not os.path.exists(self.data_file):
            return

        with open(self.data_file, 'r') as file:
            loaded_devices = json.load(file)
            for name, data in loaded_devices.items():
                ip = data['ip']
                table_choice = data.get('table', 'tree1')
                self.selected_tree_var.set(table_choice)  # Set the table choice before adding the device
                self.name_entry.insert(0, name)
                self.ip_entry.insert(0, ip)
                self.add_device()  # This will now add the device to the correct table
                self.name_entry.delete(0, tk.END)
                self.ip_entry.delete(0, tk.END)

    def reset_device_cycle(self):
        # Combine devices from both tables
        devices_combined = list(self.devices.values())
        self.device_cycle = cycle(devices_combined)

    def monitor_devices(self):
        try:
            device = next(self.device_cycle)
        except StopIteration:
            self.reset_device_cycle()
            device = next(self.device_cycle)

        self.set_to_grey(device)
        self.after(1000, lambda: self.thread_pool.submit(self.ping_and_update, device))
        self.after(1000, self.monitor_devices)  # Continue with the next device


if __name__ == "__main__":
    app = DeviceMonitorApp(resolution='1920x1080', text_size=15)
    app.after(1000, app.monitor_devices)
    app.mainloop()
