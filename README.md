
# Network Monitoring Application

This Python application for network monitoring using Ping was built for NTPC requirements. Developed by **vanshksingh**, the application utilizes the Tkinter library for the graphical user interface and provides features such as device management, settings configuration, and password protection.


![image](https://github.com/vanshksingh/NMS-NTPC/assets/114809624/3a5c4293-e76c-4680-a10d-9494fe421a76)



## Features

- **Device Management:** Add and remove network devices for monitoring.
- **Settings Configuration:** Adjust resolution, text size, and customize labels for tables.
- **Password Protection:** Secure the application with a password.
- **Font Customization:** Customize font settings for various UI elements.

## How to Run

Ensure that you have Python installed on your system. Run the following command in your terminal to execute the application:

python nms.py



## Dependencies

- **tkinter:** GUI library for building the application interface.
- **PIL:** Python Imaging Library for image processing.
- **base64:** Encoding and decoding binary data using base64.
- **concurrent.futures:** Provides a high-level interface for asynchronously executing functions using threads.
- **json:** JSON encoding and decoding.
- **subprocess:** Spawning processes and executing commands.
- **platform:** Access to underlying platform's identifying data.
- **itertools:** Functions creating iterators for efficient looping.
- **tkinter.font:** Font handling in Tkinter.
- **tkinter.messagebox:** Message box for displaying messages.


Build as Executable (Using PyInstaller)
To create an executable (exe) file, you can use PyInstaller. Install PyInstaller first:


pip install pyinstaller

Then, navigate to the directory containing your nms.py script and run:

pyinstaller --onefile nms.py

This will create a dist directory containing the executable file. You can distribute this standalone executable to run the application without needing to install Python.
You have to put images and dependencies in the same file as the exe for it to run , or it will throw error. 

csharp
Copy code

Copy and paste this content into a Markdown file (e.g., `README.md`).

## Author Information

- **Author:** vanshksingh
- **Email:** vsvsasas@gmail.com
- **GitHub:** [vanshksingh](https://github.com/vanshksingh)
- **Date:** Friday 15/12/2023


