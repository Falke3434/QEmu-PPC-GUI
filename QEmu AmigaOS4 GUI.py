import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import configparser
import os

# Pre-configured QEMU-PPC configurations
configurations = {
    "AmigaOne": {
        "machine": "amigaone",
        "memory": "2048",
        "vga": "none",
        "graphics": "sm501",
        "display": "sdl",
        "network1": "rtl8139,netdev=net0",
        "network2": "user,id=net0",
        "kernel_required": False,
        "loader_required": True,
        "usb_storage": True
    },
    "Pegasos2": {
        "machine": "pegasos2",
        "memory": "2048",
        "vga": "none",
        "graphics": "sm501",
        "display": "sdl",
        "network1": "rtl8139,netdev=net0",
        "network2": "user,id=net0",
        "kernel_required": True,
        "loader_required": False,
        "usb_storage": True
    },
    "Sam460ex": {
        "machine": "sam460ex",
        "memory": "2048",
        "vga": "none",
        "graphics": "sm501",
        "display": "sdl",
        "network1": "rtl8139,netdev=net0",
        "network2": "user,id=net0",
        "kernel_required": False,
        "loader_required": False,
        "usb_storage": False
    }
}

# Configuration file path
config_file = 'qemu_config.ini'

# Create configuration file with default values if it doesn't exist
def create_config_file():
    config = configparser.ConfigParser()
    if not os.path.exists(config_file):
        config['Settings'] = {
            'Configuration': 'sam460ex',  # Default configuration
            'ISO': '',
            'HDD1': '',
            'HDD2': '',
            'Kernel': '',
            'Initrd': '',
            'Loader1': '',
            'Loader2': '',
            'QEMU_Share': '',
            'Fullscreen': 'False'
        }
        with open(config_file, 'w') as configfile:
            config.write(configfile)

# Load configuration from file
def load_config():
    config = configparser.ConfigParser()
    if os.path.exists(config_file):
        config.read(config_file)
        try:
            config_var.set(config['Settings']['Configuration'])
            iso_var.set(config['Settings']['ISO'])
            hdd1_var.set(config['Settings']['HDD1'])
            hdd2_var.set(config['Settings']['HDD2'])
            kernel_var.set(config['Settings']['Kernel'])
            initrd_var.set(config['Settings']['Initrd'])
            loader1_var.set(config['Settings']['Loader1'])
            loader2_var.set(config['Settings']['Loader2'])
            qemu_share_var.set(config['Settings']['QEMU_Share'])
            fullscreen_var.set(config.getboolean('Settings', 'Fullscreen'))
        except KeyError:
            messagebox.showwarning("Warning", "Failed to load configuration settings.")

# Save configuration to file
def save_config():
    config = configparser.ConfigParser()
    config['Settings'] = {
        'Configuration': config_var.get(),
        'ISO': iso_var.get(),
        'HDD1': hdd1_var.get(),
        'HDD2': hdd2_var.get(),
        'Kernel': kernel_var.get(),
        'Initrd': initrd_var.get(),
        'Loader1': loader1_var.get(),
        'Loader2': loader2_var.get(),
        'QEMU_Share': qemu_share_var.get(),
        'Fullscreen': fullscreen_var.get()
    }
    with open(config_file, 'w') as configfile:
        config.write(configfile)

