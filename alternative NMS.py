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
        self.hide_ip = False

def ping(host):
    param = '-n' if platform.system().lower() == 'windows' else '-c'
    command = ['ping', param, '1', host]
    return subprocess.call(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

class SettingsDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Settings")
        self.geometry("300x300")

        container = tk.Frame(self)
        canvas = tk.Canvas(container)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
        self.scrollable_frame = tk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(
                scrollregion=canvas.bbox("all")
            )
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        container.pack(expand=True, fill="both")
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        tk.Label(self.scrollable_frame, text="Resolution (e.g., 1920x1080):").pack(pady=5)
        self.resolution_entry = tk.Entry(self.scrollable_frame)
        self.resolution_entry.pack(pady=5)
        self.resolution_entry.insert(0, master.geometry())

        tk.Label(self.scrollable_frame, text="Text Size (e.g., 12):").pack(pady=5)
        self.text_size_entry = tk.Entry(self.scrollable_frame)
        self.text_size_entry.pack(pady=5)
        self.text_size_entry.insert(0, master.text_size)

        tk.Label(self.scrollable_frame, text="Label for Table 1:").pack(pady=5)
        self.label_table1_entry = tk.Entry(self.scrollable_frame)
        self.label_table1_entry.pack(pady=5)
        self.label_table1_entry.insert(0, master.label_tree1.cget("text"))

        tk.Label(self.scrollable_frame, text="Label for Table 2:").pack(pady=5)
        self.label_table2_entry = tk.Entry(self.scrollable_frame)
        self.label_table2_entry.pack(pady=5)
        self.label_table2_entry.insert(0, master.label_tree2.cget("text"))

        self.hide_ip_var = tk.BooleanVar(value=master.hide_ip)
        tk.Checkbutton(self.scrollable_frame, text="Hide IP Addresses", variable=self.hide_ip_var).pack(pady=10)

        tk.Button(self.scrollable_frame, text="Apply", command=self.apply_settings).pack(pady=20)

    def apply_settings(self):
        resolution = self.resolution_entry.get()
        text_size = int(self.text_size_entry.get())
        self.master.update_settings(resolution, text_size, self.hide_ip_var.get())

        self.master.label_tree1.config(text=self.label_table1_entry.get())
        self.master.label_tree2.config(text=self.label_table2_entry.get())

        self.master.update_ip_visibility()
        self.master.save_devices()

        self.destroy()

class DeviceMonitorApp(tk.Tk):
    def __init__(self, resolution='1200x700', text_size=10, hide_ip=False):
        super().__init__()
        self.title("Device Monitor")
        self.geometry(resolution)
        self.text_size = text_size
        self.hide_ip = hide_ip
        self.devices = {}
        self.device_cycle = cycle([])
        self.data_file = "device_data.json"
        self.thread_pool = ThreadPoolExecutor(max_workers=10)

        # Initialize selected_tree_var before calling setup_ui
        self.selected_tree_var = tk.StringVar(value='tree1')  # Add this line

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

        settings_button = tk.Button(self.entry_frame, text="Settings", command=self.open_settings)
        settings_button.grid(row=0, column=4, padx=5)

        tk.Radiobutton(self.entry_frame, text="Table 1", variable=self.selected_tree_var, value='tree1').grid(row=1,
                                                                                                              column=0)
        tk.Radiobutton(self.entry_frame, text="Table 2", variable=self.selected_tree_var, value='tree2').grid(row=1,
                                                                                                              column=1)

        # Frames for treeviews including labels
        self.tree_frame1 = tk.Frame(self)
        self.tree_frame2 = tk.Frame(self)
        self.tree_frame1.pack(side="left", expand=True, fill="both", padx=5)
        self.tree_frame2.pack(side="right", expand=True, fill="both", padx=5)

        # Create and pack the labels above the treeviews
        self.label_tree1 = tk.Label(self.tree_frame1, text="Table 1", font=('Helvetica', 12, 'bold'))
        self.label_tree2 = tk.Label(self.tree_frame2, text="Table 2", font=('Helvetica', 12, 'bold'))
        self.label_tree1.pack(side="top", fill="x")
        self.label_tree2.pack(side="top", fill="x")

        # Treeviews
        self.tree1 = self.create_treeview(self.tree_frame1)
        self.tree2 = self.create_treeview(self.tree_frame2)
        self.tree1.pack(expand=True, fill="both")
        self.tree2.pack(expand=True, fill="both")


    def open_settings(self):
        SettingsDialog(self)

    def update_settings(self, resolution, text_size, hide_ip):
        self.geometry(resolution)
        self.text_size = text_size
        self.hide_ip = hide_ip
        self.apply_text_size()

    def update_ip_visibility(self):
        for device in self.devices.values():
            if self.hide_ip:
                ip_text = '*******'
            else:
                ip_text = device.ip
            device.tree.item(device.item, values=(device.tree.index(device.item) + 1, device.name, ip_text, device.status))


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

        # Check if IP should be hidden
        if self.hide_ip:
            ip_text = '*******'
        else:
            ip_text = device.ip

        device.tree.item(device.item, values=(device.tree.index(device.item) + 1, device.name, ip_text, device.status),
                         tags=(color,))
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
        # Save device data with table information and label texts
        device_data = {
            'devices': {
                name: {
                    'ip': device.ip,
                    'table': 'tree1' if device.tree == self.tree1 else 'tree2'
                } for name, device in self.devices.items()
            },
            'labels': {
                'label_tree1': self.label_tree1.cget("text"),
                'label_tree2': self.label_tree2.cget("text")
            }
        }

        with open(self.data_file, 'w') as file:
            json.dump(device_data, file, indent=4)

    def load_devices(self):
        if not os.path.exists(self.data_file):
            return

        with open(self.data_file, 'r') as file:
            loaded_data = json.load(file)
            loaded_devices = loaded_data.get('devices', {})
            labels = loaded_data.get('labels', {})

            # Load table labels
            self.label_tree1.config(text=labels.get('label_tree1', "Table 1"))
            self.label_tree2.config(text=labels.get('label_tree2', "Table 2"))

            for name, data in loaded_devices.items():
                ip = data.get('ip')  # Use get method to avoid KeyError
                if ip is None:
                    continue  # Skip this entry if IP is not found, or handle it differently

                table_choice = data.get('table', 'tree1')
                self.selected_tree_var.set(table_choice)
                self.name_entry.insert(0, name)
                self.ip_entry.insert(0, ip)
                self.add_device()
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
