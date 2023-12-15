import tkinter as tk
from tkinter import ttk
import tkinter.font as tkFont
import subprocess
import platform
import json
import os
from itertools import cycle
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageTk , ImageFilter , ImageDraw
import base64
import tkinter.messagebox as messagebox

"""
Author: vanshksingh
Email: vsvsasas@gmail.com
GitHub: [Your GitHub Profile]
Date: Friday 15/12/2023
Description: Network Monitoring Using Ping for NTPC requirement
"""




def encrypt_password(password):
    return base64.b64encode(password.encode()).decode()

def decrypt_password(encrypted_password):
    return base64.b64decode(encrypted_password.encode()).decode()

class PasswordDialog(tk.Toplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success
        self.title("Enter Password")

        self.geometry("300x120")


        tk.Label(self, text="Password:").pack(pady=10)
        self.password_entry = tk.Entry(self, show="*")
        self.password_entry.pack()
        tk.Button(self, text="Submit", command=self.check_password).pack(pady=10)



    def check_password(self):
        entered_password = self.password_entry.get()
        if encrypt_password(entered_password) == self.master.password:
            self.destroy()
            self.on_success()  # Call the callback function to open the settings dialog
        else:
            tk.messagebox.showerror("Error", "Incorrect Password")


class ChangePasswordDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Change Password")
        self.geometry("300x180")

        tk.Label(self, text="Current Password:").pack(pady=5)
        self.current_password_entry = tk.Entry(self, show="*")
        self.current_password_entry.pack()

        tk.Label(self, text="New Password:").pack(pady=5)
        self.new_password_entry = tk.Entry(self, show="*")
        self.new_password_entry.pack()

        tk.Button(self, text="Change", command=self.change_password).pack(pady=10)

    def change_password(self):
        current_password = self.current_password_entry.get()
        new_password = self.new_password_entry.get()
        if encrypt_password(current_password) == self.master.password:
            self.master.password = encrypt_password(new_password)
            self.master.save_password()
            tk.messagebox.showinfo("Success", "Password Changed Successfully")
            self.destroy()
        else:
            tk.messagebox.showerror("Error", "Incorrect Current Password")


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
    def __init__(self, master, app_instance):  # Accept the app_instance argument
        super().__init__(master)
        self.app_instance = app_instance  # Store the reference to the app instance
        self.title("Settings")
        self.geometry("320x900")

        # Initialize selected_tree_var
        self.selected_tree_var = tk.StringVar(value='tree1')

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

        tk.Label(self.scrollable_frame, text="Application Title:").pack(pady=5)
        self.title_entry = tk.Entry(self.scrollable_frame)
        self.title_entry.pack(pady=5)
        self.title_entry.insert(0, self.master.title_text)  # Load current title

        # Add setting fields (organized one below the other)
        self.add_setting_fields()

        # Device management frame
        self.create_device_management_frame()

        # Apply button
        tk.Button(self.scrollable_frame, text="Apply", command=self.apply_settings).pack(pady=10)
        tk.Button(self.scrollable_frame, text="Change Password", command=self.master.change_password).pack(pady=10)

    def add_setting_fields(self):
        # Resolution setting
        tk.Label(self.scrollable_frame, text="Resolution (e.g., 1920x1080):").pack(pady=5)
        self.resolution_entry = tk.Entry(self.scrollable_frame)
        self.resolution_entry.pack(pady=5)
        self.resolution_entry.insert(0, self.master.geometry())

        # Text size setting
        tk.Label(self.scrollable_frame, text="Text Size (e.g., 12):").pack(pady=5)
        self.text_size_entry = tk.Entry(self.scrollable_frame)
        self.text_size_entry.pack(pady=5)
        self.text_size_entry.insert(0, self.master.text_size)

        self.create_font_settings()

        # Label for Table 1 setting
        tk.Label(self.scrollable_frame, text="Label for Table 1:").pack(pady=5)
        self.label_table1_entry = tk.Entry(self.scrollable_frame)
        self.label_table1_entry.pack(pady=5)
        self.label_table1_entry.insert(0, self.master.label_tree1.cget("text"))

        # Label for Table 2 setting
        tk.Label(self.scrollable_frame, text="Label for Table 2:").pack(pady=5)
        self.label_table2_entry = tk.Entry(self.scrollable_frame)
        self.label_table2_entry.pack(pady=5)
        self.label_table2_entry.insert(0, self.master.label_tree2.cget("text"))

        # Hide IP Addresses checkbox
        self.hide_ip_var = tk.BooleanVar(value=self.master.hide_ip)
        tk.Checkbutton(self.scrollable_frame, text="Hide IP Addresses", variable=self.hide_ip_var).pack(pady=10)

    def create_font_settings(self):
        # Widget selection dropdown
        tk.Label(self.scrollable_frame, text="Select Widget:").pack(pady=5)
        self.widget_var = tk.StringVar()
        self.widget_dropdown = ttk.Combobox(self.scrollable_frame, textvariable=self.widget_var, state="readonly")
        self.widget_dropdown['values'] = ["label_tree1", "label_tree2", "tree1", "tree2", "title_label"]
        self.widget_dropdown.pack(pady=5)

        # Font size entry
        tk.Label(self.scrollable_frame, text="Font Size:").pack(pady=5)
        self.font_size_var = tk.StringVar()
        self.font_size_entry = tk.Entry(self.scrollable_frame, textvariable=self.font_size_var)
        self.font_size_entry.pack(pady=5)

        # Font settings
        tk.Label(self.scrollable_frame, text="Font:").pack(pady=5)
        self.font_var = tk.StringVar()
        self.font_dropdown = ttk.Combobox(self.scrollable_frame, textvariable=self.font_var, state="readonly")
        self.font_dropdown['values'] = list(tkFont.families())
        self.font_dropdown.pack(pady=5)
        self.font_dropdown.set(self.app_instance.font_family)  # Set current font

        # Font style (bold, italic, underline)
        self.bold_var = tk.BooleanVar(value=self.app_instance.font_bold)
        self.italic_var = tk.BooleanVar(value=self.app_instance.font_italic)
        self.underline_var = tk.BooleanVar(value=self.app_instance.font_underline)

        tk.Checkbutton(self.scrollable_frame, text="Bold", variable=self.bold_var).pack(pady=2)
        tk.Checkbutton(self.scrollable_frame, text="Italic", variable=self.italic_var).pack(pady=2)
        tk.Checkbutton(self.scrollable_frame, text="Underline", variable=self.underline_var).pack(pady=2)


    def create_device_management_frame(self):
        # Device management frame
        self.entry_frame = tk.Frame(self.scrollable_frame)
        self.entry_frame.pack(pady=10)

        self.name_entry = tk.Entry(self.entry_frame, width=15)
        self.name_entry.grid(row=0, column=0, padx=5)

        self.ip_entry = tk.Entry(self.entry_frame, width=15)
        self.ip_entry.grid(row=0, column=1, padx=5)

        add_button = tk.Button(self.entry_frame, text="Add Device", command=self.add_device)
        add_button.grid(row=1, column=0, padx=5)

        remove_button = tk.Button(self.entry_frame, text="Remove Device", command=self.remove_selected)
        remove_button.grid(row=1, column=1, padx=5)

        tk.Radiobutton(self.entry_frame, text="Table 1", variable=self.selected_tree_var, value='tree1').grid(row=2,
                                                                                                              column=0)
        tk.Radiobutton(self.entry_frame, text="Table 2", variable=self.selected_tree_var, value='tree2').grid(row=2,
                                                                                                              column=1)

    def add_device(self):
        # Logic to add a device
        name = self.name_entry.get()
        ip = self.ip_entry.get()
        if name and ip:
            selected_tree = self.app_instance.tree1 if self.selected_tree_var.get() == 'tree1' else self.app_instance.tree2
            device = Device(name, ip)
            device.item = selected_tree.insert("", tk.END,
                                               values=(len(self.app_instance.devices) + 1, name, ip, "Unknown"))
            device.tree = selected_tree
            self.app_instance.devices[name] = device
            self.name_entry.delete(0, tk.END)
            self.ip_entry.delete(0, tk.END)
            self.app_instance.save_devices()
            self.app_instance.reset_device_cycle()

            # Start monitoring when the first device is added
            if len(self.app_instance.devices) == 1:
                self.app_instance.monitor_devices()

    def remove_selected(self):
        # Logic to remove a selected device
        selected_item = self.master.tree1.selection()
        if selected_item:
            device_to_remove = None
            for name, device in self.master.devices.items():
                if device.item == selected_item[0]:
                    self.master.tree1.delete(selected_item[0])
                    device_to_remove = name
                    break

            if device_to_remove:
                del self.master.devices[device_to_remove]
                self.master.save_devices()
                self.master.reset_device_cycle()
            return

        selected_item = self.master.tree2.selection()
        if selected_item:
            device_to_remove = None
            for name, device in self.master.devices.items():
                if device.item == selected_item[0]:
                    self.master.tree2.delete(selected_item[0])
                    device_to_remove = name
                    break

            if device_to_remove:
                del self.master.devices[device_to_remove]
                self.master.save_devices()
                self.master.reset_device_cycle()
            return

    def apply_settings(self):
        # Logic to apply settings

        # Update IP visibility for each device
        for device in self.master.devices.values():
            if self.master.hide_ip:
                ip_text = '*******'
            else:
                ip_text = device.ip
            device.tree.item(device.item,
                             values=(device.tree.index(device.item) + 1, device.name, ip_text, device.status))

        resolution = self.resolution_entry.get()
        text_size = int(self.text_size_entry.get())
        self.master.update_settings(resolution, text_size, self.hide_ip_var.get())

        new_title = self.title_entry.get()
        self.master.update_title(new_title)  # Update the title immediately

        self.master.label_tree1.config(text=self.label_table1_entry.get())
        self.master.label_tree2.config(text=self.label_table2_entry.get())

        self.master.update_ip_visibility()
        self.master.save_devices()

        self.master.text_size = text_size
        self.master.update_treeview_style()

        self.master.text_size = text_size
        self.master.update_treeview_row_height()

        self.app_instance.font_family = self.font_var.get()
        self.app_instance.font_bold = self.bold_var.get()
        self.app_instance.font_italic = self.italic_var.get()
        self.app_instance.font_underline = self.underline_var.get()
        self.app_instance.apply_font_settings()

        # Update font for the selected widget with font size
        selected_widget = self.widget_var.get()
        font_family = self.font_var.get()
        font_size = self.font_size_var.get()
        font_style = "bold" if self.bold_var.get() else "normal"
        font_style += " italic" if self.italic_var.get() else ""
        font_style += " underline" if self.underline_var.get() else ""
        font = (font_family, font_size, font_style)
        self.app_instance.update_widget_font(selected_widget, font)

        self.destroy()



class DeviceMonitorApp(tk.Tk):
    def __init__(self, resolution='1200x700', text_size=15, hide_ip=False, title_text="Device Monitor Application"):
        super().__init__()
        self.title("Device Monitor")


        # Increase the font size for all elements
        self.text_size = text_size + 5  # Increase text size by 5

        # Adjust the widget sizes (e.g., treeview columns)
        self.tree_column_width = 250  # Increase the width of treeview columns

        self.geometry(resolution)
        self.text_size = text_size
        self.hide_ip = hide_ip
        self.devices = {}
        self.device_cycle = cycle([])
        self.data_file = "device_data.json"
        self.thread_pool = ThreadPoolExecutor(max_workers=10)

        self.title_text = title_text  # Correctly store the title text

        # Initialize selected_tree_var before calling setup_ui
        self.selected_tree_var = tk.StringVar(value='tree1')

        self.font_family = "Helvetica"  # Default font
        self.font_bold = False
        self.font_italic = False
        self.font_underline = False

        self.password_file = "password.json"
        self.password = self.load_password()

        self.setup_ui()
        self.load_devices()
        self.reset_device_cycle()
        self.apply_text_size()  # Apply the initial text size

        self.widget_fonts = {}
        self.load_font_settings()

    def load_password(self):
        if os.path.exists(self.password_file):
            with open(self.password_file, 'r') as file:
                data = json.load(file)
                return data.get('password', encrypt_password("admin"))  # default password is "admin"
        else:
            return encrypt_password("admin")

    def save_password(self):
        with open(self.password_file, 'w') as file:
            json.dump({'password': self.password}, file, indent=4)

    def open_settings(self):
        # Open Password Dialog first. If the password is correct, open_settings_dialog will be called.
        PasswordDialog(self, self.open_settings_dialog)

    def open_settings_dialog(self):
        # Open Settings Dialog only after successful password entry
        SettingsDialog(self, self)

    def change_password(self):
        ChangePasswordDialog(self)


    def update_treeview_row_height(self):
        # Estimate row height based on font size. Adjust the multiplier as needed.
        estimated_row_height = self.text_size + 10

        # Configure the custom Treeview style with the new row height
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Helvetica", self.text_size), rowheight=estimated_row_height)

        # Update the style of both treeviews
        self.tree1.configure(style="Custom.Treeview")
        self.tree2.configure(style="Custom.Treeview")

    def update_widget_font(self, widget_name, font):
        self.widget_fonts[widget_name] = font
        self.apply_font_to_widget(widget_name, font)
        self.save_font_settings()

    def apply_font_to_widget(self, widget_name, font):
        font_family, font_size, font_style = font

        # Use global font size if font_size is empty or invalid
        if not font_size.isdigit():
            font_size = self.text_size
        else:
            font_size = int(font_size)

        font_config = (font_family, font_size, font_style)

        if widget_name == "label_tree1":
            self.label_tree1.config(font=font_config)
        elif widget_name == "label_tree2":
            self.label_tree2.config(font=font_config)
        elif widget_name == "tree1":
            style = ttk.Style()
            style.configure("Treeview", font=font_config )
            self.tree1.configure(style="Treeview" )
        elif widget_name == "tree2":
            style = ttk.Style()
            style.configure("Treeview", font=font_config)
            self.tree2.configure(style="Treeview")
        elif widget_name == "title_label":
            self.title_label.config(font=font_config)

    def save_font_settings(self):
        with open("font_settings.json", "w") as file:
            json.dump(self.widget_fonts, file)

    def load_font_settings(self):
        if os.path.exists("font_settings.json"):
            with open("font_settings.json", "r") as file:
                self.widget_fonts = json.load(file)
                for widget_name, font in self.widget_fonts.items():
                    self.apply_font_to_widget(widget_name, font)

    def apply_font_settings(self):
        font_style = "normal"
        if self.font_bold:
            font_style = "bold"
        if self.font_italic:
            font_style += " italic"
        if self.font_underline:
            font_style += " underline"

        font = (self.font_family, self.text_size, font_style)
        style = ttk.Style()
        style.configure('Treeview', font=font)

    def update_treeview_style(self):
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Helvetica", self.text_size),
                        rowheight=30 + self.text_size)  # Adjust the row height dynamically
        self.tree1.configure(style="Custom.Treeview")
        self.tree2.configure(style="Custom.Treeview")


    def apply_text_size(self):
        # Update text size in Treeview
        style = ttk.Style()
        style.configure('Treeview', font=('Helvetica', self.text_size))

        # Adjust the row height in Treeview
        row_height = 100  # Adjust row height based on text size
        self.tree1.configure(style="my.Treeview", rowheight=row_height)
        self.tree2.configure(style="my.Treeview", rowheight=row_height)



    def update_title(self, new_title):
        self.title_text = new_title
        self.title(new_title)  # Update the title of the main application window
        self.title_label.config(text=new_title)  #

    def update_label(self, label_name, new_text):
        if label_name == "label_tree1":
            self.label_tree1.config(text=new_text)
        elif label_name == "label_tree2":
            self.label_tree2.config(text=new_text)

    def setup_ui(self):
        self.entry_frame = tk.Frame(self)
        self.entry_frame.pack(side="top", fill="x", pady=10)

        desired_heightl = 110
        desired_widthl = 150

        left_spacer = tk.Frame(self.entry_frame, width=20)
        left_spacer.pack(side="left")

        left_image = Image.open("ntpclogo.png")
        left_image = left_image.resize((desired_widthl, desired_heightl))
        left_image = self.make_rounded_image(left_image)
        left_photo = ImageTk.PhotoImage(left_image)

        left_image_label = tk.Label(self.entry_frame, image=left_photo)
        left_image_label.photo = left_photo  # Keep a reference to the image
        left_image_label.pack(side="left", padx=5)



        self.title_label = tk.Label(self.entry_frame, text=self.title_text, font=('Helvetica', 24, 'bold'))
        self.title_label.pack(side="left", expand=True)

        line_label = tk.Label(self.entry_frame, text="_" * 50,
                              font=('Helvetica', 1))  # Adjust font size and line length
        line_label.pack(side="bottom")

        desired_heightr = 100
        desired_widthr = 150

        right_spacer = tk.Frame(self.entry_frame, width=20)
        right_spacer.pack(side="right")

        right_bottom_frame = tk.Frame(self.entry_frame)
        right_bottom_frame.pack(side="right", padx=5)

        right_image = Image.open("auraiya.png")
        right_image = right_image.resize((desired_widthr, desired_heightr))
        right_image = self.make_rounded_image(right_image)
        right_photo = ImageTk.PhotoImage(right_image)

        right_image_label = tk.Label(right_bottom_frame, image=right_photo)
        right_image_label.photo = right_photo  # Keep a reference to the image
        right_image_label.pack(side="top", padx=5 , pady=0)

        settings_button = tk.Button(right_bottom_frame, text="Settings", command=self.open_settings)
        settings_button.pack(side="top", padx=5)  # Add some vertical padding (e.g., 10 pixels)

        # Frames for treeviews including labels
        self.tree_frame1 = tk.Frame(self, padx=10, pady=10)
        self.tree_frame2 = tk.Frame(self, padx=10, pady=10)
        self.tree_frame1.pack(side="left", expand=True, fill="both", padx=10)
        self.tree_frame2.pack(side="right", expand=True, fill="both", padx=10)

        # Create and pack the labels above the treeviews
        self.label_tree1 = tk.Label(self.tree_frame1, text="Table 1", font=('Helvetica', 22, 'bold'))
        self.label_tree2 = tk.Label(self.tree_frame2, text="Table 2", font=('Helvetica', 22, 'bold'))
        self.label_tree1.pack(side="top", fill="x")
        self.label_tree2.pack(side="top", fill="x")

        # Treeviews
        self.tree1 = self.create_treeview(self.tree_frame1, corner_radius=10)
        self.tree2 = self.create_treeview(self.tree_frame2, corner_radius=10)
        self.tree1.pack(expand=True, fill="both", padx=5, pady=5)
        self.tree2.pack(expand=True, fill="both", padx=5, pady=5)

    def make_rounded_image(self, image):
        # Make the border of the image curved
        corner_radius = 10  # You can adjust this value based on your preference

        mask = Image.new("L", image.size, 0)
        draw = ImageDraw.Draw(mask)
        draw.rounded_rectangle((0, 0, image.width, image.height), corner_radius, fill=255)

        result = Image.new("RGBA", image.size, (0, 0, 0, 0))
        result.paste(image, mask=mask)

        return result

    def update_font(self, font_family, font_size, font_style):
        self.font_family = font_family
        self.text_size = int(font_size)
        self.font_style = font_style
        self.apply_font_to_widgets()

    def apply_font_to_widgets(self):
        font = (self.font_family, self.text_size, self.font_style)
        self.option_add("*Font", font)
        self.refresh_widgets(self)

    def refresh_widgets(self, parent):
        for widget in parent.winfo_children():
            widget.update()
            if widget.winfo_children():
                self.refresh_widgets(widget)

    def open_settings(self):
        # Open Password Dialog first. If the password is correct, open_settings_dialog will be called.
        PasswordDialog(self, self.open_settings_dialog)

    def open_settings_dialog(self):
        # Open Settings Dialog only after successful password entry
        SettingsDialog(self, self)


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

    def create_treeview(self, parent, corner_radius):
        style_name = f"rounded_treeview_{corner_radius}"

        # Check if the style has been created before
        if not hasattr(self, '_style_created'):
            style = ttk.Style()
            style.configure(style_name, font=("Helvetica", self.text_size), rowheight=30)
            style.element_create(style_name, "from", "default")
            style.layout(style_name, [('Treeview.treearea', {'sticky': 'nswe'})])

            # Set the flag to indicate that the style has been created
            self._style_created = True

        tree = ttk.Treeview(parent, style=style_name, columns=("Serial", "Name", "IP", "Status"), show='headings')
        tree.heading("Serial", text="Serial No")
        tree.heading("Name", text="Name")
        tree.heading("IP", text="IP")
        tree.heading("Status", text="Status")

        tree.column("Serial", width=10, anchor=tk.CENTER)
        tree.column("Name", width=300, anchor=tk.CENTER)
        tree.column("IP", width=10, anchor=tk.CENTER)
        tree.column("Status", width=50, anchor=tk.CENTER)

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
                devices_copy = dict(self.devices)  # Create a copy of the devices dictionary

                device_to_remove = None
                for name, device in devices_copy.items():
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
        if not self.devices:
            # If there are no devices, reset the device cycle and return
            self.reset_device_cycle()
            return

        try:
            device = next(self.device_cycle)
        except StopIteration:
            # Reset the device cycle if it's empty and try again
            self.reset_device_cycle()
            try:
                device = next(self.device_cycle)
            except StopIteration:
                # If it's still empty, then there are no devices to monitor
                return

        self.set_to_grey(device)
        self.after(1000, lambda: self.thread_pool.submit(self.ping_and_update, device))
        self.after(1000, self.monitor_devices)  # Continue with the next device

    # Add this function to initiate monitoring
    def start_monitoring(self):
        if not self.devices:
            # If there are no devices, reset the device cycle and return
            self.reset_device_cycle()
            return

        self.monitor_devices()

    def set_to_grey(self, device):
        item_id = device.item
        tree_name = device.tree

        # Check if the item exists in the specified tree
        if item_id in tree_name.get_children():
            tree_name.item(item_id, tags=('grey',))
        else:
            print(f"Item {item_id} not found in the {tree_name} tree.")

    def ping_and_update(self, device):
        status = ping(device.ip)
        self.after(0, lambda: self.update_device_status(device, status))

    def save_devices(self):
        try:
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
                },
                'settings': {
                    'title': self.title_text,  # Existing title
                    'text_size': self.text_size,  # Save the current font size
                    'hide_ip': self.hide_ip  # Save the state of IP address visibility
                }
            }

            with open(self.data_file, 'w') as file:
                json.dump(device_data, file, indent=4)
        except Exception as e:
            print(f"Error saving devices: {e}")

    def load_devices(self):
        if not os.path.exists(self.data_file):
            return

        with open(self.data_file, 'r') as file:
            loaded_data = json.load(file)
            loaded_devices = loaded_data.get('devices', {})
            labels = loaded_data.get('labels', {})
            settings = loaded_data.get('settings', {})

            # Load settings
            loaded_title = settings.get('title', "Device Monitor Application")
            self.title_text = loaded_title  # Set the title_text to the loaded title
            self.update_treeview_row_height()

            # Set hide_ip before loading devices
            self.hide_ip = settings.get('hide_ip', False)

            for name, data in loaded_devices.items():
                ip = data.get('ip')
                table_choice = data.get('table', 'tree1')
                tree = self.tree1 if table_choice == 'tree1' else self.tree2
                device = Device(name, ip)
                device.tree = tree
                if self.hide_ip:
                    ip = '*******'
                device.item = tree.insert("", tk.END, values=(len(self.devices) + 1, name, ip, "Unknown"))
                self.devices[name] = device

            # Update the title after loading all devices
            self.update_title(loaded_title)

            # Update the labels after loading all devices
            self.label_tree1.config(text=labels.get('label_tree1', "Table 1"))
            self.label_tree2.config(text=labels.get('label_tree2', "Table 2"))

            # Update the IP visibility after loading all devices
            self.update_ip_visibility()
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
    app = DeviceMonitorApp(resolution='1920x1080', text_size=15, title_text="Your Title Here")
    app.start_monitoring()
    app.tk_setPalette(background='light blue', foreground='black', activeBackground='gray80', activeForeground='black')
    app.mainloop()
