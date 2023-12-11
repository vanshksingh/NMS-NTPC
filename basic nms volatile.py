import tkinter as tk
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
        self.geometry("800x600")
        self.devices = {}  # Store devices as {name: [IP, status_label]}
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

        self.device_frame = tk.Frame(self)
        self.device_frame.pack()

    def add_device(self):
        name = self.name_entry.get()
        ip = self.ip_entry.get()
        if name and ip:
            label = tk.Label(self.device_frame, text=f"{name} ({ip}): Checking...")
            label.pack()
            self.devices[name] = [ip, label]
            self.name_entry.delete(0, tk.END)
            self.ip_entry.delete(0, tk.END)

    def monitor_devices(self):
        for name, [ip, label] in self.devices.items():
            status = ping(ip)
            label.config(text=f"{name} ({ip}): {'Online' if status else 'Offline'}",
                         fg='green' if status else 'red')
        self.after(5000, self.monitor_devices)  # Schedule next check in 5 seconds

if __name__ == "__main__":
    app = DeviceMonitorApp()
    app.after(5000, app.monitor_devices)  # Start monitoring
    app.mainloop()