# Function to show the selected configuration details in a new window
def show_configuration():
    config = configurations[config_var.get()]
    details = (
        f"Configuration: {config_var.get()}\n\n"

        f"Machine: {config['machine']}\n"
        f"Memory: {config['memory']} MB\n"
        f"VGA Device: {config['vga']}\n"
        f"Graphics Device: {config['graphics']}\n"
        f"Display: {config['display']}\n"
        f"Network: {config['network1']},{config['network2']}\n"
        f"Kernel Required: {'Yes' if config['kernel_required'] else 'No'}\n"
        f"Loader Required: {'Yes' if config['loader_required'] else 'No'}\n"
        f"USB Storage Enabled: {'Yes' if config['usb_storage'] else 'No'}\n\n"

        f"ISO Path: {iso_var.get()}\n"
        f"HDD 1 Path: {hdd1_var.get()}\n"
        f"HDD 2 Path: {hdd2_var.get()}\n"
        f"BBoot Path: {kernel_var.get() if config['kernel_required'] else 'N/A'}\n"
        f"Kickstart Path: {initrd_var.get() if config['kernel_required'] else 'N/A'}\n"
        f"BBoot Path: {loader1_var.get() if config['loader_required'] else 'N/A'}\n"
        f"Kickstart Path: {loader2_var.get() if config['loader_required'] else 'N/A'}\n"
        f"QEMU Share Folder: {qemu_share_var.get()}\n\n"

        f"Fullscreen: {'Enabled' if fullscreen_var.get() else 'Disabled'}"
    )

    # Create a new window to display the details
    show_window = tk.Toplevel(root)
    show_window.title("Configuration Details")

    # Display the details in a text widget for better formatting
    text_widget = tk.Text(show_window, wrap="word", width=65, height=23)
    text_widget.insert("1.0", details)
    text_widget.config(state="disabled")  # Make the text read-only
    text_widget.pack(padx=10, pady=10)

# Function to start QEMU with the selected configuration and files
def start_qemu():
    config = configurations[config_var.get()]
    command = [
        "qemu-system-ppc",
        "-M", config["machine"],
        "-m", config["memory"],
        "-vga", config["vga"],
        "-display", config["display"],
        "-device", config["network1"],
        "-netdev", config["network2"]
    ]

    # Add graphics device if specified
    if config["graphics"]:
        command.extend(["-device", config["graphics"]])

    # Add ISO and HDD files
    if iso_var.get():
        command.extend(["-cdrom", iso_var.get()])
    if hdd1_var.get():
        command.extend(["-drive", f"file={hdd1_var.get()},format=raw,index=0,media=disk"])
    if hdd2_var.get():
        command.extend(["-drive", f"file={hdd2_var.get()},format=raw,index=1,media=disk"])

    # Add USB storage for Pegasos2 and AmigaOne
    if qemu_share_var.get():
        command.extend([
            "-drive", f"file=fat:rw:{qemu_share_var.get()},id=ufat,format=raw,if=none",
            "-device", "usb-storage,drive=ufat"
        ])

    # Add kernel and initrd if required and entered
    if config["kernel_required"]:
        if kernel_var.get():
            command.extend(["-kernel", kernel_var.get()])
        else:
            messagebox.showwarning("Warning", "Please select a kernel file for the selected configuration.")
            return

        if initrd_var.get():
            command.extend(["-initrd", initrd_var.get()])

    # Add loader if required and entered
    if config["loader_required"]:
        if loader1_var.get():
            command.extend(["-device", f"loader,cpu-num=0,file={loader1_var.get()}"])
        else:
            messagebox.showwarning("Warning", "Please select a loader file for the selected configuration.")
            return

        if loader2_var.get():
            command.extend(["-device", f"loader,addr=0x600000,file={loader2_var.get()}"])

    # Add fullscreen option if checked
    if fullscreen_var.get():
        command.append("-full-screen")

    try:
        subprocess.run(command)
        save_config()  # Save settings after starting QEMU
    except Exception as e:
        messagebox.showerror("Error", f"Error starting QEMU: {e}")

# Function to select an ISO file
def select_iso():
    file_path = filedialog.askopenfilename(filetypes=[("ISO Files", "*.iso"), ("All Files", "*.*")])
    if file_path:
        iso_var.set(file_path)

# Function to select an HDD file
def select_hdd1():
    file_path = filedialog.askopenfilename(filetypes=[("Disk Files", "*.img;*.qcow2"), ("All Files", "*.*")])
    if file_path:
        hdd1_var.set(file_path)

