import tkinter as tk
from tkinter import filedialog, messagebox
import subprocess
import configparser
import os

class QEmuPPCGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("QEmu PPC GUI v1.0")
        self.root.geometry("500x720")  # Set window size

        self.config_file = "qemu_ppc_config.ini"
        self.options_file = "qemu_ppc_options.ini"
        self.load_options()
        self.create_widgets()
        self.load_settings()

    def load_options(self):
        self.bios_pegasos2 = ''
        self.kernel = ''
        self.initrd = ''
        self.bios_amigaone = ''
        self.loader1 = ''
        self.loader2 = ''
        self.graphic_bios = ''

        """Load the Machine and CPU options from a separate INI file."""
        if os.path.exists(self.options_file):
            config = configparser.ConfigParser()
            config.read(self.options_file)

            self.bios_pegasos2 = config.get("Loaders", "bios_pegasos2", fallback="D:/Emulation/QEmu/roms/Pegasos2/pegasos2.rom")
            self.kernel = config.get("Loaders", "kernel", fallback="D:/Emulation/QEmu/bboot-0.7/bboot")
            self.initrd = config.get("Loaders", "initrd", fallback="D:/Emulation/QEmu/roms/Pegasos2/Kickstart.zip")
            self.bios_amigaone = config.get("Loaders", "bios_amigaone", fallback="D:/Emulation/QEmu/roms/AmigaOne/u-boot-amigaone.bin")
            self.loader1 = config.get("Loaders", "loader1", fallback="loader,cpu-num=0,file=D:/Emulation/QEmu/bboot-0.7/bboot")
            self.loader2 = config.get("Loaders", "loader2", fallback="loader,addr=0x600000,file=D:/Emulation/QEmu/roms/AmigaOne/Kickstart.zip")
            self.graphic_bios = config.get("Loaders", "graphic_bios", fallback="D:/Emulation/QEmu/roms/ati_rage128pro.rom")

            # Load Machine options
            machines = config.get("Machines", "Options", fallback="amigaone;pegasos2;sam460ex;mac99")
            self.machine_options = machines.split(';')

            # Load CPU options
            cpus = config.get("CPUs", "Options", fallback="G3;G4")
            self.cpu_options = cpus.split(';')
        else:
            # Default values if options file is missing
            self.machine_options = ["amigaone", "pegasos2", "sam460ex", "mac99"]
            self.cpu_options = ["g3", "g4"]
            self.bios_pegasos2 = ["D:/Emulation/QEmu/roms/Pegasos2/pegasos2.rom"]
            self.kernel = ["D:/Emulation/QEmu/bboot-0.7/bboot"]
            self.initrd = ["D:/Emulation/QEmu/roms/Pegasos2/Kickstart.zip"]
            self.bios_amigaone = ["D:/Emulation/QEmu/roms/AmigaOne/u-boot-amigaone.bin"]
            self.loader1 = ["loader,cpu-num=0,file=D:/Emulation/QEmu/bboot-0.7/bboot"]
            self.loader2 = ["loader,addr=0x600000,file=D:/Emulation/QEmu/roms/AmigaOne/Kickstart.zip"]
            self.graphic_bios = ["D:/Emulation/QEmu/roms/ati_rage128pro.rom"]

    def create_widgets(self):
        # QEMU PPC exe
        tk.Label(self.root, text="QEMU PPC exe:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.qemu_exe = tk.Entry(self.root, width=40)
        self.qemu_exe.grid(row=0, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_qemu_exe).grid(row=0, column=2, padx=5, pady=5)

        # Machine selection
        tk.Label(self.root, text="Machine:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.machine_type = tk.StringVar(value=self.machine_options[0])
        self.machine_menu = tk.OptionMenu(self.root, self.machine_type, *self.machine_options, command=self.update_machine_specific_fields)
        self.machine_menu.grid(row=1, column=1, padx=5, pady=5)

        # Bios Pegasos2 Options (checkbox and entry)
        self.bios_pegasos2_enabled_var = tk.BooleanVar()
        self.bios_pegasos2_checkbox = tk.Checkbutton(self.root, text="Bios:", variable=self.bios_pegasos2_enabled_var)
        self.bios_pegasos2_checkbox.grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.bios_pegasos2_entry = tk.Entry(self.root, width=40)
        self.bios_pegasos2_entry.grid(row=2, column=1, padx=5, pady=5)
        self.bios_pegasos2_entry.insert(0, self.bios_pegasos2)

        # Add Browse button for Pegasos2 Bios
        self.bios_pegasos2_browse_button = tk.Button(self.root, text="Browse", command=self.browse_bios_pegasos2)
        self.bios_pegasos2_browse_button.grid(row=2, column=2, padx=5, pady=5)

        # Kernel Options (checkbox and entry)
        self.kernel_enabled_var = tk.BooleanVar()
        self.kernel_checkbox = tk.Checkbutton(self.root, text="Kernel:", variable=self.kernel_enabled_var)
        self.kernel_checkbox.grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.kernel_entry = tk.Entry(self.root, width=40)
        self.kernel_entry.grid(row=3, column=1, padx=5, pady=5)
        self.kernel_entry.insert(0, self.kernel)

        # Initrd Options (checkbox and entry)
        self.initrd_enabled_var = tk.BooleanVar()
        self.initrd_checkbox = tk.Checkbutton(self.root, text="Initrd:", variable=self.initrd_enabled_var)
        self.initrd_checkbox.grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.initrd_entry = tk.Entry(self.root, width=40)
        self.initrd_entry.grid(row=4, column=1, padx=5, pady=5)
        self.initrd_entry.insert(0, self.initrd)

        # Bios AmigaOne Options (checkbox and entry)
        self.bios_amigaone_enabled_var = tk.BooleanVar()
        self.bios_amigaone_checkbox = tk.Checkbutton(self.root, text="Bios:", variable=self.bios_amigaone_enabled_var)
        self.bios_amigaone_checkbox.grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.bios_amigaone_entry = tk.Entry(self.root, width=40)
        self.bios_amigaone_entry.grid(row=2, column=1, padx=5, pady=5)
        self.bios_amigaone_entry.insert(0, self.bios_amigaone)

        # Add Browse button for AmigaOne Bios
        self.bios_amigaone_browse_button = tk.Button(self.root, text="Browse", command=self.browse_bios_amigaone)
        self.bios_amigaone_browse_button.grid(row=2, column=2, padx=5, pady=5)

        # Loader1 Options (checkbox and entry)
        self.loader1_enabled_var = tk.BooleanVar()
        self.loader1_checkbox = tk.Checkbutton(self.root, text="Loader 1:", variable=self.loader1_enabled_var)
        self.loader1_checkbox.grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.loader1_entry = tk.Entry(self.root, width=40)
        self.loader1_entry.grid(row=3, column=1, padx=5, pady=5)
        self.loader1_entry.insert(0, self.loader1)

        # Loader2 Options (checkbox and entry)
        self.loader2_enabled_var = tk.BooleanVar()
        self.loader2_checkbox = tk.Checkbutton(self.root, text="Loader 2:", variable=self.loader2_enabled_var)
        self.loader2_checkbox.grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.loader2_entry = tk.Entry(self.root, width=40)
        self.loader2_entry.grid(row=4, column=1, padx=5, pady=5)
        self.loader2_entry.insert(0, self.loader2)

        # CPU selection (optional with checkbox)
        self.cpu_enabled_var = tk.BooleanVar()
        self.cpu_checkbox = tk.Checkbutton(self.root, text="Enable CPU (optional):", variable=self.cpu_enabled_var, command=self.toggle_cpu_entry)
        self.cpu_checkbox.grid(row=7, column=0, sticky='w', padx=5, pady=5)

        self.cpu_entry = tk.StringVar(value="")
        self.cpu_menu = tk.OptionMenu(self.root, self.cpu_entry, *self.cpu_options)
        self.cpu_menu.grid(row=7, column=1, padx=5, pady=5)
        self.cpu_menu.config(state=tk.DISABLED)  # Disabled by default

        # RAM Size
        tk.Label(self.root, text="RAM Size (MB):").grid(row=9, column=0, sticky='w', padx=5, pady=5)
        self.ram_size = tk.Entry(self.root, width=10)
        self.ram_size.grid(row=9, column=1, padx=5, pady=5)
        self.ram_size.insert(0, "")

        # ISO File (optional)
        tk.Label(self.root, text="ISO File (optional):").grid(row=10, column=0, sticky='w', padx=5, pady=5)
        self.iso_file = tk.Entry(self.root, width=40)
        self.iso_file.grid(row=10, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_iso_file).grid(row=10, column=2, padx=5, pady=5)

        # Harddisk 1 (optional)
        tk.Label(self.root, text="Harddisk 1 (optional):").grid(row=11, column=0, sticky='w', padx=5, pady=5)
        self.harddisk1 = tk.Entry(self.root, width=40)
        self.harddisk1.grid(row=11, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_harddisk1).grid(row=11, column=2, padx=5, pady=5)

        # Harddisk 2 (optional)
        tk.Label(self.root, text="Harddisk 2 (optional):").grid(row=12, column=0, sticky='w', padx=5, pady=5)
        self.harddisk2 = tk.Entry(self.root, width=40)
        self.harddisk2.grid(row=12, column=1, padx=5, pady=5)
        tk.Button(self.root, text="Browse", command=self.browse_harddisk2).grid(row=12, column=2, padx=5, pady=5)

        # VGA Device
        self.vga_device_enabled_var = tk.BooleanVar(value=True)
        self.vga_device_checkbox = tk.Checkbutton(self.root, text="Enable VGA Device", variable=self.vga_device_enabled_var, command=self.toggle_vga_menu)
        self.vga_device_checkbox.grid(row=13, column=0, sticky='w', padx=5, pady=5)

        self.vga_device = tk.StringVar(value="none")
        vga_options = ["std", "none", "cirrus"]
        self.vga_menu = tk.OptionMenu(self.root, self.vga_device, *vga_options)
        self.vga_menu.grid(row=13, column=1, padx=5, pady=5)
        self.vga_menu.config(state=tk.NORMAL)  # Initially enabled

        # Graphic Device
        self.graphic_device_enabled_var = tk.BooleanVar(value=True)
        self.graphic_device_checkbox = tk.Checkbutton(self.root, text="Enable Graphic Device", variable=self.graphic_device_enabled_var, command=self.toggle_graphic_menu)
        self.graphic_device_checkbox.grid(row=14, column=0, sticky='w', padx=5, pady=5)

        self.graphic_device = tk.StringVar(value="sm501")
        graphic_options = ["sm501", "ati-vga", "cirrus-vga", "VGA"]
        self.graphic_menu = tk.OptionMenu(self.root, self.graphic_device, *graphic_options, command=self.on_graphic_device_change)
        self.graphic_menu.grid(row=14, column=1, padx=5, pady=5)
        self.graphic_menu.config(state=tk.NORMAL)  # Initially enabled

        # Graphic Bios specific (checkbox and entry)
        self.graphic_bios_enabled_var = tk.BooleanVar()
        self.graphic_bios_checkbox = tk.Checkbutton(self.root, text="Graphic Bios:", variable=self.graphic_bios_enabled_var)
        self.graphic_bios_checkbox.grid(row=15, column=0, sticky='w', padx=5, pady=5)
        self.graphic_bios_entry = tk.Entry(self.root, width=40)
        self.graphic_bios_entry.grid(row=15, column=1, padx=5, pady=5)
        self.graphic_bios_entry.insert(0, self.graphic_bios)

        # Add Browse button for Graphic Bios
        self.graphic_bios_browse_button = tk.Button(self.root, text="Browse", command=self.browse_graphic_bios)
        self.graphic_bios_browse_button.grid(row=15, column=2, padx=5, pady=5)

        # Display
        self.display_enabled_var = tk.BooleanVar(value=True)
        self.display_checkbox = tk.Checkbutton(self.root, text="Enable Display", variable=self.display_enabled_var, command=self.toggle_display_menu)
        self.display_checkbox.grid(row=16, column=0, sticky='w', padx=5, pady=5)

        self.display = tk.StringVar(value="gtk")
        display_options = ["gtk", "sdl", "egl-headless", "curses", "spice-app", "dbus"]
        self.display_menu = tk.OptionMenu(self.root, self.display, *display_options)
        self.display_menu.grid(row=16, column=1, padx=5, pady=5)
        self.display_menu.config(state=tk.NORMAL)  # Initially enabled

        # Fullscreen (optional)
        self.fullscreen_var = tk.BooleanVar()
        self.fullscreen_checkbox = tk.Checkbutton(self.root, text="Enable Fullscreen (optional)", variable=self.fullscreen_var)
        self.fullscreen_checkbox.grid(row=17, column=0, sticky='w', padx=5, pady=5)

        # Sound Device
        self.sound_enabled_var = tk.BooleanVar(value=True)
        self.sound_checkbox = tk.Checkbutton(self.root, text="Enable Sound Device", variable=self.sound_enabled_var, command=self.toggle_sound_menu)
        self.sound_checkbox.grid(row=18, column=0, sticky='w', padx=5, pady=5)

        self.sound_device = tk.StringVar(value="es1370")
        sound_options = ["ac97", "es1370"]
        self.sound_menu = tk.OptionMenu(self.root, self.sound_device, *sound_options)
        self.sound_menu.grid(row=18, column=1, padx=5, pady=5)
        self.sound_menu.config(state=tk.NORMAL)  # Initially enabled

        # Network Device
        self.network_enabled_var = tk.BooleanVar(value=True)
        self.network_checkbox = tk.Checkbutton(self.root, text="Enable Network Device", variable=self.network_enabled_var, command=self.toggle_network_menu)
        self.network_checkbox.grid(row=19, column=0, sticky='w', padx=5, pady=5)

        self.network_device = tk.StringVar(value="rtl8139")
        network_options = ["rtl8139", "e1000", "e1000e", "i82550", "i82551", "ne2k_pci", "sungem"]
        self.network_menu = tk.OptionMenu(self.root, self.network_device, *network_options)
        self.network_menu.grid(row=19, column=1, padx=5, pady=5)
        self.network_menu.config(state=tk.NORMAL)  # Initially enabled

        # Start QEMU Button
        tk.Button(self.root, text="Start QEMU", command=self.start_qemu).grid(row=20, column=0, columnspan=3, pady=20)

        # Load machine-specific fields
        self.update_machine_specific_fields()

        # Load Graphic device fields
        self.on_graphic_device_change()

    def browse_qemu_exe(self):
        filename = filedialog.askopenfilename(filetypes=[("Executable files", "*.exe")])
        if filename:
            self.qemu_exe.delete(0, tk.END)
            self.qemu_exe.insert(0, filename)

    def browse_bios_pegasos2(self):
        filename = filedialog.askopenfilename(filetypes=[("All files", "*.*"), ("BIOS files", "*.rom;*.bin")])
        if filename:
            self.bios_pegasos2_entry.delete(0, tk.END)
            self.bios_pegasos2_entry.insert(0, filename)

    def browse_bios_amigaone(self):
        filename = filedialog.askopenfilename(filetypes=[("All files", "*.*"), ("BIOS files", "*.rom;*.bin")])
        if filename:
            self.bios_amigaone_entry.delete(0, tk.END)
            self.bios_amigaone_entry.insert(0, filename)

    def browse_iso_file(self):
        filename = filedialog.askopenfilename(filetypes=[("ISO files", "*.iso")])
        if filename:
            self.iso_file.delete(0, tk.END)
            self.iso_file.insert(0, filename)

    def browse_harddisk1(self):
        filename = filedialog.askopenfilename(filetypes=[("Disk files", "*.img;*.qcow2")])
        if filename:
            self.harddisk1.delete(0, tk.END)
            self.harddisk1.insert(0, filename)

    def browse_harddisk2(self):
        filename = filedialog.askopenfilename(filetypes=[("Disk files", "*.img;*.qcow2")])
        if filename:
            self.harddisk2.delete(0, tk.END)
            self.harddisk2.insert(0, filename)

    def update_machine_specific_fields(self, *args):
        selected_machine = self.machine_type.get()
        if selected_machine == "pegasos2":
            self.bios_pegasos2_checkbox.grid(row=2, column=0, sticky='w', padx=5, pady=5)
            self.bios_pegasos2_entry.grid(row=2, column=1, padx=5, pady=5)
            self.kernel_checkbox.grid(row=3, column=0, sticky='w', padx=5, pady=5)
            self.kernel_entry.grid(row=3, column=1, padx=5, pady=5)
            self.initrd_checkbox.grid(row=4, column=0, sticky='w', padx=5, pady=5)
            self.initrd_entry.grid(row=4, column=1, padx=5, pady=5)
            self.bios_pegasos2_browse_button.grid(row=2, column=2, padx=5, pady=5)
        else:
            self.bios_pegasos2_checkbox.grid_remove()
            self.bios_pegasos2_entry.grid_remove()
            self.kernel_checkbox.grid_remove()
            self.kernel_entry.grid_remove()
            self.initrd_checkbox.grid_remove()
            self.initrd_entry.grid_remove()
            self.bios_pegasos2_browse_button.grid_remove()

        if selected_machine == "amigaone":
            self.bios_amigaone_checkbox.grid(row=2, column=0, sticky='w', padx=5, pady=5)
            self.bios_amigaone_entry.grid(row=2, column=1, padx=5, pady=5)
            self.loader1_checkbox.grid(row=5, column=0, sticky='w', padx=5, pady=5)
            self.loader1_entry.grid(row=5, column=1, padx=5, pady=5)
            self.loader2_checkbox.grid(row=6, column=0, sticky='w', padx=5, pady=5)
            self.loader2_entry.grid(row=6, column=1, padx=5, pady=5)
            self.bios_amigaone_browse_button.grid(row=2, column=2, padx=5, pady=5)
        else:
            self.bios_amigaone_checkbox.grid_remove()
            self.bios_amigaone_entry.grid_remove()
            self.loader1_checkbox.grid_remove()
            self.loader1_entry.grid_remove()
            self.loader2_checkbox.grid_remove()
            self.loader2_entry.grid_remove()
            self.bios_amigaone_browse_button.grid_remove()

    def browse_graphic_bios(self):
        filename = filedialog.askopenfilename(filetypes=[("All files", "*.*"), ("BIOS files", "*.rom;*.bin")])
        if filename:
            self.graphic_bios_entry.delete(0, tk.END)
            self.graphic_bios_entry.insert(0, filename)

    def on_graphic_device_change(self, *args):
        selected_graphic_device = self.graphic_device.get()
        if selected_graphic_device == "ati-vga":
            self.graphic_bios_entry.grid(row=15, column=1, padx=5, pady=5)
            self.graphic_bios_checkbox.grid(row=15, column=0, sticky='w', padx=5, pady=5)
            self.graphic_bios_browse_button.grid(row=15, column=2, padx=5, pady=5)
        else:
            self.graphic_bios_entry.grid_remove()
            self.graphic_bios_checkbox.grid_remove()
            self.graphic_bios_browse_button.grid_remove()

    def toggle_cpu_entry(self):
        """Enable or disable the CPU option based on the checkbox."""
        if self.cpu_enabled_var.get():
            self.cpu_menu.config(state=tk.NORMAL)
        else:
            self.cpu_menu.config(state=tk.DISABLED)

    def toggle_vga_menu(self):
        if self.vga_device_enabled_var.get():
            self.vga_menu.config(state=tk.NORMAL)
        else:
            self.vga_menu.config(state=tk.DISABLED)
            self.vga_device.set("none")

    def toggle_graphic_menu(self):
        if self.graphic_device_enabled_var.get():
            self.graphic_menu.config(state=tk.NORMAL)
        else:
            self.graphic_menu.config(state=tk.DISABLED)
            self.graphic_device.set("sm501")

    def toggle_display_menu(self):
        if self.display_enabled_var.get():
            self.display_menu.config(state=tk.NORMAL)
        else:
            self.display_menu.config(state=tk.DISABLED)
            self.display.set("gtk")

    def toggle_sound_menu(self):
        if self.sound_enabled_var.get():
            self.sound_menu.config(state=tk.NORMAL)
        else:
            self.sound_menu.config(state=tk.DISABLED)
            self.sound_device.set("es1370")

    def toggle_network_menu(self):
        if self.network_enabled_var.get():
            self.network_menu.config(state=tk.NORMAL)
        else:
            self.network_menu.config(state=tk.DISABLED)
            self.network_device.set("rtl8139")

    def start_qemu(self):
        command = [self.qemu_exe.get(), "-M", self.machine_type.get()]

        if self.bios_pegasos2_enabled_var.get() and self.bios_pegasos2_entry.get() and self.machine_type.get() == "pegasos2":
            command += ["-bios", self.bios_pegasos2_entry.get()]
            self.update_options_file('bios_pegasos2', self.bios_pegasos2_entry.get())
        if self.kernel_enabled_var.get() and self.kernel_entry.get() and self.machine_type.get() == "pegasos2":
            command += ["-kernel", self.kernel_entry.get()]
            self.update_options_file('kernel', self.kernel_entry.get())
        if self.initrd_enabled_var.get() and self.initrd_entry.get() and self.machine_type.get() == "pegasos2":
            command += ["-initrd", self.initrd_entry.get()]
            self.update_options_file('initrd', self.initrd_entry.get())
        if self.bios_amigaone_enabled_var.get() and self.bios_amigaone_entry.get() and self.machine_type.get() == "amigaone":
            command += ["-bios", self.bios_amigaone_entry.get()]
            self.update_options_file('bios_amigaone', self.bios_amigaone_entry.get())
        if self.loader1_enabled_var.get() and self.loader1_entry.get() and self.machine_type.get() == "amigaone":
            command += ["-device", self.loader1_entry.get()]
            self.update_options_file('loader1', self.loader1_entry.get())
        if self.loader2_enabled_var.get() and self.loader2_entry.get() and self.machine_type.get() == "amigaone":
            command += ["-device", self.loader2_entry.get()]
            self.update_options_file('loader2', self.loader2_entry.get())

        if self.cpu_enabled_var.get() and self.cpu_entry.get():
            command += ["-cpu", self.cpu_entry.get()]
        if self.ram_size.get():
            command += ["-m", self.ram_size.get()]
        if self.iso_file.get():
            command += ["-cdrom", self.iso_file.get()]
        if self.harddisk1.get():
            command += ["-drive", f"file={self.harddisk1.get()},format=raw,index=0,media=disk"]
        if self.harddisk2.get():
            command += ["-drive", f"file={self.harddisk2.get()},format=raw,index=1,media=disk"]

        if self.vga_device_enabled_var.get() and self.vga_device.get():
            command += ["-vga", self.vga_device.get()]

        if self.graphic_device_enabled_var.get():
            selected_graphic_device = self.graphic_device.get()
            if selected_graphic_device == "ati-vga":
                romfile = self.graphic_bios_entry.get()
                command += ["-device", f"ati-vga,guest_hwcursor=true,romfile={romfile}"]
            else:
                command += ["-device", selected_graphic_device]

        if self.display_enabled_var.get() and self.display.get():
            command += ["-display", self.display.get()]
        if self.fullscreen_var.get():
            command.append("-full-screen")
        if self.sound_enabled_var.get() and self.sound_device.get():
            command += ["-device", self.sound_device.get()]
        if self.network_enabled_var.get():
            selected_device = self.network_device.get()
            command += ["-device", f"{selected_device},netdev=net0", "-netdev", "user,id=net0"]

        # Start the QEMU process
        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError as e:
            messagebox.showerror("Error", f"Error starting QEMU: {e}")

        self.save_settings()

    def update_options_file(self, key, value):
        """Update the options file with kernel, loader1, or loader2."""
        if os.path.exists(self.options_file):
            config = configparser.ConfigParser()
            config.read(self.options_file)
        else:
            config = configparser.ConfigParser()
            config['Loaders'] = {}

        config['Loaders'][key] = value
        with open(self.options_file, 'w') as optionsfile:
            config.write(optionsfile)

    def save_settings(self):
        config = configparser.ConfigParser()
        config['Settings'] = {
            'qemu_exe': self.qemu_exe.get(),
            'machine_type': self.machine_type.get(),
            'bios_pegasos2_enabled': str(self.bios_pegasos2_enabled_var.get()),
            'kernel_enabled': str(self.kernel_enabled_var.get()),
            'initrd_enabled': str(self.initrd_enabled_var.get()),
            'bios_amigaone_enabled': str(self.bios_amigaone_enabled_var.get()),
            'loader1_enabled': str(self.loader1_enabled_var.get()),
            'loader2_enabled': str(self.loader2_enabled_var.get()),
            'cpu_enabled': str(self.cpu_enabled_var.get()),
            'cpu': self.cpu_entry.get(),
            'ram_size': self.ram_size.get(),
            'iso_file': self.iso_file.get(),
            'harddisk1': self.harddisk1.get(),
            'harddisk2': self.harddisk2.get(),
            'vga_enabled': str(self.vga_device_enabled_var.get()),
            'vga_device': self.vga_device.get(),
            'graphic_enabled': str(self.graphic_device_enabled_var.get()),
            'bios_graphic_enabled': str(self.graphic_bios_enabled_var.get()),
            'graphic_device': self.graphic_device.get(),
            'display_enabled': str(self.display_enabled_var.get()),
            'display': self.display.get(),
            'fullscreen': str(self.fullscreen_var.get()),
            'sound_enabled': str(self.sound_enabled_var.get()),
            'sound_device': self.sound_device.get(),
            'network_enabled': str(self.network_enabled_var.get()),
            'network_device': self.network_device.get(),
        }
        with open(self.config_file, 'w') as configfile:
            config.write(configfile)

    def load_settings(self):
        if os.path.exists(self.config_file):
            config = configparser.ConfigParser()
            config.read(self.config_file)

            self.qemu_exe.insert(0, config['Settings'].get('qemu_exe', ''))
            self.machine_type.set(config['Settings'].get('machine_type', 'mac99'))
            self.bios_pegasos2_enabled_var.set(config['Settings'].getboolean('bios_pegasos2_enabled', False))
            self.kernel_enabled_var.set(config['Settings'].getboolean('kernel_enabled', False))
            self.initrd_enabled_var.set(config['Settings'].getboolean('initrd_enabled', False))
            self.bios_amigaone_enabled_var.set(config['Settings'].getboolean('bios_amigaone_enabled', False))
            self.loader1_enabled_var.set(config['Settings'].getboolean('loader1_enabled', False))
            self.loader2_enabled_var.set(config['Settings'].getboolean('loader2_enabled', False))
            self.cpu_enabled_var.set(config['Settings'].getboolean('cpu_enabled', False))
            self.cpu_entry.set(config['Settings'].get('cpu', ''))
            self.ram_size.insert(0, config['Settings'].get('ram_size', '512'))
            self.iso_file.insert(0, config['Settings'].get('iso_file', ''))
            self.harddisk1.insert(0, config['Settings'].get('harddisk1', ''))
            self.harddisk2.insert(0, config['Settings'].get('harddisk2', ''))
            self.vga_device_enabled_var.set(config['Settings'].getboolean('vga_enabled', True))
            self.vga_device.set(config['Settings'].get('vga_device', 'none'))
            self.graphic_device_enabled_var.set(config['Settings'].getboolean('graphic_enabled', True))
            self.graphic_bios_enabled_var.set(config['Settings'].getboolean('bios_graphic_enabled', False))
            self.graphic_device.set(config['Settings'].get('graphic_device', 'sm501'))
            self.display_enabled_var.set(config['Settings'].getboolean('display_enabled', True))
            self.display.set(config['Settings'].get('display', 'gtk'))
            self.fullscreen_var.set(config['Settings'].getboolean('fullscreen', False))
            self.sound_enabled_var.set(config['Settings'].getboolean('sound_enabled', True))
            self.sound_device.set(config['Settings'].get('sound_device', 'es1370'))
            self.network_enabled_var.set(config['Settings'].getboolean('network_enabled', True))
            self.network_device.set(config['Settings'].get('network_device', 'rtl8139'))

            # Enable/Disable CPU based on the saved setting
            self.toggle_cpu_entry()

            self.update_machine_specific_fields()

            self.on_graphic_device_change()

if __name__ == "__main__":
    root = tk.Tk()
    app = QEmuPPCGUI(root)
    root.mainloop()