# Function to select an HDD file
def select_hdd2():
    file_path = filedialog.askopenfilename(filetypes=[("Disk Files", "*.img;*.qcow2"), ("All Files", "*.*")])
    if file_path:
        hdd2_var.set(file_path)

# Function to create a new HDD image using qemu-img
def create_hdd_image(hdd_var):
    def create_image():
        img_name = img_name_var.get()
        img_size = img_size_var.get()
        img_format = img_format_var.get()

        if not img_name or not img_size:
            messagebox.showwarning("Warning", "Please specify both the image name and size.")
            return

        # Append appropriate file extension based on the format
        if img_format == "qcow2":
            img_name += ".qcow2"
        elif img_format == "raw":
            img_name += ".img"

        command = ["qemu-img", "create", "-f", img_format, img_name, img_size]
        try:
            subprocess.run(command, check=True)
            hdd_var.set(img_name)
            create_window.destroy()
        except Exception as e:
            messagebox.showerror("Error", f"Error creating HDD image: {e}")

    create_window = tk.Toplevel(root)
    create_window.title("Create HDD Image")

    # Create input fields for image name, size, and format
    ttk.Label(create_window, text="Image Name:").grid(row=0, column=0, sticky=tk.W)
    img_name_var = tk.StringVar()
    img_name_entry = ttk.Entry(create_window, textvariable=img_name_var, width=30)
    img_name_entry.grid(row=0, column=1)

    ttk.Label(create_window, text="Image Size (e.g., 10G):").grid(row=1, column=0, sticky=tk.W)
    img_size_var = tk.StringVar(value="2G")  # Default Size
    img_size_entry = ttk.Entry(create_window, textvariable=img_size_var, width=30)
    img_size_entry.grid(row=1, column=1)

    ttk.Label(create_window, text="Image Format:").grid(row=2, column=0, sticky=tk.W)
    img_format_var = tk.StringVar(value="raw")  # Default Format
    img_format_entry = ttk.Combobox(create_window, textvariable=img_format_var, values=["qcow2", "raw"], state="readonly")
    img_format_entry.grid(row=2, column=1)

    create_button = ttk.Button(create_window, text="Create", command=create_image)
    create_button.grid(row=3, columnspan=2, pady=10)

# Function to select a kernel file (for Pegasos2)
def select_kernel():
    file_path = filedialog.askopenfilename(filetypes=[("Kernel Files", "bboot"), ("All Files", "*.*")])
    if file_path:
        kernel_var.set(file_path)

# Function to select an initrd file (for Pegasos2)
def select_initrd():
    file_path = filedialog.askopenfilename(filetypes=[("Initrd Files", "kickstart.zip"), ("All Files", "*.*")])
    if file_path:
        initrd_var.set(file_path)

# Function to select a loader file for AmigaOne
def select_loader1():
    file_path = filedialog.askopenfilename(filetypes=[("Loader Files", "bboot"), ("All Files", "*.*")])
    if file_path:
        loader1_var.set(file_path)

def select_loader2():
    file_path = filedialog.askopenfilename(filetypes=[("Loader Files", "kickstart.zip"), ("All Files", "*.*")])
    if file_path:
        loader2_var.set(file_path)

# Function to select the QEMU shared folder
def select_qemu_share():
    folder_path = filedialog.askdirectory()
    if folder_path:
        qemu_share_var.set(folder_path)

# Update kernel and initrd fields visibility based on the selected configuration
def update_kernel_initrd_fields(*args):
    if configurations[config_var.get()]["kernel_required"]:
        kernel_label.grid(row=4, column=0, sticky=tk.W)
        kernel_entry.grid(row=4, column=1)
        kernel_button.grid(row=4, column=2)
        initrd_label.grid(row=5, column=0, sticky=tk.W)
        initrd_entry.grid(row=5, column=1)
        initrd_button.grid(row=5, column=2)
    else:
        kernel_label.grid_remove()
        kernel_entry.grid_remove()
        kernel_button.grid_remove()
        initrd_label.grid_remove()
        initrd_entry.grid_remove()
        initrd_button.grid_remove()

# Update loader selection fields based on the selected configuration
def update_loader_selection(*args):
    if configurations[config_var.get()]["loader_required"]:
        loader1_label.grid(row=6, column=0, sticky=tk.W)
        loader1_entry.grid(row=6, column=1)
        loader1_button.grid(row=6, column=2)
        loader2_label.grid(row=7, column=0, sticky=tk.W)
        loader2_entry.grid(row=7, column=1)
        loader2_button.grid(row=7, column=2)
    else:
        loader1_label.grid_remove()
        loader1_entry.grid_remove()
        loader1_button.grid_remove()
        loader2_label.grid_remove()
        loader2_entry.grid_remove()
        loader2_button.grid_remove()

def update_usb_storage_selection(*args):
    if configurations[config_var.get()]["usb_storage"]:
        qemu_share_label.grid(row=8, column=0, sticky=tk.W)
        qemu_share_entry.grid(row=8, column=1)
        qemu_share_button.grid(row=8, column=2)
    else:
        qemu_share_label.grid_remove()
        qemu_share_entry.grid_remove()
        qemu_share_button.grid_remove()

class Tooltip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None

        # Bind the events for showing and hiding the tooltip
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        if self.tooltip_window is not None:
            return  # Tooltip is already visible
        x, y, _, _ = self.widget.bbox("insert")  # Get the position of the widget
        x = x + self.widget.winfo_rootx() + 25  # Offset for better visibility
        y = y + self.widget.winfo_rooty() + 25  # Offset for better visibility

        # Create a tooltip window
        self.tooltip_window = tk.Toplevel(self.widget)
        self.tooltip_window.wm_overrideredirect(True)  # Remove window decorations
        self.tooltip_window.wm_geometry(f"+{x}+{y}")
        label = ttk.Label(self.tooltip_window, text=self.text, relief="solid", borderwidth=1, background="lightyellow")
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None

# GUI Setup
root = tk.Tk()
root.title("QEmu AmigaOS4 GUI")

# Set the Window size to be fixed
root.resizable(False, False)

#Set App Icon
root.iconbitmap(r'bb.ico') 

# Add Menu Bar
menu_bar = tk.Menu(root)
root.config(menu=menu_bar)

frame = ttk.Frame(root, padding="10")
frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

# Configuration selection
config_label = ttk.Label(frame, text="Configuration:")
config_label.grid(row=0, column=0, sticky=tk.W)
config_var = tk.StringVar(value="Sam460ex")
config_var.trace("w", update_kernel_initrd_fields)
config_var.trace("w", update_loader_selection)
config_var.trace("w", update_usb_storage_selection)
config_menu = ttk.Combobox(frame, textvariable=config_var, values=list(configurations.keys()), state="readonly")
config_menu.grid(row=0, column=1, columnspan=2)

# Add the Show button to the GUI
show_button = ttk.Button(frame, text="Show", command=show_configuration)
show_button.grid(row=0, column=3, padx=(5, 0))

# ISO selection
iso_label = ttk.Label(frame, text="ISO:")
iso_label.grid(row=1, column=0, sticky=tk.W)
iso_var = tk.StringVar()
iso_entry = ttk.Entry(frame, textvariable=iso_var, width=30)
iso_entry.grid(row=1, column=1)
iso_button = ttk.Button(frame, text="Browse", command=select_iso)
iso_button.grid(row=1, column=2)
Tooltip(iso_entry, "Select Iso File")

# HDD1 selection
hdd1_label = ttk.Label(frame, text="HDD 1:")
hdd1_label.grid(row=2, column=0, sticky=tk.W)
hdd1_var = tk.StringVar()
hdd1_entry = ttk.Entry(frame, textvariable=hdd1_var, width=30)
hdd1_entry.grid(row=2, column=1)
hdd1_button = ttk.Button(frame, text="Browse", command=select_hdd1)
hdd1_button.grid(row=2, column=2)
hdd1_create_button = ttk.Button(frame, text="Create", command=lambda: create_hdd_image(hdd1_var))
hdd1_create_button.grid(row=2, column=3)
Tooltip(hdd1_entry, "Select Image File")

# HDD2 selection
hdd2_label = ttk.Label(frame, text="HDD 2:")
hdd2_label.grid(row=3, column=0, sticky=tk.W)
hdd2_var = tk.StringVar()
hdd2_entry = ttk.Entry(frame, textvariable=hdd2_var, width=30)
hdd2_entry.grid(row=3, column=1)
hdd2_button = ttk.Button(frame, text="Browse", command=select_hdd2)
hdd2_button.grid(row=3, column=2)
hdd2_create_button = ttk.Button(frame, text="Create", command=lambda: create_hdd_image(hdd2_var))
hdd2_create_button.grid(row=3, column=3)
Tooltip(hdd2_entry, "Select Image File")

# Kernel input (for Pegasos2)
kernel_label = ttk.Label(frame, text="BBoot:")
kernel_var = tk.StringVar()
kernel_entry = ttk.Entry(frame, textvariable=kernel_var, width=30)
kernel_button = ttk.Button(frame, text="Browse", command=select_kernel)
Tooltip(kernel_entry, "Select the BBoot File")

# Initrd input (for Pegasos2)
initrd_label = ttk.Label(frame, text="Kickstart (Pegasos):")
initrd_var = tk.StringVar()
initrd_entry = ttk.Entry(frame, textvariable=initrd_var, width=30)
initrd_button = ttk.Button(frame, text="Browse", command=select_initrd)
Tooltip(initrd_entry, "Select the Kickstart.zip File for Pegasos2")

# Loader input for AmigaOne
loader1_label = ttk.Label(frame, text="BBoot:")
loader1_var = tk.StringVar()
loader1_entry = ttk.Entry(frame, textvariable=loader1_var, width=30)
loader1_button = ttk.Button(frame, text="Browse", command=select_loader1)
Tooltip(loader1_entry, "Select the BBoot File")

loader2_label = ttk.Label(frame, text="Kickstart (AmigaOne):")
loader2_var = tk.StringVar()
loader2_entry = ttk.Entry(frame, textvariable=loader2_var, width=30)
loader2_button = ttk.Button(frame, text="Browse", command=select_loader2)
Tooltip(loader2_entry, "Select the Kickstart.zip File for AmigaOne")

# QEMU shared folder selection
qemu_share_label = ttk.Label(frame, text="QEMU Share Folder:")
qemu_share_var = tk.StringVar()
qemu_share_entry = ttk.Entry(frame, textvariable=qemu_share_var, width=30)
qemu_share_button = ttk.Button(frame, text="Browse", command=select_qemu_share)

# Fullscreen enabled/disabled label and checkbox
fullscreen_var = tk.BooleanVar()
fullscreen_checkbox = ttk.Checkbutton(frame, variable=fullscreen_var)
fullscreen_checkbox.grid(row=10, column=1, sticky=tk.W)
fullscreen_label = ttk.Label(frame, text="Fullscreen Enabled/Disabled:")
fullscreen_label.grid(row=10, column=0, sticky=tk.W)
Tooltip(fullscreen_checkbox, "Enable or Disable Fullscreen")

# Start button
start_button = ttk.Button(frame, text="Start QEMU", command=start_qemu)
start_button.grid(row=12, column=0, columnspan=5, pady=10)

# Load previous configuration
load_config()
update_kernel_initrd_fields()
update_loader_selection()
update_usb_storage_selection()

root.mainloop()
